from typing import Dict, NamedTuple, Set, Optional
from .names import location_names as lname


class AnimalWellLocationData(NamedTuple):
    location_groups: Optional[list[str]] = None


location_base_id = 11553377

location_table: Dict[str, AnimalWellLocationData] = {
    # major items
    lname.b_wand_chest: AnimalWellLocationData(["Toys"]),
    lname.bb_wand_chest: AnimalWellLocationData(["Toys"]),
    lname.disc_spot: AnimalWellLocationData(["Toys"]),
    lname.yoyo_chest: AnimalWellLocationData(["Toys"]),
    lname.slink_chest: AnimalWellLocationData(["Toys"]),
    lname.flute_chest: AnimalWellLocationData(["Toys", "Egg Rewards"]),
    lname.top_chest: AnimalWellLocationData(["Toys", "Egg Rewards"]),
    lname.lantern_chest: AnimalWellLocationData(["Toys"]),
    lname.uv_lantern_chest: AnimalWellLocationData(["Toys"]),
    lname.b_ball_chest: AnimalWellLocationData(["Toys"]),
    lname.remote_chest: AnimalWellLocationData(["Toys"]),
    lname.wheel_chest: AnimalWellLocationData(["Toys"]),
    lname.firecracker_first: AnimalWellLocationData(["Toys"]),

    lname.mock_disc_chest: AnimalWellLocationData(["Toys"]),
    lname.fanny_pack_chest: AnimalWellLocationData(),

    lname.match_start_ceiling: AnimalWellLocationData(["Matches"]),
    lname.match_fish_mural: AnimalWellLocationData(["Matches"]),
    lname.match_dog_switch_bounce: AnimalWellLocationData(["Matches"]),
    lname.match_dog_upper_east: AnimalWellLocationData(["Matches"]),
    lname.match_bear: AnimalWellLocationData(["Matches"]),
    lname.match_above_egg_room: AnimalWellLocationData(["Matches"]),
    lname.match_center_well: AnimalWellLocationData(["Matches"]),
    lname.match_guard_room: AnimalWellLocationData(["Matches"]),
    lname.match_under_mouse_statue: AnimalWellLocationData(["Matches"]),

    lname.key_bear_lower: AnimalWellLocationData(["Keys"]),
    lname.key_bear_upper: AnimalWellLocationData(["Keys"]),
    lname.key_chest_mouse_head_lever: AnimalWellLocationData(["Keys"]),
    lname.key_frog_guard_room_west: AnimalWellLocationData(["Keys"]),
    lname.key_frog_guard_room_east: AnimalWellLocationData(["Keys"]),
    lname.key_dog: AnimalWellLocationData(["Keys"]),
    lname.key_house: AnimalWellLocationData(["Keys"]),
    lname.key_office: AnimalWellLocationData(["Keys"]),

    lname.medal_e: AnimalWellLocationData(["Keys", "Medals"]),
    lname.medal_s: AnimalWellLocationData(["Keys", "Medals"]),
    lname.medal_k: AnimalWellLocationData(["Keys", "Medals"]),

    lname.flame_blue: AnimalWellLocationData(["Flames"]),
    lname.flame_green: AnimalWellLocationData(["Flames"]),
    lname.flame_violet: AnimalWellLocationData(["Flames"]),
    lname.flame_pink: AnimalWellLocationData(["Flames"]),

    # eggs, sorted by row top-to-bottom
    lname.egg_reference: AnimalWellLocationData(["Eggs"]),
    lname.egg_brown: AnimalWellLocationData(["Eggs"]),
    lname.egg_raw: AnimalWellLocationData(["Eggs"]),
    lname.egg_pickled: AnimalWellLocationData(["Eggs"]),
    lname.egg_big: AnimalWellLocationData(["Eggs"]),
    lname.egg_swan: AnimalWellLocationData(["Eggs"]),
    lname.egg_forbidden: AnimalWellLocationData(["Eggs"]),
    lname.egg_shadow: AnimalWellLocationData(["Eggs"]),
    lname.egg_vanity: AnimalWellLocationData(["Eggs"]),
    lname.egg_service: AnimalWellLocationData(["Eggs"]),

    lname.egg_depraved: AnimalWellLocationData(["Eggs"]),
    lname.egg_chaos: AnimalWellLocationData(["Eggs"]),
    lname.egg_upside_down: AnimalWellLocationData(["Eggs"]),
    lname.egg_evil: AnimalWellLocationData(["Eggs"]),
    lname.egg_sweet: AnimalWellLocationData(["Eggs"]),
    lname.egg_chocolate: AnimalWellLocationData(["Eggs"]),
    lname.egg_value: AnimalWellLocationData(["Eggs"]),
    lname.egg_plant: AnimalWellLocationData(["Eggs"]),
    lname.egg_red: AnimalWellLocationData(["Eggs"]),
    lname.egg_orange: AnimalWellLocationData(["Eggs"]),
    lname.egg_sour: AnimalWellLocationData(["Eggs"]),
    lname.egg_post_modern: AnimalWellLocationData(["Eggs"]),

    lname.egg_universal: AnimalWellLocationData(["Eggs"]),
    lname.egg_lf: AnimalWellLocationData(["Eggs"]),
    lname.egg_zen: AnimalWellLocationData(["Eggs"]),
    lname.egg_future: AnimalWellLocationData(["Eggs"]),
    lname.egg_friendship: AnimalWellLocationData(["Eggs"]),
    lname.egg_truth: AnimalWellLocationData(["Eggs"]),
    lname.egg_transcendental: AnimalWellLocationData(["Eggs"]),
    lname.egg_ancient: AnimalWellLocationData(["Eggs"]),
    lname.egg_magic: AnimalWellLocationData(["Eggs"]),
    lname.egg_mystic: AnimalWellLocationData(["Eggs"]),
    lname.egg_holiday: AnimalWellLocationData(["Eggs"]),
    lname.egg_rain: AnimalWellLocationData(["Eggs"]),
    lname.egg_razzle: AnimalWellLocationData(["Eggs"]),
    lname.egg_dazzle: AnimalWellLocationData(["Eggs"]),

    lname.egg_virtual: AnimalWellLocationData(["Eggs"]),
    lname.egg_normal: AnimalWellLocationData(["Eggs"]),
    lname.egg_great: AnimalWellLocationData(["Eggs"]),
    lname.egg_gorgeous: AnimalWellLocationData(["Eggs"]),
    lname.egg_planet: AnimalWellLocationData(["Eggs"]),
    lname.egg_moon: AnimalWellLocationData(["Eggs"]),
    lname.egg_galaxy: AnimalWellLocationData(["Eggs"]),
    lname.egg_sunset: AnimalWellLocationData(["Eggs"]),
    lname.egg_goodnight: AnimalWellLocationData(["Eggs"]),
    lname.egg_dream: AnimalWellLocationData(["Eggs"]),
    lname.egg_travel: AnimalWellLocationData(["Eggs"]),
    lname.egg_promise: AnimalWellLocationData(["Eggs"]),
    lname.egg_ice: AnimalWellLocationData(["Eggs"]),
    lname.egg_fire: AnimalWellLocationData(["Eggs"]),

    lname.egg_bubble: AnimalWellLocationData(["Eggs"]),
    lname.egg_desert: AnimalWellLocationData(["Eggs"]),
    lname.egg_clover: AnimalWellLocationData(["Eggs"]),
    lname.egg_brick: AnimalWellLocationData(["Eggs"]),
    lname.egg_neon: AnimalWellLocationData(["Eggs"]),
    lname.egg_iridescent: AnimalWellLocationData(["Eggs"]),
    lname.egg_rust: AnimalWellLocationData(["Eggs"]),
    lname.egg_scarlet: AnimalWellLocationData(["Eggs"]),
    lname.egg_sapphire: AnimalWellLocationData(["Eggs"]),
    lname.egg_ruby: AnimalWellLocationData(["Eggs"]),
    lname.egg_jade: AnimalWellLocationData(["Eggs"]),
    lname.egg_obsidian: AnimalWellLocationData(["Eggs"]),
    lname.egg_crystal: AnimalWellLocationData(["Eggs"]),
    lname.egg_golden: AnimalWellLocationData(["Eggs"]),

    lname.egg_65: AnimalWellLocationData(["Eggs", "Egg Rewards"]),

    # all locations beyond this point have no cooresponding item in the item pool
    lname.map_chest: AnimalWellLocationData(["Map Items"]),
    lname.stamp_chest: AnimalWellLocationData(["Map Items"]),
    lname.pencil_chest: AnimalWellLocationData(["Map Items", "Egg Rewards"]),
    lname.mama_cha: AnimalWellLocationData(),
    lname.squirrel_acorn: AnimalWellLocationData(),

    # bnnnnuyuy
    lname.bunny_barcode: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_chinchilla_vine: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_crow: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_disc_spike: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_dream: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_duck: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_face: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_file_bud: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_fish: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_ghost_dog: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_lava: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_map: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_mural: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_tv: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_uv: AnimalWellLocationData(["Bunnies"]),
    lname.bunny_water_spike: AnimalWellLocationData(["Bunnies"]),
}

location_name_to_id: Dict[str, int] = {name: location_base_id + index for index, name in enumerate(location_table)}

location_name_groups: Dict[str, Set[str]] = {}
for loc_name, loc_data in location_table.items():
    if loc_data.location_group:
        location_name_groups.setdefault(loc_data.location_group, set()).add(loc_name)
