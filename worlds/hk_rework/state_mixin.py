from collections import Counter
from collections.abc import Generator
from enum import IntEnum
from itertools import chain
from typing import TYPE_CHECKING, Any, ClassVar

from BaseClasses import CollectionState, MultiWorld, Region
from Utils import KeyedDefaultDict
from worlds.AutoWorld import LogicMixin

from .Charms import charm_name_to_id, charm_names
from .constants import BASE_HEALTH, BASE_NOTCHES, BASE_SOUL, SIMPLE_STATE_LOGIC  # noqa: F401
from .data.constants.item_names import LocationNames as ItemNames  # TODO change this when export is fixed
from .Options import HKOptions

if TYPE_CHECKING:
    from . import HKClause


# default_state = KeyedDefaultDict(lambda key: True if key == "NOFLOWER" else False)
class DefaultStateFactory:
    def __call__(self, defaults=None) -> Counter:
        if defaults is None:
            defaults = {}
        ret = Counter({"NOFLOWER": 1, "NOPASSEDCHARMEQUIP": 1})
        for key, value in defaults.items():
            ret[key] = value
        return ret


default_state = DefaultStateFactory()


class HKLogicMixin(LogicMixin):
    multiworld: MultiWorld
    _hk_per_player_resource_states: dict[int, dict[str, list[Counter]]]
    """resource state blob to map regions and their avalible resource states"""
    # state blob is [Counter({"DAMAGE": 0, "SPENTSOUL": 0, "NOFLOWER": 0, "CHARMNOTCHESSPENT": 0})]

    _hk_per_player_sweepable_entrances: dict[int, set[str]]
    """mapping for entrances that need to be statefully swept"""

    _hk_stale: dict[int, bool]
    """TODO: make an item stale and a resource_state_stale difference"""

    _hk_free_entrances: dict[int, set[str]]
    """mapping for entrances that will not alter resource state no matter how many more items we get"""

    _hk_entrance_clause_cache: dict[int, dict[str, dict[int, bool]]]
    """mapping for clauses per entrance per player to short circuit non-resource state calculations"""

    _hk_processed_item_cache: dict[int, Counter]

    hk_charm_costs: dict[int, dict[str, int]]
    """mapping for charm costs per player"""

    def init_mixin(self, multiworld: MultiWorld) -> None:
        from . import HKWorld
        players = multiworld.get_game_players(HKWorld.game)
        if not players:
            return
        self._hk_per_player_resource_states = {
            player: KeyedDefaultDict(lambda region: [default_state()] if region == "Menu" else [])
            for player in players
            }  # {player: {init_state: [start_region]} for player in players}
        self._hk_per_player_sweepable_entrances = {player: set() for player in players}
        self._hk_free_entrances = {player: {"Menu"} for player in players}
        self._hk_entrance_clause_cache = {player: {} for player in players}
        self._hk_stale = dict.fromkeys(players, True)
        self._hk_sweeping = dict.fromkeys(players, False)
        self._hk_processed_item_cache = {player: Counter() for player in players}
        self.hk_charm_costs = HKWorld.charm_names_and_costs
        # for player in players:
        #     self.prog_items[player]["TOTAL_SOUL"] = BASE_SOUL
        #     self.prog_items[player]["TOTAL_HEALTH"] = BASE_HEALTH
        #     self.prog_items[player]["SHADE_HEALTH"] = max(int(BASE_HEALTH/2), 1)
        #     self.prog_items[player]["TOTAL_NOTCHES"] = BASE_NOTCHES

    def copy_mixin(self, other) -> CollectionState:
        from . import HKWorld
        players = self.multiworld.get_game_players(HKWorld.game)
        if not players:
            return other
        other._hk_per_player_resource_states = {player: self._hk_per_player_resource_states[player].copy() for player in players}
        other._hk_free_entrances = {player: self._hk_free_entrances[player].copy() for player in players}
        other._hk_processed_item_cache = {player: self._hk_processed_item_cache[player].copy() for player in players}
        # intentionally setting by reference since it doesn't change after being set
        other.hk_charm_costs = {player: self.hk_charm_costs[player] for player in players}
        return other
        # TODO do we need to copy sweepables? should be empty any time we're mucking with resource state

    if SIMPLE_STATE_LOGIC:
        def _hk_apply_and_validate_state(self, clause: "HKClause", region: Region, target_region=None) -> bool:
            return True
    else:
        def _hk_apply_and_validate_state(self, clause: "HKClause", region: Region, target_region=None) -> bool:
            player = region.player
            # avaliable_states = self._hk_per_player_resource_states[player].get(region.name, None)

            # if avaliable_states is None:
            #     region.can_reach(self)
            #     avaliable_states = self._hk_per_player_resource_states[player].get(region.name, [])

            # unneeded?
            avaliable_states = [s.copy() for s in self._hk_per_player_resource_states[player][region.name]]
            # loses the can_reach parent call, potentially re-add it?

            if not avaliable_states:
                # no valid parent states
                return False

            if target_region:
                persist = True
            else:
                persist = False

            for handler in clause.hk_state_requirements:
                avaliable_states = [s for input_state in avaliable_states for s in handler.modify_state(input_state, self, player)]

            if len(avaliable_states):
                if not persist:
                    return True
                target_states = self._hk_per_player_resource_states[player][target_region.name]
                for index, s in reversed(list(enumerate(avaliable_states))):
                    for previous in target_states:
                        if s == previous or lt(previous, s):
                            # if the state we're adding already exists or a better state already exists, we didn't improve
                            avaliable_states.pop(index)
                            break
                if avaliable_states:
                    target_states += avaliable_states
                    # indicies_to_pop = []
                    # for index, s in enumerate(target_states):
                    #     if any(lt(other, s) for other in target_states):
                    #         indicies_to_pop.append(index)
                    # for index in reversed(indicies_to_pop):
                    #     # reverse so we can blindly pop
                    #     target_states.pop(index)

                    for index, s in reversed(list(enumerate(target_states))):
                        for other in [t_s for t_s in target_states if t_s is not s]:  # TODO make sure this doesn't ever break
                            if lt(other, s):
                                target_states.pop(index)
                                break

                    self._hk_per_player_sweepable_entrances[player].update({exit.name for exit in target_region.exits})
                    # self._hk_stale[player] = True
                assert target_states
                return True
            return False

    def _hk_sweep(self, player: int):
        if self._hk_sweeping[player]:
            return
        self._hk_sweeping[player] = True
        # assume not stale and only evaluate true clauses
        # (region can_reach dependencies will be covered by indirect connections)
        while self._hk_per_player_sweepable_entrances[player]:
            # print(self._hk_per_player_sweepable_entrances[player])
            # random pop but i don't really care
            entrance_name = self._hk_per_player_sweepable_entrances[player].pop()
            entrance = self.multiworld.get_entrance(entrance_name, player)
            if entrance.parent_region in self.reachable_regions[player]:
                # let normal sweep find new regions
                entrance.can_reach(self)
            # if entrance_name not in self._hk_entrance_clause_cache[player]:
            #     entrance.can_reach(self)
            #     # then we haven't done a single can_reach on it, let normal sweep handle that
            #     continue

            # for index in [index for index, status in self._hk_entrance_clause_cache[player][entrance_name].items() if status]:
            #     self._hk_apply_and_validate_state(entrance.hk_rule[index], entrance.parent_region, target_region=entrance.connected_region)
        self._hk_stale[player] = False
        self._hk_sweeping[player] = False


