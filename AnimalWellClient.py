"""
Animal Well Archipelago Client
Based (read: copied almost wholesale and edited) off the Zelda1 Client.
"""

import asyncio
import ctypes
import os
import platform
import struct
import subprocess

import Utils
from CommonClient import CommonContext, server_loop, gui_enabled, ClientCommandProcessor, logger, get_base_parser
from worlds.animal_well.names import ItemNames as iname
from worlds.animal_well.names import LocationNames as lname

CONNECTION_REFUSED_STATUS = "Connection Refused. Please make sure exactly one Animal Well instance is running"
CONNECTION_RESET_STATUS = "Connection was reset. Please wait"
CONNECTION_TENTATIVE_STATUS = "Initial Connection Made"
CONNECTION_CONNECTED_STATUS = "Connected"
CONNECTION_INITIAL_STATUS = "Connection has not been initiated"


class AWLocations:
    """
    The checks the player has found
    """

    def __init__(self):
        # major items
        self.b_wand_chest = False
        self.bb_wand_chest = False
        self.disc_spot = False  # TODO disc logic
        self.yoyo_chest = False
        self.slink_chest = False
        self.flute_chest = False
        self.top_chest = False
        self.lantern_chest = False
        self.uv_lantern_chest = False
        self.b_ball_chest = False
        self.remote_chest = False
        self.wheel_chest = False

        self.mock_disc_chest = False  # TODO possession logic
        self.fanny_pack_chest = False

        self.match_start_ceiling = False
        self.match_fish_mural = False
        self.match_dog_switch_bounce = False
        self.match_dog_upper_east = False
        self.match_bear = False
        self.match_above_egg_room = False
        self.match_center_well = False
        self.match_guard_room = False
        self.match_under_mouse_statue = False

        self.key_bear_lower = False  # TODO find out how many doors have been unlocked
        self.key_bear_upper = False  # TODO find out how many doors have been unlocked
        self.key_chest_mouse_head_lever = False  # TODO find out how many doors have been unlocked
        self.key_frog_guard_room_west = False  # TODO find out how many doors have been unlocked
        self.key_frog_guard_room_east = False  # TODO find out how many doors have been unlocked
        self.key_dog = False  # TODO find out how many doors have been unlocked
        self.key_house = False  # TODO house key logic
        self.key_office = False  # TODO office key logic

        self.medal_e = False
        self.medal_s = False
        self.medal_k = False  # TODO K shard logic

        self.flame_blue = False  # TODO flame logic
        self.flame_green = False  # TODO flame logic
        self.flame_violet = False  # TODO flame logic
        self.flame_pink = False  # TODO flame logic

        # eggs, sorted by row top-to-bottom
        self.egg_reference = False
        self.egg_brown = False
        self.egg_raw = False
        self.egg_pickled = False
        self.egg_big = False
        self.egg_swan = False
        self.egg_forbidden = False
        self.egg_shadow = False
        self.egg_vanity = False
        self.egg_service = False

        self.egg_depraved = False
        self.egg_chaos = False
        self.egg_upside_down = False
        self.egg_evil = False
        self.egg_sweet = False
        self.egg_chocolate = False
        self.egg_value = False
        self.egg_plant = False
        self.egg_red = False
        self.egg_orange = False
        self.egg_sour = False
        self.egg_post_modern = False

        self.egg_universal = False
        self.egg_lf = False
        self.egg_zen = False
        self.egg_future = False
        self.egg_friendship = False
        self.egg_truth = False
        self.egg_transcendental = False
        self.egg_ancient = False
        self.egg_magic = False
        self.egg_mystic = False
        self.egg_holiday = False
        self.egg_rain = False
        self.egg_razzle = False
        self.egg_dazzle = False

        self.egg_virtual = False
        self.egg_normal = False
        self.egg_great = False
        self.egg_gorgeous = False
        self.egg_planet = False
        self.egg_moon = False
        self.egg_galaxy = False
        self.egg_sunset = False
        self.egg_goodnight = False
        self.egg_dream = False
        self.egg_travel = False
        self.egg_promise = False
        self.egg_ice = False
        self.egg_fire = False

        self.egg_bubble = False
        self.egg_desert = False
        self.egg_clover = False
        self.egg_brick = False
        self.egg_neon = False
        self.egg_iridescent = False
        self.egg_rust = False
        self.egg_scarlet = False
        self.egg_sapphire = False
        self.egg_ruby = False
        self.egg_jade = False
        self.egg_obsidian = False
        self.egg_crystal = False
        self.egg_golden = False

        self.egg_65 = False

        # map things
        self.map_chest = False  # TODO map things logic
        self.stamp_chest = False  # TODO map things logic
        self.pencil_chest = False  # TODO map things logic

        # bnnnnuyuy
        self.bunny_barcode = False  # TODO bunny logic
        self.bunny_chinchilla_vine = False  # TODO bunny logic
        self.bunny_crow = False  # TODO bunny logic
        self.bunny_disc_spike = False  # TODO bunny logic
        self.bunny_dream = False  # TODO bunny logic
        self.bunny_duck = False  # TODO bunny logic
        self.bunny_face = False  # TODO bunny logic
        self.bunny_file_bud = False  # TODO bunny logic
        self.bunny_fish = False  # TODO bunny logic
        self.bunny_ghost_dog = False  # TODO bunny logic
        self.bunny_lava = False  # TODO bunny logic
        self.bunny_map = False  # TODO bunny logic
        self.bunny_mural = False  # TODO bunny logic
        self.bunny_tv = False  # TODO bunny logic
        self.bunny_uv = False  # TODO bunny logic
        self.bunny_water_spike = False  # TODO bunny logic

        # candles
        self.candle_first = False  # TODO candle logic
        self.candle_dog_dark = False  # TODO candle logic
        self.candle_dog_switch_box = False  # TODO candle logic
        self.candle_dog_many_switches = False  # TODO candle logic
        self.candle_dog_disc_switches = False  # TODO candle logic
        self.candle_dog_bat = False  # TODO candle logic
        self.candle_fish = False  # TODO candle logic
        self.candle_frog = False  # TODO candle logic
        self.candle_bear = False  # TODO candle logic

        # extras
        # self.mama_cha = False
        # self.squirrel_acorn = false
        # kangaroo medal drops

    async def read_from_game(self, process_handle, game_slot, start_address: int):
        """
        Read checked locations from the process
        """
        slot_address = start_address + 0x18 + (0x27010 * game_slot)

        # Read Chests
        buffer_size = 8
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x120, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logger.error("Unable to read Chests")
            return
        flags = bytearray(struct.unpack('Q', buffer)[0].to_bytes(8, byteorder="little"))

        buffer_size = 8
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x128, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logger.error("Unable to read Chests")
            return
        flags.extend(struct.unpack('Q', buffer)[0].to_bytes(8, byteorder="little"))

        flags = int.from_bytes(bytes(flags), byteorder="little")

        self.egg_reference = bool(flags >> 0 & 1)
        self.egg_brown = bool(flags >> 1 & 1)
        self.egg_raw = bool(flags >> 2 & 1)
        self.egg_big = bool(flags >> 3 & 1)
        self.egg_pickled = bool(flags >> 4 & 1)  # TODO VERIFY
        self.egg_swan = bool(flags >> 5 & 1)
        self.egg_forbidden = bool(flags >> 6 & 1)
        self.egg_shadow = bool(flags >> 7 & 1)

        self.egg_vanity = bool(flags >> 8 & 1)
        self.egg_service = bool(flags >> 9 & 1)
        # self.mama_cha = bool(flags >> 10 & 1)  # TODO VERIFY
        self.match_dog_switch_bounce = bool(flags >> 11 & 1)
        self.egg_depraved = bool(flags >> 12 & 1)
        self.match_bear = bool(flags >> 13 & 1)  # TODO VERIFY
        self.egg_chaos = bool(flags >> 14 & 1)
        self.b_ball_chest = bool(flags >> 15 & 1)  # TODO VERIFY

        # self.key_dog = bool(flags >> 16 & 1)  # TODO VERIFY
        self.egg_upside_down = bool(flags >> 17 & 1)  # TODO VERIFY
        self.egg_evil = bool(flags >> 18 & 1)  # TODO VERIFY
        self.match_dog_upper_east = bool(flags >> 19 & 1)
        self.egg_sweet = bool(flags >> 20 & 1)
        self.match_center_well = bool(flags >> 21 & 1)
        self.egg_chocolate = bool(flags >> 22 & 1)
        self.egg_value = bool(flags >> 23 & 1)

        self.egg_plant = bool(flags >> 24 & 1)
        self.egg_red = bool(flags >> 25 & 1)
        self.egg_orange = bool(flags >> 26 & 1)  # TODO VERIFY
        # self.mock_disc_chest = bool(flags >> 27 & 1)  # TODO possession logic VERIFY
        self.egg_sour = bool(flags >> 28 & 1)
        self.egg_post_modern = bool(flags >> 29 & 1)
        self.slink_chest = bool(flags >> 30 & 1)
        self.egg_universal = bool(flags >> 31 & 1)  # TODO VERIFY

        self.egg_lf = bool(flags >> 32 & 1)  # TODO VERIFY
        self.egg_zen = bool(flags >> 33 & 1)
        # self.key_bear_upper = bool(flags >> 34 & 1)  # TODO find out how many doors have been unlocked
        self.egg_future = bool(flags >> 35 & 1)  # TODO VERIFY
        self.egg_friendship = bool(flags >> 36 & 1)
        # self.disc_spot = bool(flags >> 37 & 1)  # TODO VERIFY
        self.match_above_egg_room = bool(flags >> 38 & 1)  # TODO VERIFY
        # self.key_office = bool(flags >> 39 & 1)  # TODO VERIFY

        self.egg_truth = bool(flags >> 40 & 1)  # TODO VERIFY
        self.egg_transcendental = bool(flags >> 41 & 1)  # TODO VERIFY
        self.medal_s = bool(flags >> 42 & 1)  # TODO VERIFY
        self.egg_ancient = bool(flags >> 43 & 1)
        self.egg_magic = bool(flags >> 44 & 1)
        self.egg_mystic = bool(flags >> 45 & 1)
        self.flute_chest = bool(flags >> 46 & 1)  # TODO VERIFY
        self.egg_65 = bool(flags >> 47 & 1)

        # self.stamp_chest = bool(flags >> 48 & 1)  # TODO VERIFY
        # self.pencil_chest = bool(flags >> 49 & 1)  # TODO VERIFY
        self.top_chest = bool(flags >> 50 & 1)  # TODO VERIFY
        self.egg_holiday = bool(flags >> 51 & 1)  # TODO VERIFY
        self.egg_rain = bool(flags >> 52 & 1)  # TODO VERIFY
        self.egg_razzle = bool(flags >> 53 & 1)
        # self.key_bear_lower = bool(flags >> 54 & 1)  # TODO find out how many doors have been unlocked VERIFY
        self.egg_dazzle = bool(flags >> 55 & 1)

        self.match_fish_mural = bool(flags >> 56 & 1)  # TODO VERIFY
        self.egg_virtual = bool(flags >> 57 & 1)
        self.egg_normal = bool(flags >> 58 & 1)
        self.egg_great = bool(flags >> 59 & 1)
        self.egg_gorgeous = bool(flags >> 60 & 1)
        # self.map_chest = bool(flags >> 61 & 1)
        # self.key_chest_mouse_head_lever = bool(flags >> 62 & 1)  # TODO find out how many doors have been unlocked VERIFY
        self.match_under_mouse_statue = bool(flags >> 63 & 1)  # TODO VERIFY

        self.egg_planet = bool(flags >> 64 & 1)  # TODO VERIFY
        self.egg_moon = bool(flags >> 65 & 1)
        self.egg_galaxy = bool(flags >> 66 & 1)
        self.egg_sunset = bool(flags >> 67 & 1)
        self.b_wand_chest = bool(flags >> 68 & 1)
        self.egg_goodnight = bool(flags >> 69 & 1)
        self.match_start_ceiling = bool(flags >> 70 & 1)
        self.egg_dream = bool(flags >> 71 & 1)

        self.egg_travel = bool(flags >> 72 & 1)  # TODO VERIFY
        self.egg_promise = bool(flags >> 73 & 1)
        self.egg_ice = bool(flags >> 74 & 1)
        self.lantern_chest = bool(flags >> 75 & 1)  # TODO VERIFY
        self.egg_fire = bool(flags >> 76 & 1)
        self.egg_bubble = bool(flags >> 77 & 1)
        self.egg_desert = bool(flags >> 78 & 1)
        self.wheel_chest = bool(flags >> 79 & 1)  # TODO VERIFY

        self.egg_clover = bool(flags >> 80 & 1)
        self.match_guard_room = bool(flags >> 81 & 1)  # TODO VERIFY
        # self.key_frog_guard_room_west = bool(flags >> 82 & 1)  # TODO find out how many doors have been unlocked VERIFY
        # self.key_frog_guard_room_east = bool(flags >> 83 & 1)  # TODO find out how many doors have been unlocked VERIFY
        self.egg_brick = bool(flags >> 84 & 1)  # TODO VERIFY
        self.egg_neon = bool(flags >> 85 & 1)  # TODO VERIFY
        self.remote_chest = bool(flags >> 86 & 1)  # TODO VERIFY
        self.egg_iridescent = bool(flags >> 87 & 1)

        self.egg_rust = bool(flags >> 88 & 1)
        self.egg_scarlet = bool(flags >> 89 & 1)  # TODO VERIFY
        self.medal_e = bool(flags >> 90 & 1)  # TODO VERIFY
        self.egg_sapphire = bool(flags >> 91 & 1)
        self.egg_ruby = bool(flags >> 92 & 1)
        self.egg_jade = bool(flags >> 93 & 1)
        self.egg_obsidian = bool(flags >> 94 & 1)
        self.bb_wand_chest = bool(flags >> 95 & 1)  # TODO VERIFY

        self.yoyo_chest = bool(flags >> 96 & 1)  # TODO VERIFY
        self.uv_lantern_chest = bool(flags >> 97 & 1)  # TODO VERIFY
        self.egg_crystal = bool(flags >> 98 & 1)  # TODO VERIFY
        self.fanny_pack_chest = bool(flags >> 99 & 1)  # TODO VERIFY
        self.egg_golden = bool(flags >> 100 & 1)  # TODO VERIFY

    async def write_to_archipelago(self, ctx):
        """
        Write checked locations to archipelago
        """
        # major items
        if self.b_wand_chest: ctx.locations_checked.append(lname.b_wand_chest)
        if self.bb_wand_chest: ctx.locations_checked.append(lname.bb_wand_chest)
        if self.disc_spot: ctx.locations_checked.append(lname.disc_spot)  # TODO disc logic
        if self.yoyo_chest: ctx.locations_checked.append(lname.yoyo_chest)
        if self.slink_chest: ctx.locations_checked.append(lname.slink_chest)
        if self.flute_chest: ctx.locations_checked.append(lname.flute_chest)
        if self.top_chest: ctx.locations_checked.append(lname.top_chest)
        if self.lantern_chest: ctx.locations_checked.append(lname.lantern_chest)
        if self.uv_lantern_chest: ctx.locations_checked.append(lname.uv_lantern_chest)
        if self.b_ball_chest: ctx.locations_checked.append(lname.b_ball_chest)
        if self.remote_chest: ctx.locations_checked.append(lname.remote_chest)
        if self.wheel_chest: ctx.locations_checked.append(lname.wheel_chest)

        if self.mock_disc_chest: ctx.locations_checked.append(lname.mock_disc_chest)  # TODO possession logic
        if self.fanny_pack_chest: ctx.locations_checked.append(lname.fanny_pack_chest)

        if self.match_start_ceiling: ctx.locations_checked.append(lname.match_start_ceiling)
        if self.match_fish_mural: ctx.locations_checked.append(lname.match_fish_mural)
        if self.match_dog_switch_bounce: ctx.locations_checked.append(lname.match_dog_switch_bounce)
        if self.match_dog_upper_east: ctx.locations_checked.append(lname.match_dog_upper_east)
        if self.match_bear: ctx.locations_checked.append(lname.match_bear)
        if self.match_above_egg_room: ctx.locations_checked.append(lname.match_above_egg_room)
        if self.match_center_well: ctx.locations_checked.append(lname.match_center_well)
        if self.match_guard_room: ctx.locations_checked.append(lname.match_guard_room)
        if self.match_under_mouse_statue: ctx.locations_checked.append(lname.match_under_mouse_statue)

        if self.key_bear_lower: ctx.locations_checked.append(
            lname.key_bear_lower)  # TODO find out how many doors have been unlocked
        if self.key_bear_upper: ctx.locations_checked.append(
            lname.key_bear_upper)  # TODO find out how many doors have been unlocked
        if self.key_chest_mouse_head_lever: ctx.locations_checked.append(
            lname.key_chest_mouse_head_lever)  # TODO find out how many doors have been unlocked
        if self.key_frog_guard_room_west: ctx.locations_checked.append(
            lname.key_frog_guard_room_west)  # TODO find out how many doors have been unlocked
        if self.key_frog_guard_room_east: ctx.locations_checked.append(
            lname.key_frog_guard_room_east)  # TODO find out how many doors have been unlocked
        if self.key_dog: ctx.locations_checked.append(lname.key_dog)  # TODO find out how many doors have been unlocked
        if self.key_house: ctx.locations_checked.append(lname.key_house)  # TODO house key logic
        if self.key_office: ctx.locations_checked.append(lname.key_office)  # TODO office key logic

        if self.medal_e: ctx.locations_checked.append(lname.medal_e)
        if self.medal_s: ctx.locations_checked.append(lname.medal_s)
        if self.medal_k: ctx.locations_checked.append(lname.medal_k)  # TODO K shard logic

        if self.flame_blue: ctx.locations_checked.append(lname.flame_blue)  # TODO flame logic
        if self.flame_green: ctx.locations_checked.append(lname.flame_green)  # TODO flame logic
        if self.flame_violet: ctx.locations_checked.append(lname.flame_violet)  # TODO flame logic
        if self.flame_pink: ctx.locations_checked.append(lname.flame_pink)  # TODO flame logic

        # eggs, sorted by row top-to-bottom
        if self.egg_reference: ctx.locations_checked.append(lname.egg_reference)
        if self.egg_brown: ctx.locations_checked.append(lname.egg_brown)
        if self.egg_raw: ctx.locations_checked.append(lname.egg_raw)
        if self.egg_pickled: ctx.locations_checked.append(lname.egg_pickled)
        if self.egg_big: ctx.locations_checked.append(lname.egg_big)
        if self.egg_swan: ctx.locations_checked.append(lname.egg_swan)
        if self.egg_forbidden: ctx.locations_checked.append(lname.egg_forbidden)
        if self.egg_shadow: ctx.locations_checked.append(lname.egg_shadow)
        if self.egg_vanity: ctx.locations_checked.append(lname.egg_vanity)
        if self.egg_service: ctx.locations_checked.append(lname.egg_service)

        if self.egg_depraved: ctx.locations_checked.append(lname.egg_depraved)
        if self.egg_chaos: ctx.locations_checked.append(lname.egg_chaos)
        if self.egg_upside_down: ctx.locations_checked.append(lname.egg_upside_down)
        if self.egg_evil: ctx.locations_checked.append(lname.egg_evil)
        if self.egg_sweet: ctx.locations_checked.append(lname.egg_sweet)
        if self.egg_chocolate: ctx.locations_checked.append(lname.egg_chocolate)
        if self.egg_value: ctx.locations_checked.append(lname.egg_value)
        if self.egg_plant: ctx.locations_checked.append(lname.egg_plant)
        if self.egg_red: ctx.locations_checked.append(lname.egg_red)
        if self.egg_orange: ctx.locations_checked.append(lname.egg_orange)
        if self.egg_sour: ctx.locations_checked.append(lname.egg_sour)
        if self.egg_post_modern: ctx.locations_checked.append(lname.egg_post_modern)

        if self.egg_universal: ctx.locations_checked.append(lname.egg_universal)
        if self.egg_lf: ctx.locations_checked.append(lname.egg_lf)
        if self.egg_zen: ctx.locations_checked.append(lname.egg_zen)
        if self.egg_future: ctx.locations_checked.append(lname.egg_future)
        if self.egg_friendship: ctx.locations_checked.append(lname.egg_friendship)
        if self.egg_truth: ctx.locations_checked.append(lname.egg_truth)
        if self.egg_transcendental: ctx.locations_checked.append(lname.egg_transcendental)
        if self.egg_ancient: ctx.locations_checked.append(lname.egg_ancient)
        if self.egg_magic: ctx.locations_checked.append(lname.egg_magic)
        if self.egg_mystic: ctx.locations_checked.append(lname.egg_mystic)
        if self.egg_holiday: ctx.locations_checked.append(lname.egg_holiday)
        if self.egg_rain: ctx.locations_checked.append(lname.egg_rain)
        if self.egg_razzle: ctx.locations_checked.append(lname.egg_razzle)
        if self.egg_dazzle: ctx.locations_checked.append(lname.egg_dazzle)

        if self.egg_virtual: ctx.locations_checked.append(lname.egg_virtual)
        if self.egg_normal: ctx.locations_checked.append(lname.egg_normal)
        if self.egg_great: ctx.locations_checked.append(lname.egg_great)
        if self.egg_gorgeous: ctx.locations_checked.append(lname.egg_gorgeous)
        if self.egg_planet: ctx.locations_checked.append(lname.egg_planet)
        if self.egg_moon: ctx.locations_checked.append(lname.egg_moon)
        if self.egg_galaxy: ctx.locations_checked.append(lname.egg_galaxy)
        if self.egg_sunset: ctx.locations_checked.append(lname.egg_sunset)
        if self.egg_goodnight: ctx.locations_checked.append(lname.egg_goodnight)
        if self.egg_dream: ctx.locations_checked.append(lname.egg_dream)
        if self.egg_travel: ctx.locations_checked.append(lname.egg_travel)
        if self.egg_promise: ctx.locations_checked.append(lname.egg_promise)
        if self.egg_ice: ctx.locations_checked.append(lname.egg_ice)
        if self.egg_fire: ctx.locations_checked.append(lname.egg_fire)

        if self.egg_bubble: ctx.locations_checked.append(lname.egg_bubble)
        if self.egg_desert: ctx.locations_checked.append(lname.egg_desert)
        if self.egg_clover: ctx.locations_checked.append(lname.egg_clover)
        if self.egg_brick: ctx.locations_checked.append(lname.egg_brick)
        if self.egg_neon: ctx.locations_checked.append(lname.egg_neon)
        if self.egg_iridescent: ctx.locations_checked.append(lname.egg_iridescent)
        if self.egg_rust: ctx.locations_checked.append(lname.egg_rust)
        if self.egg_scarlet: ctx.locations_checked.append(lname.egg_scarlet)
        if self.egg_sapphire: ctx.locations_checked.append(lname.egg_sapphire)
        if self.egg_ruby: ctx.locations_checked.append(lname.egg_ruby)
        if self.egg_jade: ctx.locations_checked.append(lname.egg_jade)
        if self.egg_obsidian: ctx.locations_checked.append(lname.egg_obsidian)
        if self.egg_crystal: ctx.locations_checked.append(lname.egg_crystal)
        if self.egg_golden: ctx.locations_checked.append(lname.egg_golden)

        if self.egg_65: ctx.locations_checked.append(lname.egg_65)

        # map things
        if self.map_chest: ctx.locations_checked.append(lname.map_chest)  # TODO map things logic
        if self.stamp_chest: ctx.locations_checked.append(lname.stamp_chest)  # TODO map things logic
        if self.pencil_chest: ctx.locations_checked.append(lname.pencil_chest)  # TODO map things logic

        # bnnnnuyuy
        if self.bunny_barcode: ctx.locations_checked.append(lname.bunny_barcode)  # TODO bunny logic
        if self.bunny_chinchilla_vine: ctx.locations_checked.append(lname.bunny_chinchilla_vine)  # TODO bunny logic
        if self.bunny_crow: ctx.locations_checked.append(lname.bunny_crow)  # TODO bunny logic
        if self.bunny_disc_spike: ctx.locations_checked.append(lname.bunny_disc_spike)  # TODO bunny logic
        if self.bunny_dream: ctx.locations_checked.append(lname.bunny_dream)  # TODO bunny logic
        if self.bunny_duck: ctx.locations_checked.append(lname.bunny_duck)  # TODO bunny logic
        if self.bunny_face: ctx.locations_checked.append(lname.bunny_face)  # TODO bunny logic
        if self.bunny_file_bud: ctx.locations_checked.append(lname.bunny_file_bud)  # TODO bunny logic
        if self.bunny_fish: ctx.locations_checked.append(lname.bunny_fish)  # TODO bunny logic
        if self.bunny_ghost_dog: ctx.locations_checked.append(lname.bunny_ghost_dog)  # TODO bunny logic
        if self.bunny_lava: ctx.locations_checked.append(lname.bunny_lava)  # TODO bunny logic
        if self.bunny_map: ctx.locations_checked.append(lname.bunny_map)  # TODO bunny logic
        if self.bunny_mural: ctx.locations_checked.append(lname.bunny_mural)  # TODO bunny logic
        if self.bunny_tv: ctx.locations_checked.append(lname.bunny_tv)  # TODO bunny logic
        if self.bunny_uv: ctx.locations_checked.append(lname.bunny_uv)  # TODO bunny logic
        if self.bunny_water_spike: ctx.locations_checked.append(lname.bunny_water_spike)  # TODO bunny logic

        # candles
        if self.candle_first: ctx.locations_checked.append(lname.candle_first)  # TODO candle logic
        if self.candle_dog_dark: ctx.locations_checked.append(lname.candle_dog_dark)  # TODO candle logic
        if self.candle_dog_switch_box: ctx.locations_checked.append(lname.candle_dog_switch_box)  # TODO candle logic
        if self.candle_dog_many_switches: ctx.locations_checked.append(
            lname.candle_dog_many_switches)  # TODO candle logic
        if self.candle_dog_disc_switches: ctx.locations_checked.append(
            lname.candle_dog_disc_switches)  # TODO candle logic
        if self.candle_dog_bat: ctx.locations_checked.append(lname.candle_dog_bat)  # TODO candle logic
        if self.candle_fish: ctx.locations_checked.append(lname.candle_fish)  # TODO candle logic
        if self.candle_frog: ctx.locations_checked.append(lname.candle_frog)  # TODO candle logic
        if self.candle_bear: ctx.locations_checked.append(lname.candle_bear)  # TODO candle logic

        # extras
        # if self.mama_cha: ctx.locations_checked.append(lname.mama_cha)
        # if self.squirrel_acorn: ctx.locations_checked.append(lname.squirrel_acorn)
        # kangaroo medal drops

        # TODO finished_game

        locations_checked = []
        for location in ctx.missing_locations:
            if location in ctx.locations_checked:
                locations_checked.append(location)
        await ctx.send_msgs([
            {"cmd": "LocationChecks",
             "locations": locations_checked}
        ])


