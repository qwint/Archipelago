from collections import Counter
from collections.abc import Generator
from typing import ClassVar

from BaseClasses import CollectionState


RCStateVariable = object  # for future typing


class ResourceStateHandler(type):
    handlers: ClassVar[list[RCStateVariable]] = []
    _handler_cache: ClassVar[dict[str, RCStateVariable]] = {}

    def __new__(mcs, name, bases, dct):
        new_class = super().__new__(mcs, name, bases, dct)
        ResourceStateHandler.handlers.append(new_class)
        return new_class

    @staticmethod
    def get_handler(req: str) -> RCStateVariable:
        ret = None
        if req in ResourceStateHandler._handler_cache:
            return ResourceStateHandler._handler_cache[req]
        # ret = next(handler(req) for handler in ResourceStateHandler.handlers if handler.try_match(req))
        for handler in ResourceStateHandler.handlers:
            if handler.try_match(req):
                ret = handler(req)
                continue
        assert ret, f"searched for a handler for req {req} and did not find one"
        ResourceStateHandler._handler_cache[req] = ret
        return ret


class RCStateVariable(metaclass=ResourceStateHandler):
    prefix: str
    # player: int
    # TODO: add this to the constructor and refactor out of all the function calls

    def __init__(self, term: str):
        assert term.startswith(self.prefix)

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

    @classmethod
    def get_terms(cls):
        """"""
        return []

    def modify_state(self, state_blob: Counter, item_state: CollectionState, player: int) -> Generator[Counter]:
        # print(self)
        # return (output_state for valid, output_state in [self._modify_state(state_blob, item_state, player)] if valid)
        valid, output_state = self._modify_state(state_blob, item_state, player)
        if valid:
            yield output_state

    def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int) -> tuple[bool, Counter]:
        pass

    def can_exclude(self, options) -> bool:
        return True

    def add_simple_item_reqs(self, items: Counter) -> None:
        pass


from .cast_spell import *  # noqa: E402
from .direct_compare import *  # noqa: E402
from .equip_charm import *  # noqa: E402
from .flower_provider import *  # noqa: E402
from .lifeblood_count import *  # noqa: E402
from .regain_soul import *  # noqa: E402
from .resetter import *  # noqa: E402
from .shade_state import *  # noqa: E402
from .spend_soul import *  # noqa: E402
from .stag_state import *  # noqa: E402
from .take_damage import *  # noqa: E402
from .warp_to import *  # noqa: E402


# TODO - i don't know what this is for; says it's for handling subhandlers but not sure when
# class StateModifierWrapper(RCStateVariable):
#     prefix = "$BENCHRESET"

#     def parse_term(self):
#         pass

#     @classmethod
#     def try_match(cls, term: str):
#         return term.startswith(cls.prefix)

#     # @classmethod
#     # def get_terms(cls):
#     #     return (term for term in ("VessleFragments",))

#     def _modify_state(self, state_blob: Counter, item_state: CollectionState, player: int):
#         pass

#     def can_exclude(self, options):
#         return False