def ge(state1: dict, state2: dict) -> bool:
    return state1.keys() >= state2.keys() and all(v2 <= state1[key] for key, v2 in state2.items())


# from mysteryem
def em_lt(state1: dict, state2: dict) -> bool:
    """Counter-like strict subset comparison"""
    if not state1.keys() <= state2.keys():
        # state1 is not a subset of state2, so state1 has some keys not present in state2
        return False
    if len(state2) > len(state1):
        # state2 has some extra keys, so even if every key in state1 has the same value as in state2, state1 is
        # still a strict subset of state2.
        for key, v1 in state1.items():
            if v1 > state2[key]:
                return False
        return True
    else:  # noqa: RET505
        # state2 has the same keys as state1, so at least one key in state1 must have a lower value than in state2
        less_than = False
        for key, v1 in state1.items():
            v2 = state2[key]
            if v1 > v2:
                # state1 has a larger value than state2 for this key, so state1 is not a subset of state2
                return False
            # todo: How to best optimise this?
            if v1 < v2:
                # state1's value is less than state2's, so state1 could be a strict subset of state2
                less_than = True
        return less_than


def lt(state1: dict, state2: dict) -> bool:
    # TODO rename to le and/or revert this
    for key, v1 in state1.items():
        if not v1 <= state2.get(key, 0):
            return False
    return True

    # if state1 == state2:
    #     breakpoint()
    # if state1.keys() - state2.keys():
    #     # if any keys exist in state1 that aren't present in state2, state1 cannot be less than
    #     return False
    # # if state1["SPENTSOUL"] > state2["SPENTSOUL"]:
    # #     # see if shortcircuting common keys adds speedups
    # #     return False
    # if any(v1 > state2[key] for key, v1 in state1.items()):
    #     return False
    # return True
    # return sum(state1[key] <= state2[key] for key in state1.keys()) == 1 and sum(state1[key] < state2[key] for key in state1.keys()) == 1
    # return not ge(state1, state2)

