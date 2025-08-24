from collections import Counter

from BaseClasses import CollectionState

from . import RCStateVariable


class SpendSoulVariable(RCStateVariable):
    prefix = "$SPENDSOUL"
    amount: int

    def parse_term(self, amount):
        self.amount = int(amount)

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState):
        if state_blob["SPENTALLSOUL"]:
            return False, state_blob

        soul = self.get_soul(state_blob)
        if soul < self.amount:
            return False, state_blob

        reserve_soul = self.get_reserve_soul(state_blob, item_state)
        if reserve_soul >= self.amount:
            state_blob["SPENTRESERVESOUL"] += self.amount
        else:
            state_blob["SPENTRESERVESOUL"] += reserve_soul
            state_blob["SPENTSOUL"] += self.amount - reserve_soul

        required_max_soul = state_blob["REQUIREDMAXSOUL"]
        alt_req = max(self.amount, state_blob["SPENTSOUL"])
        if alt_req > required_max_soul:
            state_blob["REQUIREDMAXSOUL"] = alt_req

        return True, state_blob

    def get_soul(self, state_blob):
        return 99 - state_blob["SOULLIMITER"] - state_blob["SPENTSOUL"]

    def get_reserve_soul(self, state_blob: Counter, item_state: CollectionState):
        return ((item_state.count("VESSELFRAGMENTS", self.player) // 3) * 33) - state_blob["SPENTRESERVESOUL"]

    def can_exclude(self, options):
        return False
