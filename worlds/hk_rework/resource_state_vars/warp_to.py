from collections import Counter

from BaseClasses import CollectionState

from . import RCStateVariable
from .resetter import BenchResetVariable, SaveQuitResetVariable, StartRespawnResetVariable


class WarpToBenchResetVariable(RCStateVariable):
    prefix = "$WARPTOBENCH"
    sq_reset: SaveQuitResetVariable
    bench_reset: BenchResetVariable

    def parse_term(self):
        self.sq_reset = SaveQuitResetVariable(SaveQuitResetVariable.prefix, self.player)
        self.bench_reset = BenchResetVariable(BenchResetVariable.prefix, self.player)

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState):
        valid, state_blob = self.sq_reset._modify_state(state_blob, item_state)
        if valid:
            return self.bench_reset._modify_state(state_blob, item_state)
        else:  # noqa: RET505
            return False, state_blob

    def can_exclude(self, options):
        return False


class WarpToStartResetVariable(RCStateVariable):
    prefix = "$WARPTOSTART"
    sq_reset: SaveQuitResetVariable
    start_reset: StartRespawnResetVariable

    def parse_term(self):
        self.sq_reset = SaveQuitResetVariable(SaveQuitResetVariable.prefix, self.player)
        self.start_reset = StartRespawnResetVariable(StartRespawnResetVariable.prefix, self.player)

    @classmethod
    def try_match(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def get_terms(cls):
    #     return (term for term in ("VessleFragments",))

    def _modify_state(self, state_blob: Counter, item_state: CollectionState):
        valid, state_blob = self.sq_reset._modify_state(state_blob, item_state)
        if valid:
            return self.start_reset._modify_state(state_blob, item_state)
        else:  # noqa: RET505
            return False, state_blob

    def can_exclude(self, options):
        return False