# negative values won't exist
# best case is falsy
# keys in right that are not in left are inherently lt
# any key in left > right is a failure
# any key in left and not in right is a failure
# don't care about full equality because of codepath


RCStateVariable = object  # for future typing


class ResourceStateHandler(type):
    handlers: ClassVar[list[RCStateVariable]] = []
    _handler_cache: ClassVar[dict[str, RCStateVariable]] = {}

    def __new__(mcs, name, bases, dct):
        new_class = super().__new__(mcs, name, bases, dct)
        ResourceStateHandler.handlers.append(new_class)
        return new_class

    @staticmethod
    def get_handler(req: str) -> RCStateVariable:
        ret = None
        if req in ResourceStateHandler._handler_cache:
            return ResourceStateHandler._handler_cache[req]
        # ret = next(handler(req) for handler in ResourceStateHandler.handlers if handler.try_match(req))
        for handler in ResourceStateHandler.handlers:
            if handler.try_match(req):
                ret = handler(req)
                continue
        assert ret, f"searched for a handler for req {req} and did not find one"
        ResourceStateHandler._handler_cache[req] = ret
        return ret


class RCStateVariable(metaclass=ResourceStateHandler):
    prefix: str

    def __init__(self, term: str):
        assert term.startswith(self.prefix)

        # expecting "prefix" or "prefix[one,two,three]"
        if term != self.prefix:
            params = term[len(self.prefix)+1:-1].split(",")
            self.parse_term(*params)
        else:
            self.parse_term()

    def parse_term(self, *args):
        """Subclasses should use this to expect parameter counts for init"""
        pass

    @classmethod
    def try_match(cls, term: str) -> bool:
        """Returns True if this class can handle the passed in term"""
        return False

    @classmethod
    def get_terms(cls):
        """"""
        return []

    def modify_state(self, state_blob: Counter, item_state: CollectionState, player: int) -> Generator[Counter]:
        # print(self)
        # return (output_state for valid, output_state in [self._modify_state(state_blob, item_state, player)] if valid)
        valid, output_state = self._modify_state(state_blob, item_state, player)
        if valid:
            yield output_state

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int) -> tuple[bool, Counter]:
        pass

    def can_exclude(self, options) -> bool:
        return True

    def add_simple_item_reqs(self, items: Counter) -> None:
        pass


class DirectCompare:
    term: str
    op: str
    value: str  # may be int or bool

    def __init__(self, term: str):
        self.term, self.value = (*term.split(self.op),)

    @classmethod
    def try_match(cls, term: str):
        return cls.op in term

    def can_exclude(self, options: HKOptions):
        return False


class EQVariable(DirectCompare, RCStateVariable):
    term: str
    op: str = "="
    value: str  # may be int or bool

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
        if self.value.isdigit():
            return state_blob[self.term] == int(self.value), state_blob
        else:  # noqa: RET505
            v = self.value == "TRUE"
            assert v or self.value == "FALSE"
            return state_blob[self.term] == v, state_blob


class GTVariable(DirectCompare, RCStateVariable):
    term: str
    op: str = ">"
    value: str

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
        assert self.value.isdigit()
        return state_blob[self.term] > int(self.value), state_blob


class LTVariable(DirectCompare, RCStateVariable):
    term: str
    op: str = "<"
    value: str

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
        assert self.value.isdigit()
        return state_blob[self.term] < int(self.value), state_blob


class RCResetter:
    reset_state: ClassVar[dict[str, Any]]
    """Target state to reset to"""
    opt_in: bool = False
    """Flag to determine if unhandled terms are reset"""
    reset_properties: ClassVar[dict[str, str]]  # TODO - flesh this out
    """
    Dict of requirement: terms to reset,
    use ANY for terms that can be reset with no requirment
    use NONE for terms that will never be reset even with opt_in False
    """

    def parse_term(self):
        pass

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int) -> tuple[bool, Counter]:
        # TODO: confirm this is always correct, and deletion isn't too big an assumption
        if self.opt_in:
            for key, value in self.reset_properties.items():
                if value != "None":
                    # if the reset logic evaluates to True, update to new value
                    if key not in self.reset_state:
                        if key in state_blob:
                            del state_blob[key]
                    else:
                        state_blob[key] = self.reset_state[key]
            return True, state_blob
        else:  # noqa: RET505
            ret = default_state(defaults=self.reset_state)
            for key, value in self.reset_properties.items():
                if value == "None":  # TODO: fix
                    # if the reset logic evaluates to False keep old value
                    ret[key] = state_blob[key]
            return True, ret

    @classmethod
    def try_match(cls, term: str) -> bool:
        return term.startswith(cls.prefix)

    def can_exclude(self, options: HKOptions) -> bool:
        return False


