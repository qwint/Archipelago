from collections import Counter

from BaseClasses import CollectionState

from ..options import HKOptions
from . import RCStateVariable


class RegainSoulVariable(RCStateVariable):
    prefix: str = "$REGAINSOUL"
    amount: int

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Not Fully Implemented, use soul_manager instead if possible")

    def parse_term(self, amount: str) -> None:
        self.amount = int(amount)

    @classmethod
    def try_match(cls, term: str) -> bool:
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState) -> tuple[bool, Counter]:
        if state_blob["CANNOTREGAINSOUL"]:
            return False, state_blob
        if state_blob["SPENTALLSOUL"]:
            state_blob["SPENTRESERVESOUL"] = self.get_max_reserve_soul(item_state)
            state_blob["SPENTSOUL"] = self.get_max_soul(state_blob)
            state_blob["SPENTALLSOUL"] = False
        soul_diff = self.get_max_soul(state_blob) - state_blob["SPENTSOUL"]  # i simplified this
        if self.amount < soul_diff:
            state_blob["SPENTSOUL"] -= self.amount
        else:
            state_blob["SPENTSOUL"] = 0
            amount = self.amount - soul_diff
            reserve_diff = (self.get_max_reserve_soul(item_state) - state_blob["SPENTRESERVESOUL"])
            # i simplified this
            if amount < reserve_diff:
                state_blob["SPENTRESERVESOUL"] -= amount
            else:
                state_blob["SPENTRESERVESOUL"] = 0
        return True, state_blob

    def get_max_reserve_soul(self, item_state: CollectionState) -> int:
        return (item_state.count("VesselFragment", self.player) // 3) * 33

    def get_max_soul(self, state_blob: Counter) -> int:
        return 99 - state_blob["SOULLIMITER"]

    def can_exclude(self, options: HKOptions) -> bool:
        return False
