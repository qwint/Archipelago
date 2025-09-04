from collections import Counter

from BaseClasses import CollectionState

from . import RCStateVariable


class StagStateVariable(RCStateVariable):
    prefix = "$STAGSTATEMODIFIER"

    def parse_term(self):
        pass

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    @property
    def terms(self) -> list[str]:
        return []

    def _modify_state(self, state_blob: Counter, item_state: CollectionState):
        state_blob["NOFLOWER"] = 1
        return True, state_blob

    def can_exclude(self, options):
        return False