class BenchResetVariable(RCResetter, RCStateVariable):
    prefix: str = "$BENCHRESET"
    reset_state: ClassVar[dict[str, str]] = {
        "NOPASSEDCHARMEQUIP": False
    }
    opt_in = False
    reset_properties: ClassVar[dict[str, str]] = {
        "CANNOTREGAINSOUL": "NONE",
        "CANNOTSHADESKIP": "NONE",
        "BROKEHEART": "NONE",
        "BROKEGREED": "NONE",
        "BROKESTRENGTH": "NONE",
        "NOFLOWER": "NONE",
        "SOULLIMITER": "NONE",
        "REQUIREDMAXSOUL": "NONE",

        "SPENTALLSOUL": "Salubra's_Blessing + CANNOTREGAINSOUL=FALSE",
        "SPENTSOUL": "Salubra's_Blessing + CANNOTREGAINSOUL=FALSE",
        "SPENTRESERVESOUL": "Salubra's_Blessing + CANNOTREGAINSOUL=FALSE",
    }
    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))


class HotSpringResetVariable(RCResetter, RCStateVariable):
    prefix = "$HOTSPRINGRESET"

    reset_state: ClassVar[dict[str, Any]] = {}
    opt_in = True
    reset_properties: ClassVar[dict[str, str]] = {
        "SPENTALLSOUL": "CANNOTREGAINSOUL=FALSE",
        "SPENTSOUL": "CANNOTREGAINSOUL=FALSE",
        "SPENTRESERVESOUL": "CANNOTREGAINSOUL=FALSE",
        "SPENTHP": "ANY",
    }
    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))


class SaveQuitResetVariable(RCResetter, RCStateVariable):
    prefix = "$SAVEQUITRESET"

    reset_state: ClassVar[dict[str, Any]] = {
        "SPENTALLSOUL": True
    }
    opt_in = True
    reset_properties: ClassVar[dict[str, str]] = {
        "SPENTALLSOUL": "CANNOTREGAINSOUL=FALSE",
    }

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))


class StartRespawnResetVariable(RCResetter, RCStateVariable):
    prefix = "$STARTRESPAWN"
    reset_state: ClassVar[dict[str, Any]] = {}
    opt_in = True
    reset_properties: ClassVar[dict[str, str]] = {
        "SPENTALLSOUL": "CANNOTREGAINSOUL=FALSE",
        "SPENTSOUL": "CANNOTREGAINSOUL=FALSE",
        "SPENTRESERVESOUL": "CANNOTREGAINSOUL=FALSE",
        "SPENTHP": "ANY",
    }

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))


