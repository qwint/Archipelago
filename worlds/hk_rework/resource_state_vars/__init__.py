from collections import Counter, defaultdict
from collections.abc import Generator
from typing import ClassVar

from BaseClasses import CollectionState


RCStateVariable = object  # for future typing


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

    def parse_term(self, *args):
        """Subclasses should use this to expect parameter counts for init"""
        pass

    @classmethod
    def try_match(cls, term: str) -> bool:
        """Returns True if this class can handle the passed in term"""
        return False

    @property
    def terms(self) -> list[str]:
        raise NotImplementedError()

    def modify_state(self, state_blob: Counter, item_state: CollectionState) -> Generator[Counter]:
        valid, output_state = self._modify_state(state_blob, item_state)
        if valid:
            yield output_state

    def _modify_state(self, state_blob: Counter, item_state: CollectionState) -> tuple[bool, Counter]:
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
