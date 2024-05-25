from typing import Dict, TYPE_CHECKING, cast
from BaseClasses import CollectionState, Region, Location, ItemClassification
from .regions import traversal_requirements, AWType
from .names import ItemNames as iname, RegionNames
from . import AWItem
if TYPE_CHECKING:
    from . import AnimalWellWorld


class AWLocation(Location):
    game: str = "ANIMAL WELL"


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
    return state.has_any({iname.firecrackers, iname.lantern, iname.match}, player)


def can_light_candle(state: CollectionState, player: int) -> bool:
    return state.has(iname.matchbox, player) or state.has(iname.match, player, 9)


def lit_all_candles(state: CollectionState, player: int) -> bool:
    return state.has_all({iname.event_candle_first, iname.event_candle_dog_dark, iname.event_candle_dog_switch_box,
                          iname.event_candle_dog_many_switches, iname.event_candle_dog_disc_switches,
                          iname.event_candle_dog_bat, iname.event_candle_penguin, iname.event_candle_frog,
                          iname.event_candle_bear}, player)


def can_unlock_key_door(state: CollectionState, player: int) -> bool:
    return state.has(iname.key_ring, player) or state.has(iname.key, player, 6)


def create_aw_regions(world: "AnimalWellWorld") -> Dict[str, Region]:
    aw_regions: Dict[str, Region] = {}
    for region_name in RegionNames:
        aw_regions[region_name] = Region(region_name, world.player, world.multiworld)

    return aw_regions


def create_regions_and_set_rules(world: "AnimalWellWorld") -> None:
    player = world.player
    aw_regions = create_aw_regions(world)
    # todo: make function for converting the rules into access rules
    for origin_name, destinations in traversal_requirements.items():
        for destination_name, data in destinations.items():
            if data.type == AWType.location:
                if data.event:
                    location = AWLocation(player, destination_name, None, aw_regions[origin_name])
                    location.place_locked_item(AWItem(data.event, ItemClassification.progression, None, player))
                else:
                    location = AWLocation(player, destination_name, address=world.location_name_to_id[destination_name])
                aw_regions[origin_name].locations.append(location)
            elif data.type == AWType.region:
                aw_regions[origin_name].connect(aw_regions[destination_name])

    for region in aw_regions.values():
        world.multiworld.regions.append(region)
