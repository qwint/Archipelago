from typing import Dict, NamedTuple, Set, List
from .names import LocationNames as lname


class AWLocationData(NamedTuple):
    location_groups: List[str] = []


location_base_id = 11553377

location_table: Dict[str, AWLocationData] = {
    # major items
    lname.b_wand_chest.value: AWLocationData(["Toys"]),
    lname.bb_wand_chest.value: AWLocationData(["Toys"]),
    lname.disc_spot.value: AWLocationData(["Toys"]),
    lname.yoyo_chest.value: AWLocationData(["Toys"]),
    lname.slink_chest.value: AWLocationData(["Toys"]),
    lname.flute_chest.value: AWLocationData(["Toys", "Egg Rewards"]),
    lname.top_chest.value: AWLocationData(["Toys", "Egg Rewards"]),
    lname.lantern_chest.value: AWLocationData(["Toys"]),
    lname.uv_lantern_chest.value: AWLocationData(["Toys"]),
    lname.b_ball_chest.value: AWLocationData(["Toys"]),
    lname.remote_chest.value: AWLocationData(["Toys"]),
    lname.wheel_chest.value: AWLocationData(["Toys"]),

    lname.mock_disc_chest.value: AWLocationData(["Toys"]),
    lname.fanny_pack_chest.value: AWLocationData(["Toys"]),

    lname.match_start_ceiling.value: AWLocationData(["Matches"]),
    lname.match_fish_mural.value: AWLocationData(["Matches"]),
    lname.match_dog_switch_bounce.value: AWLocationData(["Matches"]),
    lname.match_dog_upper_east.value: AWLocationData(["Matches"]),
    lname.match_bear.value: AWLocationData(["Matches"]),
    lname.match_above_egg_room.value: AWLocationData(["Matches"]),
    lname.match_center_well.value: AWLocationData(["Matches"]),
    lname.match_guard_room.value: AWLocationData(["Matches"]),
    lname.match_under_mouse_statue.value: AWLocationData(["Matches"]),

    lname.key_bear_lower.value: AWLocationData(["Keys"]),
    lname.key_bear_upper.value: AWLocationData(["Keys"]),
    lname.key_chest_mouse_head_lever.value: AWLocationData(["Keys"]),
    lname.key_frog_guard_room_west.value: AWLocationData(["Keys"]),
    lname.key_frog_guard_room_east.value: AWLocationData(["Keys"]),
    lname.key_dog.value: AWLocationData(["Keys"]),
    lname.key_house.value: AWLocationData(["Keys"]),
    lname.key_office.value: AWLocationData(["Keys"]),

    lname.medal_e.value: AWLocationData(["Keys", "Medals"]),
    lname.medal_s.value: AWLocationData(["Keys", "Medals"]),
    lname.medal_k.value: AWLocationData(["Keys", "Medals"]),

    lname.flame_blue.value: AWLocationData(["Flames"]),
    lname.flame_green.value: AWLocationData(["Flames"]),
    lname.flame_violet.value: AWLocationData(["Flames"]),
    lname.flame_pink.value: AWLocationData(["Flames"]),

    # eggs, sorted by row top-to-bottom
    lname.egg_reference.value: AWLocationData(["Eggs"]),
    lname.egg_brown.value: AWLocationData(["Eggs"]),
    lname.egg_raw.value: AWLocationData(["Eggs"]),
    lname.egg_pickled.value: AWLocationData(["Eggs"]),
    lname.egg_big.value: AWLocationData(["Eggs"]),
    lname.egg_swan.value: AWLocationData(["Eggs"]),
    lname.egg_forbidden.value: AWLocationData(["Eggs"]),
    lname.egg_shadow.value: AWLocationData(["Eggs"]),
    lname.egg_vanity.value: AWLocationData(["Eggs"]),
    lname.egg_service.value: AWLocationData(["Eggs"]),

    lname.egg_depraved.value: AWLocationData(["Eggs"]),
    lname.egg_chaos.value: AWLocationData(["Eggs"]),
    lname.egg_upside_down.value: AWLocationData(["Eggs"]),
    lname.egg_evil.value: AWLocationData(["Eggs"]),
    lname.egg_sweet.value: AWLocationData(["Eggs"]),
    lname.egg_chocolate.value: AWLocationData(["Eggs"]),
    lname.egg_value.value: AWLocationData(["Eggs"]),
    lname.egg_plant.value: AWLocationData(["Eggs"]),
    lname.egg_red.value: AWLocationData(["Eggs"]),
    lname.egg_orange.value: AWLocationData(["Eggs"]),
    lname.egg_sour.value: AWLocationData(["Eggs"]),
    lname.egg_post_modern.value: AWLocationData(["Eggs"]),

    lname.egg_universal.value: AWLocationData(["Eggs"]),
    lname.egg_lf.value: AWLocationData(["Eggs"]),
    lname.egg_zen.value: AWLocationData(["Eggs"]),
    lname.egg_future.value: AWLocationData(["Eggs"]),
    lname.egg_friendship.value: AWLocationData(["Eggs"]),
    lname.egg_truth.value: AWLocationData(["Eggs"]),
    lname.egg_transcendental.value: AWLocationData(["Eggs"]),
    lname.egg_ancient.value: AWLocationData(["Eggs"]),
    lname.egg_magic.value: AWLocationData(["Eggs"]),
    lname.egg_mystic.value: AWLocationData(["Eggs"]),
    lname.egg_holiday.value: AWLocationData(["Eggs"]),
    lname.egg_rain.value: AWLocationData(["Eggs"]),
    lname.egg_razzle.value: AWLocationData(["Eggs"]),
    lname.egg_dazzle.value: AWLocationData(["Eggs"]),

    lname.egg_virtual.value: AWLocationData(["Eggs"]),
    lname.egg_normal.value: AWLocationData(["Eggs"]),
    lname.egg_great.value: AWLocationData(["Eggs"]),
    lname.egg_gorgeous.value: AWLocationData(["Eggs"]),
    lname.egg_planet.value: AWLocationData(["Eggs"]),
    lname.egg_moon.value: AWLocationData(["Eggs"]),
    lname.egg_galaxy.value: AWLocationData(["Eggs"]),
    lname.egg_sunset.value: AWLocationData(["Eggs"]),
    lname.egg_goodnight.value: AWLocationData(["Eggs"]),
    lname.egg_dream.value: AWLocationData(["Eggs"]),
    lname.egg_travel.value: AWLocationData(["Eggs"]),
    lname.egg_promise.value: AWLocationData(["Eggs"]),
    lname.egg_ice.value: AWLocationData(["Eggs"]),
    lname.egg_fire.value: AWLocationData(["Eggs"]),

    lname.egg_bubble.value: AWLocationData(["Eggs"]),
    lname.egg_desert.value: AWLocationData(["Eggs"]),
    lname.egg_clover.value: AWLocationData(["Eggs"]),
    lname.egg_brick.value: AWLocationData(["Eggs"]),
    lname.egg_neon.value: AWLocationData(["Eggs"]),
    lname.egg_iridescent.value: AWLocationData(["Eggs"]),
    lname.egg_rust.value: AWLocationData(["Eggs"]),
    lname.egg_scarlet.value: AWLocationData(["Eggs"]),
    lname.egg_sapphire.value: AWLocationData(["Eggs"]),
    lname.egg_ruby.value: AWLocationData(["Eggs"]),
    lname.egg_jade.value: AWLocationData(["Eggs"]),
    lname.egg_obsidian.value: AWLocationData(["Eggs"]),
    lname.egg_crystal.value: AWLocationData(["Eggs"]),
    lname.egg_golden.value: AWLocationData(["Eggs"]),

    lname.egg_65.value: AWLocationData(["Eggs", "Egg Rewards"]),

    # map things
    lname.map_chest.value: AWLocationData(["Map Items"]),
    lname.stamp_chest.value: AWLocationData(["Map Items"]),
    lname.pencil_chest.value: AWLocationData(["Map Items", "Egg Rewards"]),

    # bnnnnuyuy
    lname.bunny_mural.value: AWLocationData(["Bunnies"]),
    lname.bunny_chinchilla_vine.value: AWLocationData(["Bunnies"]),
    lname.bunny_water_spike.value: AWLocationData(["Bunnies"]),
    lname.bunny_map.value: AWLocationData(["Bunnies"]),
    lname.bunny_uv.value: AWLocationData(["Bunnies"]),
    lname.bunny_fish.value: AWLocationData(["Bunnies"]),
    lname.bunny_face.value: AWLocationData(["Bunnies"]),
    lname.bunny_crow.value: AWLocationData(["Bunnies"]),
    lname.bunny_duck.value: AWLocationData(["Bunnies"]),
    lname.bunny_dream.value: AWLocationData(["Bunnies"]),
    lname.bunny_file_bud.value: AWLocationData(["Bunnies"]),
    lname.bunny_lava.value: AWLocationData(["Bunnies"]),
    lname.bunny_tv.value: AWLocationData(["Bunnies"]),
    lname.bunny_barcode.value: AWLocationData(["Bunnies"]),
    lname.bunny_ghost_dog.value: AWLocationData(["Bunnies"]),
    lname.bunny_disc_spike.value: AWLocationData(["Bunnies"]),

    # candles
    lname.candle_first.value: AWLocationData(["Candles"]),
    lname.candle_dog_dark.value: AWLocationData(["Candles"]),
    lname.candle_dog_switch_box.value: AWLocationData(["Candles"]),
    lname.candle_dog_many_switches.value: AWLocationData(["Candles"]),
    lname.candle_dog_disc_switches.value: AWLocationData(["Candles"]),
    lname.candle_dog_bat.value: AWLocationData(["Candles"]),
    lname.candle_fish.value: AWLocationData(["Candles"]),
    lname.candle_frog.value: AWLocationData(["Candles"]),
    lname.candle_bear.value: AWLocationData(["Candles"]),

    # extras
    # lname.mama_cha.value: AWLocationData(),
    # lname.squirrel_acorn.value: AWLocationData(),
    # kangaroo medal drops
}

location_name_to_id: Dict[str, int] = {name: location_base_id + index for index, name in enumerate(location_table)}

location_name_groups: Dict[str, Set[str]] = {}
for loc_name, loc_data in location_table.items():
    for location_group in loc_data.location_groups:
        location_name_groups.setdefault(location_group, set()).add(loc_name)
