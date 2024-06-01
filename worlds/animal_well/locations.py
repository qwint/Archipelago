from typing import Dict, NamedTuple, Set, List
from .names import LocationNames as lname


class AWLocationData(NamedTuple):
    offset: int
    location_groups: List[str] = []


location_base_id = 11553377
# todo: add location groups for general regions
location_table: Dict[str, AWLocationData] = {
    # major items
    lname.b_wand_chest.value: AWLocationData(0, ["Toys"]),
    lname.bb_wand_chest.value: AWLocationData(1, ["Toys"]),
    lname.disc_spot.value: AWLocationData(2, ["Toys"]),
    lname.yoyo_chest.value: AWLocationData(3, ["Toys"]),
    lname.slink_chest.value: AWLocationData(4, ["Toys"]),
    lname.flute_chest.value: AWLocationData(5, ["Toys", "Egg Rewards"]),
    lname.top_chest.value: AWLocationData(6, ["Toys", "Egg Rewards"]),
    lname.lantern_chest.value: AWLocationData(7, ["Toys"]),
    lname.uv_lantern_chest.value: AWLocationData(8, ["Toys"]),
    lname.b_ball_chest.value: AWLocationData(9, ["Toys"]),
    lname.remote_chest.value: AWLocationData(10, ["Toys"]),
    lname.wheel_chest.value: AWLocationData(11, ["Toys"]),

    lname.mock_disc_chest.value: AWLocationData(12, ["Toys"]),
    lname.fanny_pack_chest.value: AWLocationData(13, ["Toys"]),

    lname.match_start_ceiling.value: AWLocationData(14, ["Matches"]),
    lname.match_fish_mural.value: AWLocationData(15, ["Matches"]),
    lname.match_dog_switch_bounce.value: AWLocationData(16, ["Matches"]),
    lname.match_dog_upper_east.value: AWLocationData(17, ["Matches"]),
    lname.match_bear.value: AWLocationData(18, ["Matches"]),
    lname.match_above_egg_room.value: AWLocationData(19, ["Matches"]),
    lname.match_center_well.value: AWLocationData(20, ["Matches"]),
    lname.match_guard_room.value: AWLocationData(21, ["Matches"]),
    lname.match_under_mouse_statue.value: AWLocationData(22, ["Matches"]),

    lname.key_bear_lower.value: AWLocationData(23, ["Keys"]),
    lname.key_bear_upper.value: AWLocationData(24, ["Keys"]),
    lname.key_chest_mouse_head_lever.value: AWLocationData(25, ["Keys"]),
    lname.key_frog_guard_room_west.value: AWLocationData(26, ["Keys"]),
    lname.key_frog_guard_room_east.value: AWLocationData(27, ["Keys"]),
    lname.key_dog.value: AWLocationData(28, ["Keys"]),
    lname.key_house.value: AWLocationData(29, ["Keys"]),
    lname.key_office.value: AWLocationData(30, ["Keys"]),

    lname.medal_e.value: AWLocationData(31, ["Keys", "Medals"]),
    lname.medal_s.value: AWLocationData(32, ["Keys", "Medals"]),
    # lname.medal_k.value: AWLocationData(33, ["Keys", "Medals"]),

    # event only for now until modding tools maybe
    lname.flame_blue.value: AWLocationData(34, ["Flames"]),
    lname.flame_green.value: AWLocationData(35, ["Flames"]),
    lname.flame_violet.value: AWLocationData(36, ["Flames"]),
    lname.flame_pink.value: AWLocationData(37, ["Flames"]),

    # eggs, sorted by row top-to-bottom
    lname.egg_reference.value: AWLocationData(38, ["Eggs"]),
    lname.egg_brown.value: AWLocationData(39, ["Eggs"]),
    lname.egg_raw.value: AWLocationData(40, ["Eggs"]),
    lname.egg_pickled.value: AWLocationData(41, ["Eggs"]),
    lname.egg_big.value: AWLocationData(42, ["Eggs"]),
    lname.egg_swan.value: AWLocationData(43, ["Eggs"]),
    lname.egg_forbidden.value: AWLocationData(44, ["Eggs"]),
    lname.egg_shadow.value: AWLocationData(45, ["Eggs"]),
    lname.egg_vanity.value: AWLocationData(46, ["Eggs"]),
    lname.egg_service.value: AWLocationData(47, ["Eggs"]),

    lname.egg_depraved.value: AWLocationData(48, ["Eggs"]),
    lname.egg_chaos.value: AWLocationData(49, ["Eggs"]),
    lname.egg_upside_down.value: AWLocationData(50, ["Eggs"]),
    lname.egg_evil.value: AWLocationData(51, ["Eggs"]),
    lname.egg_sweet.value: AWLocationData(52, ["Eggs"]),
    lname.egg_chocolate.value: AWLocationData(53, ["Eggs"]),
    lname.egg_value.value: AWLocationData(54, ["Eggs"]),
    lname.egg_plant.value: AWLocationData(55, ["Eggs"]),
    lname.egg_red.value: AWLocationData(56, ["Eggs"]),
    lname.egg_orange.value: AWLocationData(57, ["Eggs"]),
    lname.egg_sour.value: AWLocationData(58, ["Eggs"]),
    lname.egg_post_modern.value: AWLocationData(59, ["Eggs"]),

    lname.egg_universal.value: AWLocationData(60, ["Eggs"]),
    lname.egg_lf.value: AWLocationData(61, ["Eggs"]),
    lname.egg_zen.value: AWLocationData(62, ["Eggs"]),
    lname.egg_future.value: AWLocationData(63, ["Eggs"]),
    lname.egg_friendship.value: AWLocationData(64, ["Eggs"]),
    lname.egg_truth.value: AWLocationData(65, ["Eggs"]),
    lname.egg_transcendental.value: AWLocationData(66, ["Eggs"]),
    lname.egg_ancient.value: AWLocationData(67, ["Eggs"]),
    lname.egg_magic.value: AWLocationData(68, ["Eggs"]),
    lname.egg_mystic.value: AWLocationData(69, ["Eggs"]),
    lname.egg_holiday.value: AWLocationData(70, ["Eggs"]),
    lname.egg_rain.value: AWLocationData(71, ["Eggs"]),
    lname.egg_razzle.value: AWLocationData(72, ["Eggs"]),
    lname.egg_dazzle.value: AWLocationData(73, ["Eggs"]),

    lname.egg_virtual.value: AWLocationData(74, ["Eggs"]),
    lname.egg_normal.value: AWLocationData(75, ["Eggs"]),
    lname.egg_great.value: AWLocationData(76, ["Eggs"]),
    lname.egg_gorgeous.value: AWLocationData(77, ["Eggs"]),
    lname.egg_planet.value: AWLocationData(78, ["Eggs"]),
    lname.egg_moon.value: AWLocationData(79, ["Eggs"]),
    lname.egg_galaxy.value: AWLocationData(80, ["Eggs"]),
    lname.egg_sunset.value: AWLocationData(81, ["Eggs"]),
    lname.egg_goodnight.value: AWLocationData(82, ["Eggs"]),
    lname.egg_dream.value: AWLocationData(83, ["Eggs"]),
    lname.egg_travel.value: AWLocationData(84, ["Eggs"]),
    lname.egg_promise.value: AWLocationData(85, ["Eggs"]),
    lname.egg_ice.value: AWLocationData(86, ["Eggs"]),
    lname.egg_fire.value: AWLocationData(87, ["Eggs"]),

    lname.egg_bubble.value: AWLocationData(88, ["Eggs"]),
    lname.egg_desert.value: AWLocationData(89, ["Eggs"]),
    lname.egg_clover.value: AWLocationData(90, ["Eggs"]),
    lname.egg_brick.value: AWLocationData(91, ["Eggs"]),
    lname.egg_neon.value: AWLocationData(92, ["Eggs"]),
    lname.egg_iridescent.value: AWLocationData(93, ["Eggs"]),
    lname.egg_rust.value: AWLocationData(94, ["Eggs"]),
    lname.egg_scarlet.value: AWLocationData(95, ["Eggs"]),
    lname.egg_sapphire.value: AWLocationData(96, ["Eggs"]),
    lname.egg_ruby.value: AWLocationData(97, ["Eggs"]),
    lname.egg_jade.value: AWLocationData(98, ["Eggs"]),
    lname.egg_obsidian.value: AWLocationData(99, ["Eggs"]),
    lname.egg_crystal.value: AWLocationData(100, ["Eggs"]),
    lname.egg_golden.value: AWLocationData(101, ["Eggs"]),

    lname.egg_65.value: AWLocationData(102, ["Eggs", "Egg Rewards"]),

    # map things
    lname.map_chest.value: AWLocationData(103, []),
    lname.stamp_chest.value: AWLocationData(104, []),
    lname.pencil_chest.value: AWLocationData(105, ["Egg Rewards"]),

    # bnnnnuyuy - commented until modding tools
    lname.bunny_mural.value: AWLocationData(106, ["Bunnies"]),
    lname.bunny_chinchilla_vine.value: AWLocationData(107, ["Bunnies"]),
    lname.bunny_water_spike.value: AWLocationData(108, ["Bunnies"]),
    lname.bunny_map.value: AWLocationData(109, ["Bunnies"]),
    lname.bunny_uv.value: AWLocationData(110, ["Bunnies"]),
    lname.bunny_fish.value: AWLocationData(111, ["Bunnies"]),
    lname.bunny_face.value: AWLocationData(112, ["Bunnies"]),
    lname.bunny_crow.value: AWLocationData(113, ["Bunnies"]),
    lname.bunny_duck.value: AWLocationData(114, ["Bunnies"]),
    lname.bunny_dream.value: AWLocationData(115, ["Bunnies"]),
    lname.bunny_file_bud.value: AWLocationData(116, ["Bunnies"]),
    lname.bunny_lava.value: AWLocationData(117, ["Bunnies"]),
    lname.bunny_tv.value: AWLocationData(118, ["Bunnies"]),
    lname.bunny_barcode.value: AWLocationData(119, ["Bunnies"]),
    lname.bunny_ghost_dog.value: AWLocationData(120, ["Bunnies"]),
    lname.bunny_disc_spike.value: AWLocationData(121, ["Bunnies"]),

    # candles - commented until modding tools
    lname.candle_first.value: AWLocationData(122, ["Candles"]),
    lname.candle_dog_dark.value: AWLocationData(123, ["Candles"]),
    lname.candle_dog_switch_box.value: AWLocationData(124, ["Candles"]),
    lname.candle_dog_many_switches.value: AWLocationData(125, ["Candles"]),
    lname.candle_dog_disc_switches.value: AWLocationData(126, ["Candles"]),
    lname.candle_dog_bat.value: AWLocationData(127, ["Candles"]),
    lname.candle_fish.value: AWLocationData(128, ["Candles"]),
    lname.candle_frog.value: AWLocationData(129, ["Candles"]),
    lname.candle_bear.value: AWLocationData(130, ["Candles"]),

    # extras
    lname.mama_cha.value: AWLocationData(131, []),
}

location_name_to_id: Dict[str, int] = {name: location_base_id + index for index, name in enumerate(location_table)}

location_name_groups: Dict[str, Set[str]] = {}
for loc_name, loc_data in location_table.items():
    for location_group in loc_data.location_groups:
        location_name_groups.setdefault(location_group, set()).add(loc_name)
