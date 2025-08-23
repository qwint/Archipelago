from collections import Counter
from collections.abc import Generator
from itertools import chain

from BaseClasses import CollectionState

from . import RCStateVariable
from .equip_charm import EquipCharmVariable
from ..Options import HKOptions


class HealthManager:
    max_damage = 99
    """Used to max out lazy hp to signal it is determined"""

    def take_damage(self):
        ...

    def take_damage_sequence(self):
        ...

    def try_focus(self):
        ...

    def do_focus(self):
        ...

    def give_blue_health(self):
        ...

    def give_health(self):
        ...

    def restore_white_health(self):
        ...

    def restore_all_health(self):
        ...

    def is_hp_determined(self):
        ...

    def determine_hp(self):
        ...

    def get_hp_info(self):
        ...

    def strict_hp_info(self):
        ...
