from typing import Dict, TYPE_CHECKING, cast

from BaseClasses import CollectionState
from .names import item_names as iname, location_names as lname
if TYPE_CHECKING:
    from . import AnimalWellWorld


# helper functions, idk if we're gonna have more than that here
def can_bubble_short(state: CollectionState, player: int) -> bool:
    world: "AnimalWellWorld" = cast("AnimalWellWorld", state.multiworld.worlds[player])
    if world.options.bubble_jumping:
        return state.has(iname.bubble, player)
    else:
        return state.has(iname.bubble_long, player)


def can_bubble_long(state: CollectionState, player: int) -> bool:
    world: "AnimalWellWorld" = cast("AnimalWellWorld", state.multiworld.worlds[player])
    if world.options.bubble_jumping == 2:
        return state.has(iname.bubble, player)
    else:
        return state.has(iname.bubble_long, player)
