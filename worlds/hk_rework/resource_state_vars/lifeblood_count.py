from collections import Counter

from BaseClasses import CollectionState

from . import RCStateVariable
from .take_damage import TakeDamageVariable
from .equip_charm import EquipCharmVariable


class LifebloodCountVariable(RCStateVariable):
    prefix = "$LIFEBLOOD"
    required_blue_masks: int
    hp_manager: TakeDamageVariable
    joni_manager: EquipCharmVariable

    def parse_term(self, required_blue_masks=1):
        self.required_blue_masks = required_blue_masks
        self.hp_manager = TakeDamageVariable(TakeDamageVariable.prefix, self.player)
        self.joni_manager = EquipCharmVariable(f"{EquipCharmVariable.prefix}[Joni's_Blessing]", self.player)
        # set hp state manager and joni's equip charm variable

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    def _modify_state(self, state_blob: Counter, item_state: CollectionState):
        valid, state_blob = self.hp_manager._modify_state(state_blob, item_state)
        if valid:
            return self.joni_manager._modify_state(state_blob, item_state)
        else:  # noqa: RET505
            return False, state_blob

    def can_exclude(self, options):
        return False
