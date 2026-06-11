from collections.abc import MutableMapping
from worlds.AutoWorld import AutoWorldRegister
from worlds.Files import AutoPatchRegister
from settings import _update_cache


# make sure settings api sees all loaded worlds
_update_cache()


INCLUDE_WORLDS = (
    "Air Delivery",
    "Hollow Knight",
    "Minit",
    "Pseudoregalia",
    )
# Testable worlds


class FilteredRegister(MutableMapping):
    child: dict

    def __init__(self, child: dict):
        self.child = child

    def __getitem__(self, key):
        return self.child.__getitem__(key)

    def __setitem__(self, key, value):
        self.child.__setitem__(key, value)

    def __delitem__(self, key):
        self.child.__delitem__(key)

    def __iter__(self):
        return iter([i for i in self.child.__iter__() if i in INCLUDE_WORLDS])

    def __len__(self):
        return self.child.__len__()

    def copy(self):
        return FilteredRegister(self.child.copy())


AutoWorldRegister.world_types = FilteredRegister(AutoWorldRegister.world_types)
AutoPatchRegister.patch_types = FilteredRegister(AutoPatchRegister.patch_types)
