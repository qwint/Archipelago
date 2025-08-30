from collections import Counter

from BaseClasses import CollectionState

from . import RCStateVariable
from ..options import HKOptions


class DirectCompare:
    term: str
    op: str
    value: str  # may be int or bool

    def __init__(self, term: str, player: int):
        self.term, self.value = (*term.split(self.op),)
        self.player = player

    @classmethod
    def try_match(cls, term: str):
        return cls.op in term

    def can_exclude(self, options: HKOptions):
        return False

    @property
    def terms(self) -> list[str]:
        return [self.term]


class EQVariable(DirectCompare, RCStateVariable):
    term: str
    op: str = "="
    value: str  # may be int or bool

    def _modify_state(self, state_blob: Counter, item_state: CollectionState):
        if self.value.isdigit():
            return state_blob[self.term] == int(self.value), state_blob
        else:  # noqa: RET505
            v = self.value == "TRUE"
            assert v or self.value == "FALSE"
            return state_blob[self.term] == v, state_blob


class GTVariable(DirectCompare, RCStateVariable):
    term: str
    op: str = ">"
    value: str

    def _modify_state(self, state_blob: Counter, item_state: CollectionState):
        assert self.value.isdigit()
        return state_blob[self.term] > int(self.value), state_blob


class LTVariable(DirectCompare, RCStateVariable):
    term: str
    op: str = "<"
    value: str

    def _modify_state(self, state_blob: Counter, item_state: CollectionState):
        assert self.value.isdigit()
        return state_blob[self.term] < int(self.value), state_blob
