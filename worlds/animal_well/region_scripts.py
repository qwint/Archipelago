from typing import List, Dict, TYPE_CHECKING
from BaseClasses import Region, Location, ItemClassification
from worlds.generic.Rules import CollectionRule, add_rule
from .region_data import AWType, LocType
from .names import ItemNames as iname, LocationNames as lname, RegionNames
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


def convert_helper_reqs(helper_name: str, reqs: List[List[str]]) -> List[List[str]]:
    new_list_storage: List[List[str]] = []
    for i, sublist in enumerate(reqs):
        for j, req in enumerate(sublist):
            if req == helper_name:
                for replacement in helper_reference[helper_name]:
                    new_list = sublist.copy()
                    new_list[j] = replacement
                    new_list_storage.append(new_list)
                del reqs[i]
                break

    for sublist in new_list_storage:
        reqs.append(sublist)

    # remove empty lists from the reqs
    return reqs


def convert_key_reqs(reqs: List[List[str]], options: AnimalWellOptions) -> List[List[str]]:
    if not options.key_ring:
        for sublist in reqs:
            for i, req in enumerate(sublist):
                if req == iname.key_ring:
                    sublist[i] = iname.can_use_keys
    return reqs


def convert_match_reqs(reqs: List[List[str]], options: AnimalWellOptions) -> List[List[str]]:
    if not options.matchbox:
        for sublist in reqs:
            for i, req in enumerate(sublist):
                if req == iname.matchbox:
                    sublist[i] = iname.can_use_matches
    return reqs


def convert_bubble_reqs(reqs: List[List[str]], options: AnimalWellOptions) -> List[List[str]]:
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


def convert_tech_reqs(reqs: List[List[str]], options: AnimalWellOptions) -> List[List[str]]:
    # these convert [[wheel_hop], [disc]] to either [[wheel], [disc]] or [[disc]]
    # and convert [[disc_hop_hard]] to either [[disc]] or []
    reqs = [
        [iname.wheel if item == iname.wheel_hop else item for item in sublist]
        for sublist in reqs
        if not (iname.wheel_hop in sublist and not options.wheel_hopping)
    ]
    reqs = [
        [iname.disc if item == iname.disc_hop else item for item in sublist]
        for sublist in reqs
        if not (iname.disc_hop in sublist and not options.disc_hopping)
    ]
    reqs = [
        [iname.disc if item == iname.disc_hop_hard else item for item in sublist]
        for sublist in reqs
        if not (iname.disc_hop_hard in sublist and not options.disc_hopping == options.disc_hopping.option_multiple)
    ]
    reqs = [
        [None if item == iname.weird_tricks else item for item in sublist]
        for sublist in reqs
        if not (iname.weird_tricks in sublist and not options.weird_tricks)
    ]
    return reqs


def create_aw_regions(world: "AnimalWellWorld") -> Dict[str, Region]:
    aw_regions: Dict[str, Region] = {}
    for region_name in RegionNames:
        aw_regions[region_name] = Region(region_name, world.player, world.multiworld)
    return aw_regions


# basicaly any(all(individual requirements))
def interpret_rule(reqs: List[List[str]], world: "AnimalWellWorld") -> CollectionRule:
    # todo: check if we actually need to set equal here, or if we can just remove the returns
    # expand the helpers into individual items
    reqs = convert_key_reqs(reqs, world.options)
    reqs = convert_match_reqs(reqs, world.options)
    reqs = convert_bubble_reqs(reqs, world.options)
    reqs = convert_tech_reqs(reqs, world.options)
    for helper_name in helper_reference.keys():
        reqs = convert_helper_reqs(helper_name, reqs)
    if not reqs:
        return lambda state: True
    return lambda state: any(state.has_all(sublist, world.player) for sublist in reqs)


