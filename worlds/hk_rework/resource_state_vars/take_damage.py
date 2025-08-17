from collections import Counter

from BaseClasses import CollectionState

from . import RCStateVariable
from ..constants import BASE_HEALTH


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
