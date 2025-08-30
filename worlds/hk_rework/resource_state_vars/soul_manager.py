from collections import Counter
from collections.abc import Generator
from itertools import chain
from typing import NamedTuple, Iterable

from BaseClasses import CollectionState

from . import ResourceStateHandler
from .equip_charm import EquipCharmVariable
from ..options import HKOptions


class SoulInfo:
    soul: int
    max_soul: int
    reserve_soul: int
    max_reserve_soul: int

    def __init__(self, soul, max_soul, reserve_soul, max_reserve_soul):
        self.soul = soul
        self.max_soul = max_soul
        self.reserve_soul = reserve_soul
        self.max_reserve_soul = max_reserve_soul


class SoulManager(metaclass=ResourceStateHandler):
    prefix = "$SSM"
    player: int

    @classmethod
    def try_match(cls, term: str) -> bool:
        return term == cls.prefix

    @property
    def terms(self) -> list[str]:
        return ["VESSELFRAGMENTS"]

    def __init__(self, term: str, player: int):
        self.player = player

    def spend_soul(self, state_blob: Counter, item_state: CollectionState, amount: int) -> Generator[Counter]:
        ret = state_blob.copy()
        if self.try_spend_soul(ret, item_state, amount):
            yield ret

    def spend_soul_sequence(self):
        ...

    def spend_soul_slow(self):
        ...

    def try_spend_soul(self, state_blob: Counter, item_state: CollectionState, amount: int) -> bool:
        soul = self.get_soul_info(state_blob, item_state)
        if soul.soul < amount:
            return False
        self.spend_and_rebalance(state_blob, item_state, amount, soul)
        return True

    def spend_and_rebalance(self, state_blob: Counter, item_state: CollectionState, amount: int, soul: SoulInfo) -> None:
        self.spend_without_rebalance(state_blob, item_state, amount, soul)
        self.rebalance_reserve(state_blob, item_state, soul)

    def spend_without_rebalance(self, state_blob: Counter, item_state: CollectionState, amount: int, soul: SoulInfo) -> None:
        state_blob["SPENTSOUL"] += amount
        state_blob["REQUIREDMAXSOUL"] = max(state_blob["REQUIREDMAXSOUL"], state_blob["SPENTSOUL"])
        soul.soul -= amount

    def rebalance_reserve(self, state_blob: Counter, item_state: CollectionState, soul: SoulInfo) -> None:
        transfer = min(soul.max_soul - soul.soul, soul.reserve_soul)
        if transfer > 0:
            state_blob["SPENTSOUL"] -= transfer
            state_blob["SPENTRESERVESOUL"] += transfer
            soul.soul += transfer
            soul.reserve_soul -= transfer

    def try_spend_soul_sequence(self, state_blob: Counter, item_state: CollectionState, amount: int, casts: list[int]) -> bool:
        soul = self.get_soul_info(state_blob, item_state)
        for cast in casts:
            group_total = cast * amount
            if soul.soul < group_total:
                return False
            self.spend_and_rebalance(state_blob, item_state, group_total, soul)
        return True

    def try_spend_soul_slow(self):
        ...

    def try_resore_soul(self):
        ...

    def spend_all_soul(self, state_blob: Counter, item_state: CollectionState) -> Generator[Counter]:
        ret = state_blob.copy()
        if self.try_spend_all_soul(ret, item_state):
            yield ret

    def try_spend_all_soul(self, state_blob: Counter, item_state: CollectionState) -> bool:
        info = self.get_soul_info(state_blob, item_state)
        state_blob["SPENTSOUL"] = info.max_soul
        state_blob["REQUIREDMAXSOUL"] = info.max_soul
        state_blob["SPENTRESERVESOUL"] = info.max_reserve_soul
        return True

    def restore_soul(self):
        ...

    def restore_all_soul(self, state_blob: Counter, item_state: CollectionState, restore_reserves: bool) -> Generator[Counter]:
        ret = state_blob.copy()
        if self.try_restore_all_soul(ret, item_state, restore_reserves):
            yield ret

    def try_restore_soul(self):
        ...

    def try_restore_all_soul(self, state_blob: Counter, item_state: CollectionState, restore_reserves: bool) -> bool:
        if state_blob["CANNOTREGAINSOUL"]:
            return False
        state_blob["SPENTSOUL"] = 0
        if restore_reserves:
            state_blob["SPENTRESERVESOUL"] = 0
        return True

    def get_soul_info(self, state_blob: Counter, item_state: CollectionState) -> SoulInfo:
        max_soul = 99 - state_blob["SOULLIMITER"]
        soul = max_soul - state_blob["SPENTSOUL"]
        vessels = item_state.count("VESSELFRAGMENTS", self.player) // 3
        max_reserve_soul = vessels * 33
        reserve_soul = max_reserve_soul - state_blob["SPENTRESERVESOUL"]
        return SoulInfo(soul, max_soul, reserve_soul, max_reserve_soul)

    def try_set_soul_limit(self, state_blob: Counter, item_state: CollectionState, limiter: int, applies_to_prior_path: bool):
        if applies_to_prior_path and state_blob["REQUIREDMAXSOUL"] > limiter:
            return False
        current = state_blob["SOULLIMITER"]
        if limiter > current:
            state_blob["SOULLIMITER"] = limiter
        elif limiter < current:
            state_blob["SOULLIMITER"] = limiter
            self.try_spend_soul(state_blob, item_state, current - limiter)

        return True

    def limit_soul(self, state_blob: Counter, item_state: CollectionState, limiter: int, applies_to_prior_path: bool):
        ret = state_blob.copy()
        if self.try_set_soul_limit(ret, item_state, limiter, applies_to_prior_path):
            yield ret

    def soul_info(self):
        ...
