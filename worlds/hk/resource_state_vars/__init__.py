from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Generator
from copy import copy
# from dataclasses import dataclass
from typing import ClassVar

from BaseClasses import CollectionState

from ..data.constants.state_field_names import StateFieldNames


bit_per_key = {name: 1 << i for i, name in enumerate(StateFieldNames)}


# @dataclass
class ResourceState:
    field: int = bit_per_key[StateFieldNames.NOPASSEDCHARMEQUIP] | bit_per_key[StateFieldNames.NOFLOWER]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if value is bool:
                self.set_bool(key, value)
            else:
                self.set_int(key, value)

    def set_int(self, key: str, value: int):
        assert hasattr(self, key)
        setattr(self, key, value)
        self.set_bool(key, value)

    def set_bool(self, key: str, value: bool):
        if value:
            # set the bit with an OR
            self.field |= bit_per_key[key]
        else:
            # null the bit with an inverse AND
            self.field &= (~bit_per_key[key])

    def get_int(self, key: str) -> int:
        return getattr(self, key, 0)

    def get_bool(self, key) -> bool:
        return bool(self.field & bit_per_key[key])

    def copy(self):
        return copy(self)


# default_state = KeyedDefaultDict(lambda key: True if key == "NOFLOWER" else False)
class DefaultStateFactory:
    def __call__(self, defaults=None) -> Counter:
        if defaults is None:
            defaults = {}
        ret = ResourceState(**defaults)
        # for key, value in defaults.items():
        #     ret[key] = value
        return ret


default_state = DefaultStateFactory()

# For ease of typing in submodules
cs = CollectionState
rs = ResourceState


class ResourceStateHandler(type):
    handlers: ClassVar[list[RCStateVariable]] = []
    _handler_cache: ClassVar[dict[int, dict[str, RCStateVariable]]] = defaultdict(dict)
    # TODO: check if this cache could crash and burn if it is reused for other multiworlds

    def __new__(mcs, name, bases, dct):
        new_class = super().__new__(mcs, name, bases, dct)
        ResourceStateHandler.handlers.append(new_class)
        return new_class

    @staticmethod
    def get_handler(req: str, player: int) -> RCStateVariable:
        ret = None
        if req in ResourceStateHandler._handler_cache[player]:
            return ResourceStateHandler._handler_cache[player][req]

        for handler in ResourceStateHandler.handlers:
            if handler.try_match(req):
                ret = handler(req, player)
                continue
        assert ret, f"searched for a handler for req {req} and did not find one"
        ResourceStateHandler._handler_cache[player][req] = ret
        return ret


class RCStateVariable(metaclass=ResourceStateHandler):
    prefix: str
    player: int

    def __init__(self, term: str, player: int):
        assert term.startswith(self.prefix)
        self.player = player

        # expecting "prefix" or "prefix[one,two,three]"
        if term != self.prefix:
            params = term[len(self.prefix)+1:-1].split(",")
            self.parse_term(*params)
        else:
            self.parse_term()

    def parse_term(self, *args) -> None:
        """Subclasses should use this to expect parameter counts for init"""
        pass

    @classmethod
    def try_match(cls, term: str) -> bool:
        """Returns True if this class can handle the passed in term"""
        return False

    @property
    def terms(self) -> list[str]:
        raise NotImplementedError()

    def modify_state(self, state_blob: rs, item_state: cs) -> Generator[rs]:
        valid, output_state = self._modify_state(state_blob, item_state)
        if valid:
            yield output_state

    def _modify_state(self, state_blob: rs, item_state: cs) -> tuple[bool, rs]:
        raise NotImplementedError()

    def can_exclude(self, options) -> bool:
        return True

    def add_simple_item_reqs(self, items: Counter) -> None:
        pass


from .cast_spell import *  # noqa: E402, F403
from .direct_compare import *  # noqa: E402, F403
from .equip_charm import *  # noqa: E402, F403
from .flower_provider import *  # noqa: E402, F403
from .lifeblood_count import *  # noqa: E402, F403
from .regain_soul import *  # noqa: E402, F403
from .resetter import *  # noqa: E402, F403
from .shade_state import *  # noqa: E402, F403
from .spend_soul import *  # noqa: E402, F403
from .stag_state import *  # noqa: E402, F403
from .take_damage import *  # noqa: E402, F403
from .warp_to import *  # noqa: E402, F403
