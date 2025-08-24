from collections import Counter

from BaseClasses import CollectionState

from . import RCStateVariable
from ..Options import HKOptions


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

    def _modify_state(self, state_blob: Counter, item_state: CollectionState) -> tuple[bool, Counter]:
        # TODO fill out when i finish equipped item variable
        if state_blob["SpentShade"]:
            return False, state_blob
        else:  # noqa: RET505
            state_blob["SpentShade"] = True
            return True, state_blob

    def can_exclude(self, options: HKOptions) -> bool:
        return not bool(options.ShadeSkips)
