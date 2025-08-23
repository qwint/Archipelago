from collections import Counter
from collections.abc import Generator
from itertools import chain

from BaseClasses import CollectionState

from . import RCStateVariable
from .equip_charm import EquipCharmVariable
from ..Options import HKOptions


class SoulManager:
    def spend_soul(self):
        ...

    def spend_soul_sequence(self):
        ...

    def spend_soul_slow(self):
        ...

    def try_spend_soul(self):
        ...

    def try_spend_soul_sequence(self):
        ...

    def try_spend_soul_slow(self):
        ...

    def spend_all_soul(self):
        ...

    def try_spend_all_soul(self):
        ...

    def restore_soul(self):
        ...

    def restore_all_soul(self):
        ...

    def try_restore_soul(self):
        ...

    def try_restore_all_soul(self):
        ...

    def get_soul_info(self):
        ...

    def try_set_soul_limit(self):
        ...

    def limit_soul(self):
        ...

    def soul_info(self):
        ...
