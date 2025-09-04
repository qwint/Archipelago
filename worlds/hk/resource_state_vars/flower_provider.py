from collections import Counter

from BaseClasses import CollectionState

from ..options import HKOptions
from . import RCStateVariable


class FlowerProviderVariable(RCStateVariable):
    prefix: str = "$FLOWERGET"

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState) -> tuple[bool, Counter]:
        state_blob["NOFLOWER"] = False
        return True, state_blob

    @classmethod
    def try_match(cls, term: str) -> bool:
        return term == cls.prefix

    def can_exclude(self, options: HKOptions) -> bool:
        return False

    @property
    def terms(self) -> list[str]:
        return []