class AWItems:
    """
    The items the player has received
    """

    def __init__(self):
        # Major progression items
        self.bubble = 0  # progressive
        # self.disc = False
        self.yoyo = False
        self.slink = False
        self.flute = False
        self.top = False
        self.lantern = False
        self.uv = False
        self.ball = False
        self.remote = False
        self.wheel = False
        self.firecrackers = True

        # Minor progression items and keys
        self.m_disc = False  # TODO possession logic
        self.fanny_pack = False

        self.match = 0
        self.matchbox = False

        self.key = 0  # TODO find out how many doors have been unlocked
        self.key_ring = False
        self.house_key = False
        self.office_key = False

        self.e_medal = False
        self.s_medal = False
        self.k_shard = 0  # TODO K shard logic

        # self.blue_flame = False
        # self.green_flame = False
        # self.violet_flame = False
        # self.pink_flame = False

        # Eggs
        self.egg_reference = False
        self.egg_brown = False
        self.egg_raw = False
        self.egg_pickled = False
        self.egg_big = False
        self.egg_swan = False
        self.egg_forbidden = False
        self.egg_shadow = False
        self.egg_vanity = False
        self.egg_service = False

        self.egg_depraved = False
        self.egg_chaos = False
        self.egg_upside_down = False
        self.egg_evil = False
        self.egg_sweet = False
        self.egg_chocolate = False
        self.egg_value = False
        self.egg_plant = False
        self.egg_red = False
        self.egg_orange = False
        self.egg_sour = False
        self.egg_post_modern = False

        self.egg_universal = False
        self.egg_lf = False
        self.egg_zen = False
        self.egg_future = False
        self.egg_friendship = False
        self.egg_truth = False
        self.egg_transcendental = False
        self.egg_ancient = False
        self.egg_magic = False
        self.egg_mystic = False
        self.egg_holiday = False
        self.egg_rain = False
        self.egg_razzle = False
        self.egg_dazzle = False

        self.egg_virtual = False
        self.egg_normal = False
        self.egg_great = False
        self.egg_gorgeous = False
        self.egg_planet = False
        self.egg_moon = False
        self.egg_galaxy = False
        self.egg_sunset = False
        self.egg_goodnight = False
        self.egg_dream = False
        self.egg_travel = False
        self.egg_promise = False
        self.egg_ice = False
        self.egg_fire = False

        self.egg_bubble = False
        self.egg_desert = False
        self.egg_clover = False
        self.egg_brick = False
        self.egg_neon = False
        self.egg_iridescent = False
        self.egg_rust = False
        self.egg_scarlet = False
        self.egg_sapphire = False
        self.egg_ruby = False
        self.egg_jade = False
        self.egg_obsidian = False
        self.egg_crystal = False
        self.egg_golden = False

        self.egg_65 = False

        self.firecracker_refill = 0  # TODO Fill Logic
        self.big_blue_fruit = 0  # TODO Fill Logic

    async def read_from_archipelago(self, ctx):
        """
        Read inventory state from archipelago
        """
        items = [item.item for item in ctx.items_received]

        # Major progression items
        self.bubble = 0
        if iname.bubble in items: self.bubble += 1
        if iname.bubble_long in items: self.bubble += 1
        # self.disc = iname.disc in items
        self.yoyo = iname.yoyo in items
        self.slink = iname.slink in items
        self.flute = iname.flute in items
        self.top = iname.top in items
        self.lantern = iname.lantern in items
        self.uv = iname.uv in items
        self.ball = iname.ball in items
        self.remote = iname.remote in items
        self.wheel = iname.wheel in items
        self.firecrackers = iname.firecrackers in items

        # Minor progression items and keys
        self.m_disc = iname.m_disc in items  # TODO possession logic
        self.fanny_pack = iname.fanny_pack in items

        self.match = len([item for item in items if item == iname.match])
        self.matchbox = iname.matchbox in items

        self.key = len([item for item in items if item == iname.key])  # TODO find out how many doors have been unlocked
        self.key_ring = iname.key_ring in items
        self.house_key = iname.house_key in items
        self.office_key = iname.office_key in items

        self.e_medal = iname.e_medal in items
        self.s_medal = iname.s_medal in items
        self.k_shard = len([item for item in items if item == iname.k_shard])  # TODO K shard logic

        # self.blue_flame = iname.blue_flame in items
        # self.green_flame = iname.green_flame in items
        # self.violet_flame = iname.violet_flame in items
        # self.pink_flame = iname.pink_flame in items

        # Eggs
        self.egg_reference = iname.egg_reference in items
        self.egg_brown = iname.egg_brown in items
        self.egg_raw = iname.egg_raw in items
        self.egg_pickled = iname.egg_pickled in items
        self.egg_big = iname.egg_big in items
        self.egg_swan = iname.egg_swan in items
        self.egg_forbidden = iname.egg_forbidden in items
        self.egg_shadow = iname.egg_shadow in items
        self.egg_vanity = iname.egg_vanity in items
        self.egg_service = iname.egg_service in items

        self.egg_depraved = iname.egg_depraved in items
        self.egg_chaos = iname.egg_chaos in items
        self.egg_upside_down = iname.egg_upside_down in items
        self.egg_evil = iname.egg_evil in items
        self.egg_sweet = iname.egg_sweet in items
        self.egg_chocolate = iname.egg_chocolate in items
        self.egg_value = iname.egg_value in items
        self.egg_plant = iname.egg_plant in items
        self.egg_red = iname.egg_red in items
        self.egg_orange = iname.egg_orange in items
        self.egg_sour = iname.egg_sour in items
        self.egg_post_modern = iname.egg_post_modern in items

        self.egg_universal = iname.egg_universal in items
        self.egg_lf = iname.egg_lf in items
        self.egg_zen = iname.egg_zen in items
        self.egg_future = iname.egg_future in items
        self.egg_friendship = iname.egg_friendship in items
        self.egg_truth = iname.egg_truth in items
        self.egg_transcendental = iname.egg_transcendental in items
        self.egg_ancient = iname.egg_ancient in items
        self.egg_magic = iname.egg_magic in items
        self.egg_mystic = iname.egg_mystic in items
        self.egg_holiday = iname.egg_holiday in items
        self.egg_rain = iname.egg_rain in items
        self.egg_razzle = iname.egg_razzle in items
        self.egg_dazzle = iname.egg_dazzle in items

        self.egg_virtual = iname.egg_virtual in items
        self.egg_normal = iname.egg_normal in items
        self.egg_great = iname.egg_great in items
        self.egg_gorgeous = iname.egg_gorgeous in items
        self.egg_planet = iname.egg_planet in items
        self.egg_moon = iname.egg_moon in items
        self.egg_galaxy = iname.egg_galaxy in items
        self.egg_sunset = iname.egg_sunset in items
        self.egg_goodnight = iname.egg_goodnight in items
        self.egg_dream = iname.egg_dream in items
        self.egg_travel = iname.egg_travel in items
        self.egg_promise = iname.egg_promise in items
        self.egg_ice = iname.egg_ice in items
        self.egg_fire = iname.egg_fire in items

        self.egg_bubble = iname.egg_bubble in items
        self.egg_desert = iname.egg_desert in items
        self.egg_clover = iname.egg_clover in items
        self.egg_brick = iname.egg_brick in items
        self.egg_neon = iname.egg_neon in items
        self.egg_iridescent = iname.egg_iridescent in items
        self.egg_rust = iname.egg_rust in items
        self.egg_scarlet = iname.egg_scarlet in items
        self.egg_sapphire = iname.egg_sapphire in items
        self.egg_ruby = iname.egg_ruby in items
        self.egg_jade = iname.egg_jade in items
        self.egg_obsidian = iname.egg_obsidian in items
        self.egg_crystal = iname.egg_crystal in items
        self.egg_golden = iname.egg_golden in items

        self.egg_65 = iname.egg_65 in items

        self.firecracker_refill = len([item for item in items if item == "Firecracker Refill"])  # TODO Fill Logic
        self.big_blue_fruit = len([item for item in items if item == "Big Blue Fruit"])  # TODO Fill Logic

    async def write_to_game(self, process_handle, game_slot, start_address: int):

        """
        Write inventory state to the process
        """

        slot_address = start_address + 0x18 + (0x27010 * game_slot)

        # Read Quest State
        buffer_size = 4
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x1EC, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logger.error("Unable to read Quest State")
            return
        flags = struct.unpack('I', buffer)[0]
        inserted_s_medal = bool(flags >> 15 & 1)
        e_medal_inserted = bool(flags >> 16 & 1)

        # Write Quest State
        if self.bubble < 0 or self.bubble > 2:
            raise AssertionError("Invalid number of bubble wand upgrades %d", self.bubble)
        bits = ((str(flags >> 0 & 1)) +
                (str(flags >> 1 & 1)) +
                (str(flags >> 2 & 1)) +
                (str(flags >> 3 & 1)) +
                (str(flags >> 4 & 1)) +
                (str(flags >> 5 & 1)) +
                (str(flags >> 6 & 1)) +
                (str(flags >> 7 & 1)) +
                (str(flags >> 8 & 1)) +
                (str(flags >> 9 & 1)) +
                (str(flags >> 10 & 1)) +
                (str(flags >> 11 & 1)) +
                (str(flags >> 12 & 1)) +
                (str(flags >> 13 & 1)) +
                (str(flags >> 14 & 1)) +
                (str(flags >> 15 & 1)) +
                (str(flags >> 16 & 1)) +
                (str(flags >> 17 & 1)) +
                (str(flags >> 18 & 1)) +
                ("1" if self.bubble == 2 else "0") +
                ("1" if self.egg_65 else "0") +
                (str(flags >> 21 & 1)) +
                (str(flags >> 22 & 1)) +
                (str(flags >> 23 & 1)) +
                (str(flags >> 24 & 1)) +
                (str(flags >> 25 & 1)) +
                (str(flags >> 26 & 1)) +
                (str(flags >> 27 & 1)) +
                (str(flags >> 28 & 1)) +
                (str(flags >> 29 & 1)) +
                (str(flags >> 30 & 1)) +
                (str(flags >> 31 & 1)))[::-1]
        buffer = int(bits, 2).to_bytes((len(bits) + 7) // 8, byteorder="little")
        bytes_written = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.WriteProcessMemory(process_handle, slot_address + 0x1EC, buffer, len(buffer),
                                                         ctypes.byref(bytes_written)):
            logger.warning("Unable to write Quest State")

        # Write Eggs
        bits = (("1" if self.egg_reference else "0") +
                ("1" if self.egg_brown else "0") +
                ("1" if self.egg_raw else "0") +
                ("1" if self.egg_pickled else "0") +
                ("1" if self.egg_big else "0") +
                ("1" if self.egg_swan else "0") +
                ("1" if self.egg_forbidden else "0") +
                ("1" if self.egg_shadow else "0") +
                ("1" if self.egg_vanity else "0") +
                ("1" if self.egg_service else "0") +

                ("1" if self.egg_depraved else "0") +
                ("1" if self.egg_chaos else "0") +
                ("1" if self.egg_upside_down else "0") +
                ("1" if self.egg_evil else "0") +
                ("1" if self.egg_sweet else "0") +
                ("1" if self.egg_chocolate else "0") +
                ("1" if self.egg_value else "0") +
                ("1" if self.egg_plant else "0") +
                ("1" if self.egg_red else "0") +
                ("1" if self.egg_orange else "0") +
                ("1" if self.egg_sour else "0") +
                ("1" if self.egg_post_modern else "0") +

                ("1" if self.egg_universal else "0") +
                ("1" if self.egg_lf else "0") +
                ("1" if self.egg_zen else "0") +
                ("1" if self.egg_future else "0") +
                ("1" if self.egg_friendship else "0") +
                ("1" if self.egg_truth else "0") +
                ("1" if self.egg_transcendental else "0") +
                ("1" if self.egg_ancient else "0") +
                ("1" if self.egg_magic else "0") +
                ("1" if self.egg_mystic else "0") +
                ("1" if self.egg_holiday else "0") +
                ("1" if self.egg_rain else "0") +
                ("1" if self.egg_razzle else "0") +
                ("1" if self.egg_dazzle else "0") +

                ("1" if self.egg_virtual else "0") +
                ("1" if self.egg_normal else "0") +
                ("1" if self.egg_great else "0") +
                ("1" if self.egg_gorgeous else "0") +
                ("1" if self.egg_planet else "0") +
                ("1" if self.egg_moon else "0") +
                ("1" if self.egg_galaxy else "0") +
                ("1" if self.egg_sunset else "0") +
                ("1" if self.egg_goodnight else "0") +
                ("1" if self.egg_dream else "0") +
                ("1" if self.egg_travel else "0") +
                ("1" if self.egg_promise else "0") +
                ("1" if self.egg_ice else "0") +
                ("1" if self.egg_fire else "0") +

                ("1" if self.egg_bubble else "0") +
                ("1" if self.egg_desert else "0") +
                ("1" if self.egg_clover else "0") +
                ("1" if self.egg_brick else "0") +
                ("1" if self.egg_neon else "0") +
                ("1" if self.egg_iridescent else "0") +
                ("1" if self.egg_rust else "0") +
                ("1" if self.egg_scarlet else "0") +
                ("1" if self.egg_sapphire else "0") +
                ("1" if self.egg_ruby else "0") +
                ("1" if self.egg_jade else "0") +
                ("1" if self.egg_obsidian else "0") +
                ("1" if self.egg_crystal else "0") +
                ("1" if self.egg_golden else "0"))[::-1]
        buffer = int(bits, 2).to_bytes((len(bits) + 7) // 8, byteorder="little")
        bytes_written = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.WriteProcessMemory(process_handle, slot_address + 0x188, buffer, len(buffer),
                                                         ctypes.byref(bytes_written)):
            logger.warning("Unable to write Eggs")

        # Read Candles Lit
        buffer_size = 2
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x1E0, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logger.error("Unable to read Candles Lit")
            return
        flags = struct.unpack('H', buffer)[0]
        candles_lit = ((flags >> 0 & 1) +
                       (flags >> 1 & 1) +
                       (flags >> 2 & 1) +
                       (flags >> 3 & 1) +
                       (flags >> 4 & 1) +
                       (flags >> 5 & 1) +
                       (flags >> 6 & 1) +
                       (flags >> 7 & 1) +
                       (flags >> 8 & 1))

        if candles_lit > self.match:
            raise AssertionError("More candles lit than matches")

        # Write Matches
        if self.match < 0 or self.match > 9:
            raise AssertionError("Invalid number of matches %d", self.match)
        buffer = (self.match - candles_lit).to_bytes()
        bytes_written = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.WriteProcessMemory(process_handle, slot_address + 0x1B2, buffer, len(buffer),
                                                         ctypes.byref(bytes_written)):
            logger.warning("Unable to write Matches")

        # Read Owned Equipment
        buffer_size = 2
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x1DC, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logger.error("Unable to read Owned Equipment")
            return
        flags = struct.unpack('H', buffer)[0]

        # Write Owned Equipment
        bits = ("0" +
                ("1" if self.firecrackers else "0") +
                ("1" if self.flute else "0") +
                ("1" if self.lantern else "0") +
                ("1" if self.top else "0") +
                (str(flags >> 4 & 1)) +
                ("1" if self.bubble > 0 else "0") +
                ("1" if self.yoyo else "0") +
                ("1" if self.slink else "0") +
                ("1" if self.remote else "0") +
                ("1" if self.ball else "0") +
                ("1" if self.wheel else "0") +
                ("1" if self.uv else "0") +
                "000")[::-1]
        buffer = int(bits, 2).to_bytes((len(bits) + 7) // 8, byteorder="little")
        bytes_written = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.WriteProcessMemory(process_handle, slot_address + 0x1DC, buffer, len(buffer),
                                                         ctypes.byref(bytes_written)):
            logger.warning("Unable to write Owned Equipment")

        # Read Other Items
        buffer_size = 1
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x1DE, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logger.error("Unable to read Other Items")
            return
        flags = struct.unpack('B', buffer)[0]

        # Write Other Items
        bits = ((str(flags >> 0 & 1)) +
                ("1" if (self.s_medal and not inserted_s_medal) else "0") +
                "0" +
                ("1" if self.house_key else "0") +
                ("1" if self.office_key else "0") +
                "0" +
                ("1" if (self.e_medal and not e_medal_inserted) else "0") +
                ("1" if self.fanny_pack else "0"))[::-1]
        buffer = int(bits, 2).to_bytes((len(bits) + 7) // 8, byteorder="little")
        bytes_written = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.WriteProcessMemory(process_handle, slot_address + 0x1DE, buffer, len(buffer),
                                                         ctypes.byref(bytes_written)):
            logger.warning("Unable to write Other Items")


class AnimalWellCommandProcessor(ClientCommandProcessor):
    """
    CommandProcessor for Animal Well
    """

    def _cmd_connection(self):
        """Check Animal Well Connection State"""
        if isinstance(self.ctx, AnimalWellContext):
            logger.info(f"Animal Well Connection Status: {self.ctx.connection_status}")


class AnimalWellContext(CommonContext):
    """
    Animal Well Archipelago context
    """
    command_processor = AnimalWellCommandProcessor
    items_handling = 0b101  # get sent remote and starting items

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.bonus_items = []
        self.process_handle = None
        self.start_address = None
        self.process_sync_task = None
        self.locations = AWLocations()
        self.items = AWItems()
        self.messages = {}
        self.locations_array = None
        self.connection_status = CONNECTION_INITIAL_STATUS
        self.game = 'Animal Well'
        self.awaiting_game = True

    async def server_auth(self, password_requested: bool = False):
        """
        Authenticate with the Archipelago server
        """
        if password_requested and not self.password:
            await super(AnimalWellContext, self).server_auth(password_requested)
        if self.awaiting_game:
            logger.info('Awaiting connection to Animal Well to get Player information')
            return

        await self.get_username()
        await self.send_connect()

    def run_gui(self):
        """
        Run the GUI
        """
        from kvui import GameManager

        class AnimalWellManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Animal Well Client"

        self.ui = AnimalWellManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


async def get_animal_well_process_handle():
    """
    Get the process handle of Animal Well
    """
    if platform.uname()[0] == "Windows":
        logger.debug("Getting process handle on Windows")

        pid = None
        command = subprocess.Popen(['tasklist', '/FI', f'IMAGENAME eq Animal Well.exe', '/fo', 'CSV'],
                                   stdout=subprocess.PIPE)
        output = str(command.communicate()[0])
        if 'INFO' not in output:
            output_list = output.split("Animal Well.exe")
            for i in range(1, len(output_list)):
                if pid is None:
                    pid = int(output_list[i].replace("\"", '')[1:].split(',')[0])
                else:
                    logger.error("Multiple Animal Well Processes Exist")
                    raise ConnectionRefusedError

        if pid is None:
            logger.warning("No Animal Well Processes Exist")
            raise ConnectionRefusedError

        logger.debug(f"Found PID {pid}")
        process_handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)

        logger.debug("Reading save file data")
        with open(f"{os.getenv('APPDATA')}\\..\\LocalLow\\Billy Basso\\Animal Well\\AnimalWell.sav", "rb") as savefile:
            file_header = bytearray(savefile.read(24))
            # Set slot to 0 for comparison purposes
            file_header[12] = 0

        logger.debug("Finding start address of memory")
        # In my experience they're all somewhere after this address
        address = 0x10000000
        buffer_size = 8
        found = False
        while not found:
            buffer = ctypes.create_string_buffer(buffer_size)
            bytes_read = ctypes.c_ulong(0)
            if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, address, buffer, buffer_size,
                                                            ctypes.byref(bytes_read)):
                address += 4
                continue
            process_header = bytearray(struct.unpack('Q', buffer)[0].to_bytes(8, byteorder="little"))
            buffer = ctypes.create_string_buffer(buffer_size)
            bytes_read = ctypes.c_ulong(0)
            if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, address + 8, buffer, buffer_size,
                                                            ctypes.byref(bytes_read)):
                address += 4
                continue
            process_header.extend(struct.unpack('Q', buffer)[0].to_bytes(8, byteorder="little"))
            buffer = ctypes.create_string_buffer(buffer_size)
            bytes_read = ctypes.c_ulong(0)
            if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, address + 16, buffer, buffer_size,
                                                            ctypes.byref(bytes_read)):
                address += 4
                continue
            process_header.extend(struct.unpack('Q', buffer)[0].to_bytes(8, byteorder="little"))
            process_header[12] = 0
            if bytes(file_header) == bytes(process_header):
                logger.debug("Found start address %d", address)
                found = True
            else:
                address += 4

        buffer_size = 4
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, address, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logger.error("Unable to read version information from process")
            raise ConnectionAbortedError
        version = struct.unpack('I', buffer)[0]
        logger.debug("Found version number %d", version)

        if version != 9:
            logger.fatal("Animal Well version %d detected, only version 9 supported", version)
            raise NotImplementedError

        return process_handle, address
    else:
        logger.fatal("Only Windows is implemented right now")
        raise NotImplementedError


