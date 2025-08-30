from collections import Counter
from collections.abc import Generator

from BaseClasses import CollectionState

from . import RCStateVariable
from .soul_manager import SoulManager
from .equip_charm import EquipCharmVariable, EquipResult, FragileCharmVariable
from ..options import HKOptions


class ShadeStateVariable(RCStateVariable):
    prefix: str = "$SHADESKIP"
    health: int

    fragile_heart: FragileCharmVariable
    voidheart: EquipCharmVariable
    jonis: EquipCharmVariable
    sp_manager: SoulManager

    def __init__(self, *args):
        super().__init__(*args)
        self.fragile_heart = FragileCharmVariable("$EQUIPPEDCHARM[Fragile_Heart]", self.player)
        self.voidheart = EquipCharmVariable("$EQUIPPEDCHARM[Void_Heart]", self.player)
        self.jonis = EquipCharmVariable("$EQUIPPEDCHARM[Joni's_Blessing]", self.player)
        self.sp_manager = SoulManager(SoulManager.prefix, self.player)

    def parse_term(self, *args) -> None:
        if len(args) == 1:
            hits = args[0]
            self.health = int(hits[:-4])
        elif len(args) == 0:
            self.health = 1
        else:
            raise Exception(f"unknown {self.prefix} term, args: {args}")

    @classmethod
    def try_match(cls, term: str) -> bool:
        return term.startswith(cls.prefix)

    @property
    def terms(self) -> list[str]:
        if self.health > 1:
            return ["MASKSHARDS"]
        return []

    def modify_state(self, state_blob: Counter, item_state: CollectionState) -> Generator[Counter]:
        ret = state_blob.copy()
        if self.do_shade_skip(ret, item_state):
            yield ret

    def do_shade_skip(self, state_blob: Counter, item_state: CollectionState) -> bool:
        if self.voidheart.is_equipped(state_blob):
            return False
        if state_blob["CANNOTSHADESKIP"] or state_blob["USEDSHADE"]:
            return False
        self.voidheart.set_unequippable(state_blob)
        state_blob["USEDSHADE"] = 1

        test_one = self.sp_manager.try_set_soul_limit(state_blob, item_state, 33, True)
        test_two = self.sp_manager.try_set_soul_limit(state_blob, item_state, 0, False)
        if not test_one or not test_two:
            # edge case where using a shade skip is not safe to re-trace the path
            return False
        if not self.check_health_requirement(state_blob, item_state):
            # checking joni's and fragile heart
            return False
        if not state_blob["NOFLOWER"]:
            state_blob["NOFLOWER"] = 1
            # just not worth it
        return True

    def check_health_requirement(self, state_blob: Counter, item_state: CollectionState) -> bool:
        if self.health == 1:
            return True

        if self.jonis.is_equipped(state_blob):
            return False
        self.jonis.set_unequippable(state_blob)

        hp = (item_state.count("MASKSHARDS", self.player) // 4) // 2
        if (
            hp >= self.health
            or (self.health == hp + 1 and self.fragile_heart.can_equip(state_blob, item_state) != EquipResult.NONE)
        ):
            self.fragile_heart.break_charm(state_blob, item_state)
            return True
        return False

    def can_exclude(self, options: HKOptions) -> bool:
        return not bool(options.ShadeSkips)
