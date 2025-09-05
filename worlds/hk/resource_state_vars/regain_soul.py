from ..options import HKOptions
from . import RCStateVariable, cs, rs


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

    def _modify_state(self, state_blob: rs, item_state: cs) -> tuple[bool, rs]:
        if state_blob.get_bool("CANNOTREGAINSOUL"):
            return False, state_blob
        if state_blob.get_bool("SPENTALLSOUL"):
            state_blob.set_int("SPENTRESERVESOUL", self.get_max_reserve_soul(item_state))
            state_blob.set_int("SPENTSOUL", self.get_max_soul(state_blob))
            state_blob.set_bool("SPENTALLSOUL", False)
        soul_diff = self.get_max_soul(state_blob) - state_blob.get_int("SPENTSOUL")  # i simplified this
        if self.amount < soul_diff:
            state_blob.set_int("SPENTSOUL", state_blob.get_int("SPENTSOUL") - self.amount)
        else:
            state_blob.set_int("SPENTSOUL", 0)
            amount = self.amount - soul_diff
            reserve_diff = (self.get_max_reserve_soul(item_state) - state_blob.get_int("SPENTRESERVESOUL"))
            # i simplified this
            if amount < reserve_diff:
                state_blob.set_int("SPENTRESERVESOUL", state_blob.get_int("SPENTRESERVESOUL") - amount)
            else:
                state_blob.set_int("SPENTRESERVESOUL", 0)
        return True, state_blob

    def get_max_reserve_soul(self, item_state: cs) -> int:
        return (item_state.count("VesselFragment", self.player) // 3) * 33

    def get_max_soul(self, state_blob: rs) -> int:
        return 99 - state_blob.get_int("SOULLIMITER")

    def can_exclude(self, options: HKOptions) -> bool:
        return False