class CastSpellVariable(RCStateVariable):
    prefix: str = "$CASTSPELL"
    casts: list[int]
    before: str | None
    after: str | None
    equip_st: "EquipCharmVariable"

    def __init__(self, *args):
        super().__init__(*args)
        self.equip_st = EquipCharmVariable("$EQUIPPEDCHARM[Spell_Twister]")

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

    def modify_state(self, state_blob: Counter, item_state: CollectionState, player: int) -> Generator[Counter]:
        max_soul = self.get_max_soul(state_blob)
        if not state_blob["CANNOTREGAINSOUL"] and self.before:
            soul = self.get_max_soul(state_blob)
            reserves = self.get_reserves(state_blob, item_state, player)
        elif state_blob["SPENTALLSOUL"]:
            soul = 0
            reserves = 0
        else:
            soul = self.get_soul(state_blob)
            reserves = self.get_reserves(state_blob, item_state, player)

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
                and self.equip_st.can_equip(state_st, item_state, player)):
            check, state_st = self.equip_st._modify_state(state_st, item_state, player)  # we know EquipCharmVariable only yields once
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

    @classmethod
    def get_max_reserves(cls, state_blob: Counter, item_state: CollectionState, player) -> int:
        return (item_state.count("VesselFragment", player) // 3) * 33

    @classmethod
    def get_reserves(cls, state_blob: Counter, item_state: CollectionState, player: int) -> int:
        return cls.get_max_reserves(state_blob, item_state, player) - state_blob["SPENTRESERVESOUL"]


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
            self.stall_cast = CastSpellVariable(f"{CastSpellVariable.prefix}[{','.join(sub_params)}]")
        else:
            self.stall_cast = None

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def modify_state(self, state_blob, item_state, player):
        if not item_state.has_all_counts({"SCREAM": 2, "WINGS": 1}, player):
            return False, state_blob
        elif self.stall_cast and ((not self.no_left_stall and item_state["LEFTDASH"])  # noqa: RET505
                                  (not self.no_right_stall and item_state["RIGHTDASH"])):
            return self.stall_cast.modify_state(state_blob, item_state, player)
        else:
            return super().modify_state(state_blob, item_state, player)

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

    def _modify_state(self, state_blob, item_state, player):
        if not item_state.has("FIREBALL", player):
            return False, state_blob
        else:  # noqa: RET505
            return super()._modify_state(state_blob, item_state, player)

    def can_exclude(self, options):
        return True
        # TODO add the option lol
        # return bool(options.SlopeBallSkips)

    def add_simple_item_reqs(self, items: Counter) -> None:
        items["FIREBALL"] = items.get("FIREBALL", 1)


class EquipCharmVariable(RCStateVariable):
    prefix: str = "$EQUIPPEDCHARM"
    equip_prefix: str = "CHARM"
    no_equip_prefix: str = "noCHARM"
    excluded_charm_ids: tuple[int] = (23, 24, 25, 36,)  # fragiles and Kingsoul
    charm_id: int
    charm_name: str
    charm_key: str

    class EquipResult(IntEnum):
        NONE = 1
        OVERCHARM = 2
        NONOVERCHARM = 3

    # maybe remove this later if it ends up not being useful compared to charm_id_and_name
    @staticmethod
    def get_name(charm: str) -> str:
        """Convert charm id to name, or just return the name"""
        if charm.isdigit():
            return charm_names[int(charm) - 1]
        else:  # noqa: RET505
            return charm

    @staticmethod
    def get_id(charm: str) -> int:
        """Convert charm name to id, or just return the id"""
        if charm.isdigit():
            return int(charm)
        else:  # noqa: RET505
            return charm_name_to_id[charm] + 1

    @staticmethod
    def charm_id_and_name(charm: str) -> tuple[int, str]:
        """Convert 1 indexed charm id or charm name to both"""
        if charm.isdigit():
            return int(charm), charm_names[int(charm) - 1]
        else:  # noqa: RET505
            return charm_name_to_id[charm] + 1, charm

    def parse_term(self, term: str) -> None:
        self.charm_id, self.charm_name = self.charm_id_and_name(term)
        self.charm_key = f"CHARM{self.charm_id}"

    @classmethod
    def try_match(cls, term: str) -> bool:
        if term.startswith(cls.prefix):
            # strip the $EQUIPPEDCHARM[] from the term and extract the 1 indexed charm id
            charm_id = cls.get_id(term[len(cls.prefix)+1:-1])
            # covered by other handlers
            if charm_id not in cls.excluded_charm_ids:
                return True
        # else
        return False

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def has_item(self, item_state: CollectionState, player: int) -> bool:
        return item_state.has(self.charm_key, player)
        # return bool(item_state._hk_processed_item_cache[player][self.charm_name])

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int) -> tuple[bool, Counter]:
        return self.try_equip(state_blob, item_state, player), state_blob

    def try_equip(self, state_blob: Counter, item_state: CollectionState, player: int) -> bool:
        if self.charm_key in state_blob:
            return True
        if f"no{self.charm_key}" in state_blob:
            return False
        if not self.has_item(item_state, player):
            return False
        if self.can_equip(state_blob, item_state, player):
            self.do_equip_charm(state_blob, item_state, player)
            return True
        return False

    @property
    def anti_term(self) -> str:
        return f"{self.no_equip_prefix}{self.charm_id}"

    @property
    def term(self) -> str:
        return f"{self.equip_prefix}{self.charm_id}"

    def has_state_requirements(self, state_blob: Counter) -> bool:
        if state_blob["NOPASSEDCHARMEQUIP"] or state_blob[self.anti_term]:
            return False
        return True

    @staticmethod
    def get_total_notches(item_state: CollectionState, player: int) -> int:
        collected_notches = item_state.count(ItemNames.CHARM_NOTCH, player)
        return BASE_NOTCHES + collected_notches

    def get_notch_cost(self, item_state: CollectionState, player: int) -> int:
        return item_state.hk_charm_costs[player][self.charm_name]

    def has_notch_requirments(self, state_blob: Counter, item_state: CollectionState, player: int) -> EquipResult:
        notch_cost = self.get_notch_cost(item_state, player)
        if notch_cost <= 0 or self.is_equipped(state_blob):
            return self.EquipResult.OVERCHARM if state_blob["OVERCHARMED"] else self.EquipResult.NONOVERCHARM
        # can be equipped
        net_notches = self.get_total_notches(item_state, player) - state_blob["USEDNOTCHES"] - notch_cost
        if net_notches >= 0:
            return self.EquipResult.NONOVERCHARM
        # something to figure out if you can overcharm to get this on
        overcharm_save = max(notch_cost, state_blob["MAXNOTCHCOST"])
        if net_notches + overcharm_save > 0 and not state_blob["CANNOTOVERCHARM"]:
            return self.EquipResult.OVERCHARM
        return self.EquipResult.NONE  # TODO doublecheck

    def can_equip_non_overcharm(self, state_blob: Counter, item_state: CollectionState, player) -> bool:
        return (self.has_item(item_state, player) and self.has_state_requirements(state_blob)
                and self.has_notch_requirments(state_blob, item_state, player) == self.EquipResult.NONOVERCHARM)

    def can_equip_overcharm(self, state_blob: Counter, item_state: CollectionState, player: int) -> bool:
        return (self.has_item(item_state, player) and self.has_state_requirements(state_blob)
                and self.has_notch_requirments(state_blob, item_state, player) != self.EquipResult.NONE)

    def can_equip(self, state_blob: Counter, item_state: CollectionState, player: int) -> EquipResult:
        if not self.has_item(item_state, player):
            return self.EquipResult.NONE

        overcharm = False
        for _ in (None,):  # there's an iteration in upstream I don't want to lose sight of
            if self.has_state_requirements(state_blob):
                ret = self.has_notch_requirments(state_blob, item_state, player)
                if ret == self.EquipResult.NONE:
                    continue
                elif ret == self.EquipResult.OVERCHARM:  # noqa: RET507
                    overcharm = True
                elif ret == self.EquipResult.NONOVERCHARM:
                    return ret
        return self.EquipResult.OVERCHARM if overcharm else self.EquipResult.NONE

    def do_equip_charm(self, state_blob: Counter, item_state: CollectionState, player: int) -> None:
        notch_cost = self.get_notch_cost(item_state, player)
        state_blob["USEDNOTCHES"] += notch_cost
        # one of these 2 should probably go at some point
        state_blob[self.term] = True
        state_blob[self.charm_key] = True
        state_blob["MAXNOTCHCOST"] = min(state_blob["MAXNOTCHCOST"], notch_cost)
        if state_blob["USEDNOTCHES"] > state_blob["NOTCHES"]:
            state_blob["OVERCHARMED"] = True

    def is_equipped(self, state_blob: Counter) -> bool:
        return bool(state_blob[self.term])

    def set_unequippable(self, state_blob: Counter) -> None:
        state_blob[self.anti_term] = True

    @staticmethod
    def get_avaliable_notches(state_blob: Counter) -> int:
        return state_blob["NOTCHES"] - state_blob["USEDNOTCHES"]

    def can_exclude(self, options: HKOptions) -> bool:
        return False

    def add_simple_item_reqs(self, items: Counter) -> None:
        items[self.charm_key] = 1


