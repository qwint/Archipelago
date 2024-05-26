from typing import List, Dict, TYPE_CHECKING, cast
from BaseClasses import CollectionState, Region, Location, ItemClassification
from worlds.generic.Rules import CollectionRule
from .regions import AWType
from .names import ItemNames as iname, RegionNames
from .items import AWItem
from .options import AnimalWellOptions
if TYPE_CHECKING:
    from . import AnimalWellWorld


class AWLocation(Location):
    game: str = "ANIMAL WELL"


helper_reference: Dict[str, List[str]] = {
    iname.can_defeat_ghost: [iname.firecrackers, iname.lantern],
    # you can't really distract them with the wheel, but you can get by them with it, so it's the same thing basically
    iname.can_distract_dogs: [iname.disc, iname.top, iname.ball, iname.wheel],
    iname.can_open_flame: [iname.flute, iname.disc, iname.yoyo, iname.top, iname.ball, iname.wheel],
    iname.can_break_spikes: [iname.disc, iname.yoyo, iname.top, iname.ball, iname.wheel],
    iname.can_break_spikes_below: [iname.yoyo, iname.top, iname.ball, iname.wheel],
}


def convert_helper_req(helper_name: str, reqs: List[List[str]]) -> List[List[str]]:
    new_list_storage: List[List[str]] = []
    for i, sublist in enumerate(reqs):
        for j, req in enumerate(sublist):
            if req == helper_name:
                for replacement in helper_reference[helper_name]:
                    new_list = sublist.copy()
                    new_list[j] = replacement
                    new_list_storage.append(new_list)
                reqs[i] = []

    for sublist in new_list_storage:
        reqs.append(sublist)

    # remove empty lists from the reqs
    return [x for x in reqs if x]


def convert_key_req(reqs: List[List[str]], options: AnimalWellOptions) -> List[List[str]]:
    if options.key_ring:
        for sublist in reqs:
            for i, req in enumerate(sublist):
                if req == iname.key:
                    sublist[i] = iname.key_ring
    return reqs


def convert_match_req(reqs: List[List[str]], options: AnimalWellOptions) -> List[List[str]]:
    if options.matchbox:
        for sublist in reqs:
            for i, req in enumerate(sublist):
                if req == iname.match:
                    sublist[i] = iname.matchbox
    return reqs


def convert_bubble_req(reqs: List[List[str]], options: AnimalWellOptions) -> List[List[str]]:
    for sublist in reqs:
        for i, req in enumerate(sublist):
            # turn bubble short into b wand or bb wand based on option chosen
            if req == iname.bubble_short:
                if options.bubble_jumping:
                    sublist[i] = iname.bubble
                else:
                    sublist[i] = iname.bubble_long
            # turn bb wand into b wand if you have the hardest option on
            if req == iname.bubble_long:
                if options.bubble_jumping == options.bubble_jumping.option_on:
                    sublist[i] = iname.bubble
    return reqs


# todo: figure out what to do with this
def can_light_candle(state: CollectionState, player: int) -> bool:
    return state.has(iname.matchbox, player) or state.has(iname.match, player, 9)


# todo: figure out what to do with this
def can_unlock_key_door(state: CollectionState, player: int) -> bool:
    return state.has(iname.key_ring, player) or state.has(iname.key, player, 6)


def create_aw_regions(world: "AnimalWellWorld") -> Dict[str, Region]:
    aw_regions: Dict[str, Region] = {}
    for region_name in RegionNames:
        aw_regions[region_name] = Region(region_name, world.player, world.multiworld)
    return aw_regions


# basicaly any(all(individual requirements))
def interpret_rule(reqs: List[List[str]], world: "AnimalWellWorld") -> CollectionRule:
    # todo: check if we actually need to set equal here, or if we can just remove the returns
    # expand the helpers into individual items
    reqs = convert_key_req(reqs, world.options)
    reqs = convert_bubble_req(reqs, world.options)
    for helper_name in helper_reference.keys():
        reqs = convert_helper_req(helper_name, reqs)
    if not reqs:
        return lambda state: True
    return lambda state: any(state.has_all(sublist, world.player) for sublist in reqs)


def create_regions_and_set_rules(world: "AnimalWellWorld") -> None:
    player = world.player
    aw_regions = create_aw_regions(world)
    for origin_name, destinations in world.traversal_requirements.items():
        for destination_name, data in destinations.items():
            if data.type == AWType.location:
                if data.event:
                    location = AWLocation(player, destination_name, None, aw_regions[origin_name])
                    location.place_locked_item(AWItem(data.event, ItemClassification.progression, None, player))
                else:
                    location = AWLocation(player, destination_name, world.location_name_to_id[destination_name],
                                          aw_regions[origin_name])
                location.access_rule = interpret_rule(data.rules, world)
                aw_regions[origin_name].locations.append(location)
            elif data.type == AWType.region:
                aw_regions[origin_name].connect(connecting_region=aw_regions[destination_name],
                                                rule=interpret_rule(data.rules, world))

    for region in aw_regions.values():
        world.multiworld.regions.append(region)

    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)
