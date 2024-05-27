from typing import Dict, NamedTuple, Set, List
from .names import LocationNames as lname


class AWLocationData(NamedTuple):
    location_groups: List[str] = []


location_base_id = 11553377

location_table: Dict[str, AWLocationData] = {
    # major items
    lname.b_wand_chest: AWLocationData(["Toys"]),
    lname.bb_wand_chest: AWLocationData(["Toys"]),
    lname.disc_spot: AWLocationData(["Toys"]),
    lname.yoyo_chest: AWLocationData(["Toys"]),
    lname.slink_chest: AWLocationData(["Toys"]),
    lname.flute_chest: AWLocationData(["Toys", "Egg Rewards"]),
    lname.top_chest: AWLocationData(["Toys", "Egg Rewards"]),
    lname.lantern_chest: AWLocationData(["Toys"]),
    lname.uv_lantern_chest: AWLocationData(["Toys"]),
    lname.b_ball_chest: AWLocationData(["Toys"]),
    lname.remote_chest: AWLocationData(["Toys"]),
    lname.wheel_chest: AWLocationData(["Toys"]),

    lname.mock_disc_chest: AWLocationData(["Toys"]),
    lname.fanny_pack_chest: AWLocationData(["Toys"]),

    lname.match_start_ceiling: AWLocationData(["Matches"]),
    lname.match_fish_mural: AWLocationData(["Matches"]),
    lname.match_dog_switch_bounce: AWLocationData(["Matches"]),
    lname.match_dog_upper_east: AWLocationData(["Matches"]),
    lname.match_bear: AWLocationData(["Matches"]),
    lname.match_above_egg_room: AWLocationData(["Matches"]),
    lname.match_center_well: AWLocationData(["Matches"]),
    lname.match_guard_room: AWLocationData(["Matches"]),
    lname.match_under_mouse_statue: AWLocationData(["Matches"]),

    lname.key_bear_lower: AWLocationData(["Keys"]),
    lname.key_bear_upper: AWLocationData(["Keys"]),
    lname.key_chest_mouse_head_lever: AWLocationData(["Keys"]),
    lname.key_frog_guard_room_west: AWLocationData(["Keys"]),
    lname.key_frog_guard_room_east: AWLocationData(["Keys"]),
    lname.key_dog: AWLocationData(["Keys"]),
    lname.key_house: AWLocationData(["Keys"]),
    lname.key_office: AWLocationData(["Keys"]),

    lname.medal_e: AWLocationData(["Keys", "Medals"]),
    lname.medal_s: AWLocationData(["Keys", "Medals"]),
    lname.medal_k: AWLocationData(["Keys", "Medals"]),

    lname.flame_blue: AWLocationData(["Flames"]),
    lname.flame_green: AWLocationData(["Flames"]),
    lname.flame_violet: AWLocationData(["Flames"]),
    lname.flame_pink: AWLocationData(["Flames"]),

    # eggs, sorted by row top-to-bottom
    lname.egg_reference: AWLocationData(["Eggs"]),
    lname.egg_brown: AWLocationData(["Eggs"]),
    lname.egg_raw: AWLocationData(["Eggs"]),
    lname.egg_pickled: AWLocationData(["Eggs"]),
    lname.egg_big: AWLocationData(["Eggs"]),
    lname.egg_swan: AWLocationData(["Eggs"]),
    lname.egg_forbidden: AWLocationData(["Eggs"]),
    lname.egg_shadow: AWLocationData(["Eggs"]),
    lname.egg_vanity: AWLocationData(["Eggs"]),
    lname.egg_service: AWLocationData(["Eggs"]),

    lname.egg_depraved: AWLocationData(["Eggs"]),
    lname.egg_chaos: AWLocationData(["Eggs"]),
    lname.egg_upside_down: AWLocationData(["Eggs"]),
    lname.egg_evil: AWLocationData(["Eggs"]),
    lname.egg_sweet: AWLocationData(["Eggs"]),
    lname.egg_chocolate: AWLocationData(["Eggs"]),
    lname.egg_value: AWLocationData(["Eggs"]),
    lname.egg_plant: AWLocationData(["Eggs"]),
    lname.egg_red: AWLocationData(["Eggs"]),
    lname.egg_orange: AWLocationData(["Eggs"]),
    lname.egg_sour: AWLocationData(["Eggs"]),
    lname.egg_post_modern: AWLocationData(["Eggs"]),

    lname.egg_universal: AWLocationData(["Eggs"]),
    lname.egg_lf: AWLocationData(["Eggs"]),
    lname.egg_zen: AWLocationData(["Eggs"]),
    lname.egg_future: AWLocationData(["Eggs"]),
    lname.egg_friendship: AWLocationData(["Eggs"]),
    lname.egg_truth: AWLocationData(["Eggs"]),
    lname.egg_transcendental: AWLocationData(["Eggs"]),
    lname.egg_ancient: AWLocationData(["Eggs"]),
    lname.egg_magic: AWLocationData(["Eggs"]),
    lname.egg_mystic: AWLocationData(["Eggs"]),
    lname.egg_holiday: AWLocationData(["Eggs"]),
    lname.egg_rain: AWLocationData(["Eggs"]),
    lname.egg_razzle: AWLocationData(["Eggs"]),
    lname.egg_dazzle: AWLocationData(["Eggs"]),

    lname.egg_virtual: AWLocationData(["Eggs"]),
    lname.egg_normal: AWLocationData(["Eggs"]),
    lname.egg_great: AWLocationData(["Eggs"]),
    lname.egg_gorgeous: AWLocationData(["Eggs"]),
    lname.egg_planet: AWLocationData(["Eggs"]),
    lname.egg_moon: AWLocationData(["Eggs"]),
    lname.egg_galaxy: AWLocationData(["Eggs"]),
    lname.egg_sunset: AWLocationData(["Eggs"]),
    lname.egg_goodnight: AWLocationData(["Eggs"]),
    lname.egg_dream: AWLocationData(["Eggs"]),
    lname.egg_travel: AWLocationData(["Eggs"]),
    lname.egg_promise: AWLocationData(["Eggs"]),
    lname.egg_ice: AWLocationData(["Eggs"]),
    lname.egg_fire: AWLocationData(["Eggs"]),

    lname.egg_bubble: AWLocationData(["Eggs"]),
    lname.egg_desert: AWLocationData(["Eggs"]),
    lname.egg_clover: AWLocationData(["Eggs"]),
    lname.egg_brick: AWLocationData(["Eggs"]),
    lname.egg_neon: AWLocationData(["Eggs"]),
    lname.egg_iridescent: AWLocationData(["Eggs"]),
    lname.egg_rust: AWLocationData(["Eggs"]),
    lname.egg_scarlet: AWLocationData(["Eggs"]),
    lname.egg_sapphire: AWLocationData(["Eggs"]),
    lname.egg_ruby: AWLocationData(["Eggs"]),
    lname.egg_jade: AWLocationData(["Eggs"]),
    lname.egg_obsidian: AWLocationData(["Eggs"]),
    lname.egg_crystal: AWLocationData(["Eggs"]),
    lname.egg_golden: AWLocationData(["Eggs"]),

    lname.egg_65: AWLocationData(["Eggs", "Egg Rewards"]),

    # map things
    lname.map_chest: AWLocationData(["Map Items"]),
    lname.stamp_chest: AWLocationData(["Map Items"]),
    lname.pencil_chest: AWLocationData(["Map Items", "Egg Rewards"]),

    # bnnnnuyuy
    lname.bunny_barcode: AWLocationData(["Bunnies"]),
    lname.bunny_chinchilla_vine: AWLocationData(["Bunnies"]),
    lname.bunny_crow: AWLocationData(["Bunnies"]),
    lname.bunny_disc_spike: AWLocationData(["Bunnies"]),
    lname.bunny_dream: AWLocationData(["Bunnies"]),
    lname.bunny_duck: AWLocationData(["Bunnies"]),
    lname.bunny_face: AWLocationData(["Bunnies"]),
    lname.bunny_file_bud: AWLocationData(["Bunnies"]),
    lname.bunny_fish: AWLocationData(["Bunnies"]),
    lname.bunny_ghost_dog: AWLocationData(["Bunnies"]),
    lname.bunny_lava: AWLocationData(["Bunnies"]),
    lname.bunny_map: AWLocationData(["Bunnies"]),
    lname.bunny_mural: AWLocationData(["Bunnies"]),
    lname.bunny_tv: AWLocationData(["Bunnies"]),
    lname.bunny_uv: AWLocationData(["Bunnies"]),
    lname.bunny_water_spike: AWLocationData(["Bunnies"]),

    # candles
    # lname.candle_first: AWLocationData(["Candles"]),
    # lname.candle_dog_dark: AWLocationData(["Candles"]),
    # lname.candle_dog_switch_box: AWLocationData(["Candles"]),
    # lname.candle_dog_many_switches: AWLocationData(["Candles"]),
    # lname.candle_dog_disc_switches: AWLocationData(["Candles"]),
    # lname.candle_dog_bat: AWLocationData(["Candles"]),
    # lname.candle_fish: AWLocationData(["Candles"]),
    # lname.candle_frog: AWLocationData(["Candles"]),
    # lname.candle_bear: AWLocationData(["Candles"]),

    # extras
    # lname.mama_cha: AWLocationData(),
    # lname.squirrel_acorn: AWLocationData(),
    # kangaroo medal drops
}

location_name_to_id: Dict[str, int] = {name: location_base_id + index for index, name in enumerate(location_table)}

location_name_groups: Dict[str, Set[str]] = {}
for loc_name, loc_data in location_table.items():
    for location_group in loc_data.location_groups:
        location_name_groups.setdefault(location_group, set()).add(loc_name)