class FragileCharmVariable(EquipCharmVariable):
    # prefix = "$EQUIPPEDCHARM"
    fragile_lookup: ClassVar[dict[int, list[str]]] = {
        23: ["Fragile_Heart", "Unbreakable_Heart"],
        24: ["Fragile_Greed", "Unbreakable_Greed"],
        25: ["Fragile_Strength", "Unbreakable_Strength"],
    }
    # todo: break_bool matters when dealing with Shade Skips
    break_bool: bool
    # todo: determine logic for repair term. Probably access to Leggy and some sort of money logic to repair?
    repair_term: bool

    def parse_term(self, term: str) -> None:
        super().parse_term(term)
        self.break_bool = False
        self.repair_term = True  # make false later after figuring out how to slot in leggy access

    # todo: break_bool matters when dealing with Shade Skips
    def break_charm(self, state_blob: Counter, item_state: CollectionState, player: int) -> None:
        if state_blob[self.charm_key] >= 2:
            return

    def has_state_requirements(self, state_blob: Counter) -> bool:
        return (super().has_state_requirements(state_blob)
                and ((state_blob[self.charm_key] >= 2)
                     or (not self.break_bool and self.repair_term)))

    @classmethod
    def try_match(cls, term: str) -> bool:
        if term.startswith(cls.prefix):
            charm_id, _ = cls.charm_id_and_name(term[len(cls.prefix)+1:-1])
            if charm_id in cls.fragile_lookup:
                return True
        # else
        return False

    def add_simple_item_reqs(self, items: Counter) -> None:
        super().add_simple_item_reqs(items)
        items["Can_Repair_Fragile_Charms"] = 1


