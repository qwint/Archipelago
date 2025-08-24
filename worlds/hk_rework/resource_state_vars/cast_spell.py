from collections import Counter
from collections.abc import Generator
from itertools import chain

from BaseClasses import CollectionState

from . import RCStateVariable
from .equip_charm import EquipCharmVariable
from ..Options import HKOptions


class CastSpellVariable(RCStateVariable):
    prefix: str = "$CASTSPELL"
    casts: list[int]
    before: str | None
    after: str | None
    equip_st: "EquipCharmVariable"

    def __init__(self, *args):
        super().__init__(*args)
        self.equip_st = EquipCharmVariable("$EQUIPPEDCHARM[Spell_Twister]", self.player)

    def parse_term(self, *args) -> None:
        self.casts = []
        self.before = None
        self.after = None
        self.no_left_stall = False
        self.no_right_stall = False
        for arg in args:
            if arg.isdigit():
                self.casts.append(int(arg))
            elif arg.startswith("before"):
                self.before = arg[7:]
            elif arg.startswith("after"):
                self.after = arg[6:]
            elif arg == "noDG":
                raise Exception("no dreamgate is currently not implemented")
                # self.can_dreamgate = False
            elif arg == "NOLEFTSTALL":
                self.no_left_stall = True
            elif arg == "NORIGHTSTALL":
                self.no_right_stall = True
            elif arg == "NOSTALL":
                self.no_left_stall = True
                self.no_right_stall = True
            else:
                raise Exception(f"unknown {self.prefix} term, args: {args}")
        if len(self.casts) == 0:
            self.casts.append(1)

    @classmethod
    def try_match(cls, term: str) -> bool:
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def modify_state(self, state_blob: Counter, item_state: CollectionState) -> Generator[Counter]:
        max_soul = self.get_max_soul(state_blob)
        if not state_blob["CANNOTREGAINSOUL"] and self.before:
            soul = self.get_max_soul(state_blob)
            reserves = self.get_reserves(state_blob, item_state)
        elif state_blob["SPENTALLSOUL"]:
            soul = 0
            reserves = 0
        else:
            soul = self.get_soul(state_blob)
            reserves = self.get_reserves(state_blob, item_state)

        # try without spell twister
        if (not self.equip_st.is_equipped(state_blob)
                and self.try_cast_all(33, max_soul, reserves, soul)):
            state33 = state_blob.copy()
            # setUnequippable(state33, spelltwister)
            self.do_all_casts(33, reserves, state33)
            if not state33["CANNOTREGAINSOUL"] and self.after:
                self.recover_soul(sum(self.casts) * 33, state33)
            yield state33

        # try with spell twister
        state_st = state_blob.copy()
        if (self.try_cast_all(24, max_soul, reserves, soul)
                and self.equip_st.can_equip(state_st, item_state)):
            check, state_st = self.equip_st._modify_state(state_st, item_state)
            # we know EquipCharmVariable only yields once
            if check:
                self.do_all_casts(24, reserves, state_st)
                if not state_st["CANNOTREGAINSOUL"] and self.after:
                    self.recover_soul(sum(self.casts) * 33, state_st)
                yield state_st

    def can_exclude(self, options: HKOptions) -> bool:
        return False

    def do_all_casts(self, cost_per_cast: int, reserves: int, state_blob: Counter) -> None:
        for cast in self.casts:
            reserves = self.spend_soul(cost_per_cast * cast, reserves, state_blob)

    @classmethod
    def spend_soul(cls, amount: int, reserve: int, state_blob: Counter) -> int:
        if reserve >= amount:
            state_blob["SPENTRESERVESOUL"] += amount
            reserve -= amount
        elif reserve > 0:
            state_blob["SPENTRESERVESOUL"] += reserve
            state_blob["SPENTSOUL"] += amount - reserve
            reserve = 0
        else:
            state_blob["SPENTSOUL"] += amount

        if amount > state_blob["MAXREQUIREDSOUL"]:
            state_blob["MAXREQUIREDSOUL"] = amount

        return reserve

    @classmethod
    def try_spend_soul(cls, amount: int, max_soul: int, reserves: int, soul: int, valid: bool) -> tuple[int, int, bool]:
        if not valid:
            return (reserves, soul, valid)
        if soul < amount:
            return (reserves, soul, False)

        transfer_amt = min(reserves, max_soul - soul)
        soul += transfer_amt
        reserves -= transfer_amt
        return (reserves, soul, True)

    def try_cast_all(self, cost_per_cast: int, max_soul: int, reserves: int, soul: int) -> bool:
        ret = True
        for cast in self.casts:
            reserves, soul, ret = self.try_spend_soul(cost_per_cast * cast, max_soul, reserves, soul, ret)
        return ret

    @classmethod
    def recover_soul(cls, amount: int, state_blob: Counter) -> None:
        soul_diff = state_blob["SPENTSOUL"]
        if soul_diff >= amount:
            state_blob["SPENTSOUL"] -= amount
        elif soul_diff < amount:
            state_blob["SPENTSOUL"] = 0
            amount -= soul_diff
        reserve_diff = state_blob["SPENTRESERVESOUL"]
        if reserve_diff >= amount:
            state_blob["SPENTRESERVESOUL"] -= amount
        elif reserve_diff > 0:
            state_blob["SPENTRESERVESOUL"] = 0
            amount -= reserve_diff

    @classmethod
    def get_max_soul(cls, state_blob: Counter) -> int:
        return 99 - state_blob["SOULLIMITER"]

    @classmethod
    def get_soul(cls, state_blob: Counter) -> int:
        return cls.get_max_soul(state_blob) - state_blob["SPENTSOUL"]

    def get_max_reserves(self, state_blob: Counter, item_state: CollectionState) -> int:
        return (item_state.count("VesselFragment", self.player) // 3) * 33

    def get_reserves(self, state_blob: Counter, item_state: CollectionState) -> int:
        return self.get_max_reserves(state_blob, item_state) - state_blob["SPENTRESERVESOUL"]


class ShriekPogoVariable(CastSpellVariable):
    prefix = "$SHRIEKPOGO"
    stall_cast: CastSpellVariable | None

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    def parse_term(self, *args):
        super().parse_term(*args)
        if any(cast > 1 for cast in self.casts) and (not self.no_left_stall or not self.no_right_stall):
            sub_params = list(chain.from_iterable([["1"] * int(i) if i.isdigit() else [i] for i in args]))
            # flatten any > 1 cast value into that many copies of 1
            # to tell downstream that there can be a break to regain soul
            self.stall_cast = CastSpellVariable(f"{CastSpellVariable.prefix}[{','.join(sub_params)}]", self.player)
        else:
            self.stall_cast = None

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob, item_state):
        if not item_state.has_all_counts({"SCREAM": 2, "WINGS": 1}, self.player):
            return False, state_blob
        elif self.stall_cast and ((not self.no_left_stall and item_state.has("LEFTDASH", self.player))  # noqa: RET505
                                  (not self.no_right_stall and item_state.has("RIGHTDASH", self.player))):
            return self.stall_cast._modify_state(state_blob, item_state)
        else:
            return super()._modify_state(state_blob, item_state)

    def can_exclude(self, options):
        return True
        # TODO add the option lol
        # on = bool(options.ShriekPogoSkips)
        # difficult = sum(self.casts) > 3
        # difficult_on = bool(options.DifficultSkips)
        # return (not on) or (difficult and not difficult_on)

    def add_simple_item_reqs(self, items: Counter) -> None:
        items["SCREAM"] = 2
        items["WINGS"] = 1


class SlopeballVariable(CastSpellVariable):
    prefix = "$SLOPEBALL"

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob, item_state):
        if not item_state.has("FIREBALL", self.player):
            return False, state_blob
        else:  # noqa: RET505
            return super()._modify_state(state_blob, item_state)

    def can_exclude(self, options):
        return True
        # TODO add the option lol
        # return bool(options.SlopeBallSkips)

    def add_simple_item_reqs(self, items: Counter) -> None:
        items["FIREBALL"] = items.get("FIREBALL", 1)
