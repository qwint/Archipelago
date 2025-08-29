from collections import Counter

from BaseClasses import CollectionState

from . import RCStateVariable
from .health_manager import HealthManager
from .equip_charm import EquipCharmVariable


class LifebloodCountVariable(RCStateVariable):
    prefix = "$LIFEBLOOD"
    required_blue_masks: int
    hp_manager: HealthManager
    joni_manager: EquipCharmVariable

    def parse_term(self, required_blue_masks=1):
        self.required_blue_masks = required_blue_masks
        self.hp_manager = HealthManager(HealthManager.prefix, self.player)
        self.joni_manager = EquipCharmVariable(f"{EquipCharmVariable.prefix}[Joni's_Blessing]", self.player)
        # set hp state manager and joni's equip charm variable

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    def modify_state(self, state_blob: Counter, item_state: CollectionState):
        rets = [s for s in self.hp_manager.determine_hp(state_blob, item_state)]
        for r in rets:
            info = self.hp_manager.get_hp_info(r, item_state)
            blue_masks = info.current_blue_hp + (info.current_white_hp if self.joni_manager.is_equipped(r) else 0)
            if blue_masks >= self.required_blue_masks:
                yield r

    def can_exclude(self, options):
        return False

    @property
    def terms(self) -> list[str]:
        return self.hp_manager.terms + self.joni_manager.terms