class WhiteFragmentEquipVariable(EquipCharmVariable):
    # prefix = "$EQUIPPEDCHARM"
    void: bool
    quantity: int

    def parse_term(self, charm: str) -> None:
        super().parse_term(charm)
        self.void = self.charm_name == "Void_Heart"
        assert not self.void == (self.charm_name == "Kingsoul")
        if self.charm_name == "Kingsoul":
            self.quantity = 2
        if self.charm_name == "Void_Heart":
            self.quantity = 3

    @classmethod
    def try_match(cls, term: str) -> bool:
        if term.startswith(cls.prefix):
            charm_id, _ = cls.charm_id_and_name(term[len(cls.prefix)+1:-1])
            if charm_id == 36:
                return True
        # else
        return False

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def has_item(self, item_state: CollectionState, player: int) -> bool:
        if self.void:
            count = 3
        else:
            count = 2
        return item_state.has(self.charm_key, player, count)

    # TODO double check this is not necessary with has_item defined
    # def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
    #     # TODO figure this out
    #     # TODO actually
    #     print(self.void)
    #     return super()._modify_state(state_blob, item_state, player)

    def add_simple_item_reqs(self, items: Counter) -> None:
        if self.void:
            count = 3
        else:
            count = 2
        if items[self.charm_key] < count:
            items[self.charm_key] = count


class FlowerProviderVariable(RCStateVariable):
    prefix: str = "$FLOWERGET"

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int) -> tuple[bool, Counter]:
        state_blob["NOFLOWER"] = False
        return True, state_blob

    @classmethod
    def try_match(cls, term: str) -> bool:
        return term == cls.prefix

    def can_exclude(self, options: HKOptions) -> bool:
        return False


class RegainSoulVariable(RCStateVariable):
    prefix: str = "$REGAINSOUL"
    amount: int

    def parse_term(self, amount: str) -> None:
        self.amount = int(amount)

    @classmethod
    def try_match(cls, term: str) -> bool:
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int) -> tuple[bool, Counter]:
        if state_blob["CANNOTREGAINSOUL"]:
            return False, state_blob
        if state_blob["SPENTALLSOUL"]:
            state_blob["SPENTRESERVESOUL"] = self.get_max_reserve_soul(item_state, player)
            state_blob["SPENTSOUL"] = self.get_max_soul(state_blob)
            state_blob["SPENTALLSOUL"] = False
        soul_diff = self.get_max_soul(state_blob) - state_blob["SPENTSOUL"]  # i simplified this
        if self.amount < soul_diff:
            state_blob["SPENTSOUL"] -= self.amount
        else:
            state_blob["SPENTSOUL"] = 0
            amount = self.amount - soul_diff
            reserve_diff = (self.get_max_reserve_soul(item_state, player) - state_blob["SPENTRESERVESOUL"])  # i simplified this
            if amount < reserve_diff:
                state_blob["SPENTRESERVESOUL"] -= amount
            else:
                state_blob["SPENTRESERVESOUL"] = 0
        return True, state_blob

    def get_max_reserve_soul(self, item_state: CollectionState, player: int) -> int:
        return (item_state.count("VesselFragment", player) // 3) * 33

    def get_max_soul(self, state_blob: Counter) -> int:
        return 99 - state_blob["SOULLIMITER"]

    def can_exclude(self, options: HKOptions) -> bool:
        return False


class ShadeStateVariable(RCStateVariable):
    prefix: str = "$SHADESKIP"
    health: int

    def parse_term(self, *args) -> None:
        if len(args) == 1:
            hits = args[0]
            self.health = hits[:-4]
        elif len(args) == 0:
            self.health = 1
        else:
            raise Exception(f"unknown {self.prefix} term, args: {args}")

    @classmethod
    def try_match(cls, term: str) -> bool:
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int) -> tuple[bool, Counter]:
        # TODO fill out when i finish equipped item variable
        if state_blob["SpentShade"]:
            return False, state_blob
        else:  # noqa: RET505
            state_blob["SpentShade"] = True
            return True, state_blob

    def can_exclude(self, options: HKOptions) -> bool:
        return not bool(options.ShadeSkips)


