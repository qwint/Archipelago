from collections import Counter

from BaseClasses import CollectionState

from . import RCStateVariable
from .health_manager import HealthManager


class TakeDamageVariable(RCStateVariable):
    prefix = "$TAKEDAMAGE"
    damage: int

    def parse_term(self, damage=1):
        self.damage = int(damage)
        self.hp_manager = HealthManager(HealthManager.prefix, self.player)
        pass

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def modify_state(self, state_blob: Counter, item_state: CollectionState):
        yield from self.hp_manager.take_damage(state_blob, item_state, self.damage)

    def can_exclude(self, options):
        # can not actually be excluded because the damage skip option is checked in logic seperately
        return False
