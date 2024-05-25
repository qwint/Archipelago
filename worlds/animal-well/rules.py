from typing import Dict, TYPE_CHECKING, cast
from .regions import traversal_requirements
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


def can_break_spikes(state: CollectionState, player: int) -> bool:
    return state.has_any({iname.disc, iname.yoyo, iname.top, iname.ball, iname.wheel}, player)


# can't use disc, can use any other things that break spikes
def can_break_spikes_below(state: CollectionState, player: int) -> bool:
    return state.has_any({iname.yoyo, iname.top, iname.ball, iname.wheel}, player)


def can_open_flame(state: CollectionState, player: int) -> bool:
    return state.has_any({iname.flute, iname.disc, iname.yoyo, iname.top, iname.ball, iname.wheel}, player)


# you can't really distract them with the wheel, but you can get by them with it, so it's the same thing basically
def can_distract_dogs(state: CollectionState, player: int) -> bool:
    return state.has_any({iname.disc, iname.top, iname.ball, iname.wheel}, player)


def can_defeat_ghost(state: CollectionState, player: int) -> bool:
    # for now, we're not shuffling firecrackers, so we can assume you have them. We might do so in the future though
    # return state.has_any({iname.lantern, iname.firecrackers, iname.match}, player)
    return True


def can_light_candle(state: CollectionState, player: int) -> bool:
    return state.has(iname.matchbox, player) or state.has(iname.match, player, 9)


def lit_all_candles(state: CollectionState, player: int) -> bool:
    return state.has_all({iname.event_candle_first, iname.event_candle_dog_dark, iname.event_candle_dog_switch_box,
                          iname.event_candle_dog_many_switches, iname.event_candle_dog_disc_switches,
                          iname.event_candle_dog_bat, iname.event_candle_penguin, iname.event_candle_frog,
                          iname.event_candle_bear}, player)


def can_unlock_key_door(state: CollectionState, player: int) -> bool:
    return state.has(iname.key_ring, player) or state.has(iname.key, player, 6)