class SpendSoulVariable(RCStateVariable):
    prefix = "$SPENDSOUL"
    amount: int

    def parse_term(self, amount):
        self.amount = amount

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
        if state_blob["SPENTALLSOUL"]:
            return False, state_blob

        soul = self.get_soul(state_blob)
        if soul < self.amount:
            return False, state_blob

        reserve_soul = self.get_reserve_soul(state_blob, item_state, player)
        if reserve_soul >= self.amount:
            state_blob["SPENTRESERVESOUL"] += self.amount
        else:
            state_blob["SPENTRESERVESOUL"] += reserve_soul
            state_blob["SPENTSOUL"] += self.amount - reserve_soul

        required_max_soul = state_blob["REQUIREDMAXSOUL"]
        alt_req = max(self.amount, state_blob["SPENTSOUL"])
        if alt_req > required_max_soul:
            state_blob["REQUIREDMAXSOUL"] = alt_req

        return True, state_blob

    def get_soul(self, state_blob):
        return 99 - state_blob["SOULLIMITER"] - state_blob["SPENTSOUL"]

    def get_reserve_soul(self, state_blob: Counter, item_state: CollectionState, player: int):
        return ((item_state.count("VesselFragment", player) // 3) * 33) - state_blob["SPENTRESERVESOUL"]

    def can_exclude(self, options):
        return False


class StagStateVariable(RCStateVariable):
    prefix = "$STAGSTATEMODIFIER"

    def parse_term(self):
        pass

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
        state_blob["NOFLOWER"] = 1
        return True, state_blob

    def can_exclude(self, options):
        return False


# TODO - i don't know what this is for; says it's for handling subhandlers but not sure when
# class StateModifierWrapper(RCStateVariable):
#     prefix = "$BENCHRESET"

#     def parse_term(self):
#         pass

#     @classmethod
#     def try_match(cls, term: str):
#         return term.startswith(cls.prefix)

#     # @classmethod
#     # def get_terms(cls):
#     #     return (term for term in ("VessleFragments",))

#     def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
#         pass

#     def can_exclude(self, options):
#         return False


class TakeDamageVariable(RCStateVariable):
    prefix = "$TAKEDAMAGE"
    damage: int

    def parse_term(self, damage=1):
        self.damage = int(damage)
        pass

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
        # TODO figure this out
        if self.damage + state_blob["DAMAGE"] >= BASE_HEALTH:
            return False, state_blob
        else:  # noqa: RET505
            state_blob["DAMAGE"] += self.damage
            return True, state_blob

    def can_exclude(self, options):
        # can not actually be excluded because the damage skip option is checked in logic seperately
        return False


class LifebloodCountVariable(RCStateVariable):
    prefix = "$LIFEBLOOD"
    required_blue_masks: int
    hp_manager: TakeDamageVariable
    joni_manager: EquipCharmVariable

    def parse_term(self, required_blue_masks=1):
        self.required_blue_masks = required_blue_masks
        self.hp_manager = TakeDamageVariable(TakeDamageVariable.prefix)
        self.joni_manager = EquipCharmVariable(f"{EquipCharmVariable.prefix}[Joni's_Blessing]")
        # set hp state manager and joni's equip charm variable

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
        valid, state_blob = self.hp_manager._modify_state(state_blob, item_state, player)
        if valid:
            return self.joni_manager._modify_state(state_blob, item_state, player)
        else:  # noqa: RET505
            return False, state_blob

    def can_exclude(self, options):
        return False


class WarpToBenchResetVariable(RCStateVariable):
    prefix = "$WARPTOBENCH"
    sq_reset: SaveQuitResetVariable
    bench_reset: BenchResetVariable

    def parse_term(self):
        self.sq_reset = SaveQuitResetVariable(SaveQuitResetVariable.prefix)
        self.bench_reset = BenchResetVariable(BenchResetVariable.prefix)

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
        valid, state_blob = self.sq_reset._modify_state(state_blob, item_state, player)
        if valid:
            return self.bench_reset._modify_state(state_blob, item_state, player)
        else:  # noqa: RET505
            return False, state_blob

    def can_exclude(self, options):
        return False


class WarpToStartResetVariable(RCStateVariable):
    prefix = "$WARPTOSTART"
    sq_reset: SaveQuitResetVariable
    start_reset: StartRespawnResetVariable

    def parse_term(self):
        self.sq_reset = SaveQuitResetVariable(SaveQuitResetVariable.prefix)
        self.start_reset = StartRespawnResetVariable(StartRespawnResetVariable.prefix)

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
        valid, state_blob = self.sq_reset._modify_state(state_blob, item_state, player)
        if valid:
            return self.start_reset._modify_state(state_blob, item_state, player)
        else:  # noqa: RET505
            return False, state_blob

    def can_exclude(self, options):
        return False