async def get_active_game_slot(process_handle, start_address):
    """
    Get the game slot currently being played
    """
    if platform.uname()[0] == "Windows":
        buffer_size = 1
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, start_address + 12, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logger.error("Unable to read version information from process")
            raise ConnectionResetError
        slot = struct.unpack('B', buffer)[0]
        return slot
    else:
        logger.fatal("Only Windows is implemented right now")
        raise NotImplementedError


async def process_sync_task(ctx: AnimalWellContext):
    """
    Connect to the Animal Well process
    """
    logger.info("Starting Animal Well connector. Use /connection for status information")
    while not ctx.exit_event.is_set():
        error_status = None
        if ctx.process_handle and ctx.start_address:
            try:
                active_slot = await get_active_game_slot(ctx.process_handle, ctx.start_address)
                await ctx.locations.read_from_game(ctx.process_handle, active_slot, ctx.start_address)
                await ctx.locations.write_to_archipelago(ctx)
                await ctx.items.read_from_archipelago(ctx)
                await ctx.items.write_to_game(ctx.process_handle, active_slot, ctx.start_address)
                if ctx.awaiting_game:
                    ctx.awaiting_game = False
                    await ctx.server_auth()
            except ConnectionResetError:
                logger.debug("Read failed due to Connection Lost, Reconnecting")
                error_status = CONNECTION_RESET_STATUS
                ctx.process_handle = None
                ctx.start_address = None
            if ctx.connection_status == CONNECTION_TENTATIVE_STATUS:
                if not error_status:
                    logger.info("Successfully Connected to Animal Well")
                    ctx.connection_status = CONNECTION_CONNECTED_STATUS
                else:
                    ctx.connection_status = f"Was tentatively connected but error occurred: {error_status}"
            elif error_status:
                ctx.connection_status = error_status
                logger.info(
                    "Lost connection to Animal Well and attempting to reconnect. Use /connection for status updates")
        else:
            try:
                logger.debug("Attempting to connect to Animal Well")
                ctx.process_handle, ctx.start_address = await get_animal_well_process_handle()
                ctx.connection_status = CONNECTION_TENTATIVE_STATUS
            except ConnectionRefusedError:
                logger.debug("Connection Refused, Trying Again")
                ctx.connection_status = CONNECTION_REFUSED_STATUS
                continue


if __name__ == '__main__':
    # Text Mode to use !hint and such with games that have no text entry
    Utils.init_logging("AnimalWellClient")


    async def main(args):
        """
        main function
        """
        ctx = AnimalWellContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        ctx.process_sync_task = asyncio.create_task(process_sync_task(ctx), name="Animal Well Process Sync")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()

        if ctx.process_sync_task:
            await ctx.process_sync_task


    import colorama

    parser = get_base_parser()
    parsed_args = parser.parse_args()
    colorama.init()

    asyncio.run(main(parsed_args))
    colorama.deinit()