def create_regions_and_set_rules(world: "AnimalWellWorld") -> None:
    player = world.player
    egg_ratio = world.options.eggs_needed.value / 64
    aw_regions = create_aw_regions(world)
    for origin_name, destinations in world.traversal_requirements.items():
        # don't create these regions if bunny warps are not in logic
        if not world.options.bunny_warps_in_logic and origin_name in [RegionNames.bulb_bunny_spot,
                                                                      RegionNames.bear_map_bunny_spot,
                                                                      RegionNames.bear_chinchilla_song_room]:
            continue
        for destination_name, data in destinations.items():
            if data.type == AWType.location:
                if not world.options.bunnies_as_checks and data.loc_type == LocType.bunny:
                    continue
                if (world.options.bunnies_as_checks == world.options.bunnies_as_checks.option_exclude_tedious and
                        destination_name in [lname.bunny_mural, lname.bunny_dream, lname.bunny_uv,
                                             lname.bunny_lava]):
                    continue
                if not world.options.candle_checks and data.loc_type == LocType.candle:
                    continue
                # not shuffling these yet
                if data.loc_type == LocType.figure:
                    continue
                if data.event:
                    location = AWLocation(player, destination_name, None, aw_regions[origin_name])
                    location.place_locked_item(AWItem(data.event, ItemClassification.progression, None, player))
                else:
                    location = AWLocation(player, destination_name, world.location_name_to_id[destination_name],
                                          aw_regions[origin_name])
                location.access_rule = interpret_rule(data.rules, world)
                if data.eggs_required:  # swap to count_group_unique in 0.4.7
                    add_rule(location, lambda state, eggs_required=data.eggs_required:
                             state.count_group("Eggs", player) >= eggs_required * egg_ratio)
                aw_regions[origin_name].locations.append(location)
            elif data.type == AWType.region:
                if data.bunny_warp and not world.options.bunny_warps_in_logic and not world.options.bunnies_as_checks:
                    continue
                entrance = aw_regions[origin_name].connect(connecting_region=aw_regions[destination_name],
                                                           rule=interpret_rule(data.rules, world))
                if data.eggs_required:  # swap to count_group_unique in 0.4.7
                    add_rule(entrance, lambda state, eggs_required=data.eggs_required:
                             state.count_group("Eggs", player) >= eggs_required * egg_ratio)

    if not world.options.key_ring:
        location = AWLocation(player, lname.got_all_keys, None, aw_regions[RegionNames.bird_area])
        location.place_locked_item(AWItem(iname.can_use_keys, ItemClassification.progression, None, player))
        location.access_rule = lambda state: state.has(iname.key, player, 6)
        aw_regions[RegionNames.bird_area].locations.append(location)

    if not world.options.matchbox:
        location = AWLocation(player, lname.got_all_matches, None, aw_regions[RegionNames.bird_area])
        location.place_locked_item(AWItem(iname.can_use_matches, ItemClassification.progression, None, player))
        location.access_rule = lambda state: state.has(iname.match, player, 9)
        aw_regions[RegionNames.bird_area].locations.append(location)

    # a little hacky but oh well, it keeps other parts from being more convoluted
    bbwand = AWLocation(player, lname.upgraded_wand, None, aw_regions[RegionNames.bird_area])
    bbwand.place_locked_item(AWItem(iname.bubble_long, ItemClassification.progression, None, player))
    bbwand.access_rule = lambda state: state.has(iname.bubble, player, 2)
    aw_regions[RegionNames.bird_area].locations.append(bbwand)

    k_medal = AWLocation(player, lname.k_medal, None, aw_regions[RegionNames.bird_area])
    k_medal.place_locked_item(AWItem(iname.k_medal, ItemClassification.progression, None, player))
    k_medal.access_rule = lambda state: state.has(iname.k_shard, player, 3)
    aw_regions[RegionNames.bird_area].locations.append(k_medal)

    for region in aw_regions.values():
        world.multiworld.regions.append(region)

    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)
