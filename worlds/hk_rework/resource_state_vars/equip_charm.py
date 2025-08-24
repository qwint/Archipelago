from collections import Counter
from enum import IntEnum
from typing import ClassVar, Iterable

from BaseClasses import CollectionState

from . import RCStateVariable
from ..Charms import charm_name_to_id, charm_names
from ..constants import BASE_NOTCHES
from ..data.constants.item_names import ItemNames
from ..Options import HKOptions


class EquipResult(IntEnum):
    NONE = 1
    OVERCHARM = 2
    NONOVERCHARM = 3


class EquipCharmVariable(RCStateVariable):
    prefix: str = "$EQUIPPEDCHARM"
    equip_prefix: str = "CHARM"
    no_equip_prefix: str = "noCHARM"
    excluded_charm_ids: tuple[int] = (23, 24, 25, 36,)  # fragiles and Kingsoul
    charm_id: int
    charm_name: str
    charm_key: str

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

    def has_item(self, item_state: CollectionState) -> bool:
        return item_state.has(self.charm_name, self.player)
        # return bool(item_state._hk_processed_item_cache[self.player][self.charm_name])

    def _modify_state(self, state_blob: Counter, item_state: CollectionState) -> tuple[bool, Counter]:
        return self.try_equip(state_blob, item_state), state_blob

    def _try_equip(self, state_blob: Counter, item_state: CollectionState) -> tuple[bool, Counter]:
        if self.is_equipped(state_blob):
            return True, state_blob
        if self.can_equip(state_blob, item_state) != EquipResult.NONE:
            ret = state_blob.copy()
            self.do_equip_charm(ret, item_state)
            return True, ret
        return False, state_blob

    def try_equip(self, state_blob: Counter, item_state: CollectionState) -> bool:
        if self.is_equipped(state_blob):
            return True
        if self.can_equip(state_blob, item_state) != EquipResult.NONE:
            self.do_equip_charm(state_blob, item_state)
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

    def get_total_notches(self, item_state: CollectionState) -> int:
        return item_state.count("NOTCHES", self.player)
        # collected_notches = item_state.count(ItemNames.CHARM_NOTCH, self.player)
        # return BASE_NOTCHES + collected_notches

    def get_notch_cost(self, item_state: CollectionState) -> int:
        return item_state.hk_charm_costs[self.player][self.charm_name]

    def has_notch_requirments(self, state_blob: Counter, item_state: CollectionState) -> EquipResult:
        notch_cost = self.get_notch_cost(item_state)
        if notch_cost <= 0 or self.is_equipped(state_blob):
            return EquipResult.OVERCHARM if state_blob["OVERCHARMED"] else EquipResult.NONOVERCHARM
        # can be equipped
        net_notches = self.get_total_notches(item_state) - state_blob["USEDNOTCHES"] - notch_cost
        if net_notches >= 0:
            return EquipResult.NONOVERCHARM
        # something to figure out if you can overcharm to get this on
        overcharm_save = max(notch_cost, state_blob["MAXNOTCHCOST"])
        if net_notches + overcharm_save > 0 and not state_blob["CANNOTOVERCHARM"]:
            return EquipResult.OVERCHARM
        return EquipResult.NONE  # TODO doublecheck

    def can_equip_non_overcharm(self, state_blob: Counter, item_state: CollectionState) -> bool:
        return (self.has_item(item_state) and self.has_state_requirements(state_blob)
                and self.has_notch_requirments(state_blob, item_state) == EquipResult.NONOVERCHARM)

    def can_equip_overcharm(self, state_blob: Counter, item_state: CollectionState) -> bool:
        return (self.has_item(item_state) and self.has_state_requirements(state_blob)
                and self.has_notch_requirments(state_blob, item_state) != EquipResult.NONE)

    def can_equip(self, state_blob: Counter, item_state: CollectionState) -> EquipResult:
        if not self.has_charm_progression(item_state) or not self.has_state_requirements(state_blob):
            return EquipResult.NONE
        return self.has_notch_requirments(state_blob, item_state)

    # TODO: pretty sure this is for some overload i don't understand
    # def can_equip(self, state_blob: Counter, item_state: CollectionState) -> EquipResult:
    #     if not self.has_item(item_state):
    #         return EquipResult.NONE

    #     overcharm = False
    #     for _ in (None,):  # there's an iteration in upstream I don't want to lose sight of
    #         if self.has_state_requirements(state_blob):
    #             ret = self.has_notch_requirments(state_blob, item_state)
    #             if ret == EquipResult.NONE:
    #                 continue
    #             elif ret == EquipResult.OVERCHARM:  # noqa: RET507
    #                 overcharm = True
    #             elif ret == EquipResult.NONOVERCHARM:
    #                 return ret
    #     return EquipResult.OVERCHARM if overcharm else EquipResult.NONE

    def do_equip_charm(self, state_blob: Counter, item_state: CollectionState) -> None:
        notch_cost = self.get_notch_cost(item_state)
        state_blob["USEDNOTCHES"] += notch_cost
        # one of these 2 should probably go at some point
        state_blob[self.term] = True
        state_blob[self.charm_key] = True
        state_blob["MAXNOTCHCOST"] = max(state_blob["MAXNOTCHCOST"], notch_cost)
        if state_blob["USEDNOTCHES"] > item_state.count("NOTCHES", self.player):
            state_blob["OVERCHARMED"] = True

    def is_equipped(self, state_blob: Counter) -> bool:
        return bool(state_blob[self.term])

    def set_unequippable(self, state_blob: Counter) -> None:
        state_blob[self.anti_term] = True

    def get_avaliable_notches(self, state_blob: Counter, item_state: CollectionState) -> int:
        return item_state.count("NOTCHES", self.player) - state_blob["USEDNOTCHES"]

    def can_exclude(self, options: HKOptions) -> bool:
        return False

    def add_simple_item_reqs(self, items: Counter) -> None:
        items[self.charm_key] = 1

    def is_determined(self, state_blob: Counter, item_state: CollectionState) -> bool:
        return state_blob[self.term] or state_blob[self.anti_term]

    def has_charm_progression(self, item_state: CollectionState) -> bool:
        return self.has_item(item_state)

    @staticmethod
    def generate_charm_combinations(state_blob: Counter, item_state: CollectionState, charm_list: "Iterable[EquipCharmVariable]"):
        charms = []
        base_state = state_blob.copy()
        for c in charm_list:
            if not c.is_determined(base_state, item_state):
                if (
                    not c.has_charm_progression(item_state)
                    or not c.has_state_requirements(base_state)
                    or not c.has_notch_requirments(base_state, item_state)
                ):
                    c.set_unequippable(base_state)
                else:
                    charms.append(c)

        charm_len = len(charms)
        if charm_len == 0:
            yield base_state
            return
        elif charm_len > 30:
            raise Exception("Out of range when calculating generate_charm_combinations")

        p = 1 << charm_len
        for i in range(p):
            cur_state = base_state.copy()
            for j in range(charm_len):
                f = 1 << j
                if (i & f) == f:  # equip
                    if not charms[j].try_equip(cur_state, item_state):
                        # should only fail due to out of notches
                        break
                else:  # do not equip
                    charms[j].set_unequippable(cur_state)
            else:
                # only yield if we did not break
                yield cur_state


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
    def break_charm(self, state_blob: Counter, item_state: CollectionState) -> None:
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

    def has_item(self, item_state: CollectionState) -> bool:
        if self.void:
            count = 3
        else:
            count = 2
        return item_state.has("WHITEFRAGMENT", self.player, count)

    # TODO double check this is not necessary with has_item defined
    # def _modify_state(self, state_blob: Counter, item_state: CollectionState, self.player: int):
    #     # TODO figure this out
    #     # TODO actually
    #     print(self.void)
    #     return super()._modify_state(state_blob, item_state)

    def add_simple_item_reqs(self, items: Counter) -> None:
        if self.void:
            count = 3
        else:
            count = 2
        if items[self.charm_key] < count:
            items[self.charm_key] = count
