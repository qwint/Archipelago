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
from NetUtils import ClientStatus
from worlds.animal_well.items import item_name_to_id
from worlds.animal_well.locations import location_name_to_id
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
        self.disc_spot = False
        self.yoyo_chest = False
        self.slink_chest = False
        self.flute_chest = False
        self.top_chest = False
        self.lantern_chest = False
        self.uv_lantern_chest = False
        self.b_ball_chest = False
        self.remote_chest = False
        self.wheel_chest = False

        self.mock_disc_chest = False
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

        self.key_bear_lower = False
        self.key_bear_upper = False
        self.key_chest_mouse_head_lever = False
        self.key_frog_guard_room_west = False
        self.key_frog_guard_room_east = False
        self.key_dog = False
        self.key_house = False
        self.key_office = False

        self.medal_e = False
        self.medal_s = False
        self.medal_k = False  # TODO K shard logic

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
        self.map_chest = False
        self.stamp_chest = False
        self.pencil_chest = False

        # bnnnnuyuy
        self.bunny_mural = False
        self.bunny_chinchilla_vine = False
        self.bunny_water_spike = False
        self.bunny_map = False
        self.bunny_uv = False
        self.bunny_fish = False
        self.bunny_face = False
        self.bunny_crow = False
        self.bunny_duck = False
        self.bunny_dream = False
        self.bunny_file_bud = False
        self.bunny_lava = False
        self.bunny_tv = False
        self.bunny_barcode = False
        self.bunny_ghost_dog = False
        self.bunny_disc_spike = False

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
        self.egg_pickled = bool(flags >> 3 & 1)
        self.egg_big = bool(flags >> 4 & 1)  # TODO-VERIFY
        self.egg_swan = bool(flags >> 5 & 1)
        self.egg_forbidden = bool(flags >> 6 & 1)
        self.egg_shadow = bool(flags >> 7 & 1)

        self.egg_vanity = bool(flags >> 8 & 1)
        self.egg_service = bool(flags >> 9 & 1)
        # self.mama_cha = bool(flags >> 10 & 1)  # TODO-VERIFY
        self.match_dog_switch_bounce = bool(flags >> 11 & 1)
        self.egg_depraved = bool(flags >> 12 & 1)
        self.match_bear = bool(flags >> 13 & 1)  # TODO-VERIFY
        self.egg_chaos = bool(flags >> 14 & 1)
        self.b_ball_chest = bool(flags >> 15 & 1)  # TODO-VERIFY

        self.key_dog = bool(flags >> 16 & 1)  # TODO-VERIFY
        self.egg_upside_down = bool(flags >> 17 & 1)  # TODO-VERIFY
        self.egg_evil = bool(flags >> 18 & 1)  # TODO-VERIFY
        self.match_dog_upper_east = bool(flags >> 19 & 1)
        self.egg_sweet = bool(flags >> 20 & 1)
        self.match_center_well = bool(flags >> 21 & 1)
        self.egg_chocolate = bool(flags >> 22 & 1)
        self.egg_value = bool(flags >> 23 & 1)

        self.egg_plant = bool(flags >> 24 & 1)
        self.egg_red = bool(flags >> 25 & 1)
        self.egg_orange = bool(flags >> 26 & 1)  # TODO-VERIFY
        self.mock_disc_chest = bool(flags >> 27 & 1)  # TODO-VERIFY
        self.egg_sour = bool(flags >> 28 & 1)
        self.egg_post_modern = bool(flags >> 29 & 1)
        self.slink_chest = bool(flags >> 30 & 1)
        self.egg_universal = bool(flags >> 31 & 1)  # TODO-VERIFY

        self.egg_lf = bool(flags >> 32 & 1)  # TODO-VERIFY
        self.egg_zen = bool(flags >> 33 & 1)
        self.key_bear_upper = bool(flags >> 34 & 1)  # TODO
        self.egg_future = bool(flags >> 35 & 1)  # TODO-VERIFY
        self.egg_friendship = bool(flags >> 36 & 1)
        self.disc_spot = bool(flags >> 37 & 1)  # TODO-VERIFY
        self.match_above_egg_room = bool(flags >> 38 & 1)  # TODO-VERIFY
        self.key_office = bool(flags >> 39 & 1)  # TODO-VERIFY

        self.egg_truth = bool(flags >> 40 & 1)  # TODO-VERIFY
        self.egg_transcendental = bool(flags >> 41 & 1)  # TODO-VERIFY
        self.medal_s = bool(flags >> 42 & 1)  # TODO-VERIFY
        self.egg_ancient = bool(flags >> 43 & 1)
        self.egg_magic = bool(flags >> 44 & 1)
        self.egg_mystic = bool(flags >> 45 & 1)
        self.flute_chest = bool(flags >> 46 & 1)  # TODO-VERIFY
        self.egg_65 = bool(flags >> 47 & 1)

        self.top_chest = bool(flags >> 48 & 1)  # TODO-VERIFY
        self.pencil_chest = bool(flags >> 49 & 1)  # TODO-VERIFY
        self.stamp_chest = bool(flags >> 50 & 1)
        self.egg_holiday = bool(flags >> 51 & 1)  # TODO-VERIFY
        self.egg_rain = bool(flags >> 52 & 1)  # TODO-VERIFY
        self.egg_razzle = bool(flags >> 53 & 1)
        self.key_bear_lower = bool(flags >> 54 & 1)  # TODO-VERIFY
        self.egg_dazzle = bool(flags >> 55 & 1)

        self.match_fish_mural = bool(flags >> 56 & 1)  # TODO-VERIFY
        self.egg_virtual = bool(flags >> 57 & 1)
        self.egg_normal = bool(flags >> 58 & 1)
        self.egg_great = bool(flags >> 59 & 1)
        self.egg_gorgeous = bool(flags >> 60 & 1)
        self.map_chest = bool(flags >> 61 & 1)
        self.key_chest_mouse_head_lever = bool(flags >> 62 & 1)  # TODO-VERIFY
        self.match_under_mouse_statue = bool(flags >> 63 & 1)  # TODO-VERIFY

        self.egg_planet = bool(flags >> 64 & 1)  # TODO-VERIFY
        self.egg_moon = bool(flags >> 65 & 1)
        self.egg_galaxy = bool(flags >> 66 & 1)
        self.egg_sunset = bool(flags >> 67 & 1)
        self.b_wand_chest = bool(flags >> 68 & 1)
        self.egg_goodnight = bool(flags >> 69 & 1)
        self.match_start_ceiling = bool(flags >> 70 & 1)
        self.egg_dream = bool(flags >> 71 & 1)

        self.egg_travel = bool(flags >> 72 & 1)  # TODO-VERIFY
        self.egg_promise = bool(flags >> 73 & 1)
        self.egg_ice = bool(flags >> 74 & 1)
        self.lantern_chest = bool(flags >> 75 & 1)  # TODO-VERIFY
        self.egg_fire = bool(flags >> 76 & 1)
        self.egg_bubble = bool(flags >> 77 & 1)
        self.egg_desert = bool(flags >> 78 & 1)
        self.wheel_chest = bool(flags >> 79 & 1)  # TODO-VERIFY

        self.egg_clover = bool(flags >> 80 & 1)
        self.match_guard_room = bool(flags >> 81 & 1)  # TODO-VERIFY
        self.key_frog_guard_room_west = bool(flags >> 82 & 1)  # TODO-VERIFY
        self.key_frog_guard_room_east = bool(flags >> 83 & 1)  # TODO-VERIFY
        self.egg_brick = bool(flags >> 84 & 1)  # TODO-VERIFY
        self.egg_neon = bool(flags >> 85 & 1)  # TODO-VERIFY
        self.remote_chest = bool(flags >> 86 & 1)  # TODO-VERIFY
        self.egg_iridescent = bool(flags >> 87 & 1)

        self.egg_rust = bool(flags >> 88 & 1)
        self.egg_scarlet = bool(flags >> 89 & 1)  # TODO-VERIFY
        self.medal_e = bool(flags >> 90 & 1)  # TODO-VERIFY
        self.egg_sapphire = bool(flags >> 91 & 1)
        self.egg_ruby = bool(flags >> 92 & 1)
        self.egg_jade = bool(flags >> 93 & 1)
        self.egg_obsidian = bool(flags >> 94 & 1)
        self.bb_wand_chest = bool(flags >> 95 & 1)  # TODO-VERIFY

        self.uv_lantern_chest = bool(flags >> 96 & 1)  # TODO-VERIFY
        self.yoyo_chest = bool(flags >> 97 & 1)
        self.egg_crystal = bool(flags >> 98 & 1)  # TODO-VERIFY
        self.egg_golden = bool(flags >> 99 & 1)  # TODO-VERIFY
        self.fanny_pack_chest = bool(flags >> 100 & 1)

        # Read Bunnies
        buffer_size = 4
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x198, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logger.error("Unable to read Bunnies State")
            return
        flags = struct.unpack('I', buffer)[0]
        self.bunny_water_spike = bool(flags >> 0 & 1)
        self.bunny_barcode = bool(flags >> 2 & 1)
        self.bunny_crow = bool(flags >> 3 & 1)
        self.bunny_face = bool(flags >> 4 & 1)
        self.bunny_fish = bool(flags >> 6 & 1)
        self.bunny_map = bool(flags >> 7 & 1)
        self.bunny_tv = bool(flags >> 8 & 1)
        self.bunny_uv = bool(flags >> 9 & 1)
        self.bunny_file_bud = bool(flags >> 10 & 1)
        self.bunny_chinchilla_vine = bool(flags >> 11 & 1)
        self.bunny_mural = bool(flags >> 15 & 1)
        self.bunny_duck = bool(flags >> 22 & 1)
        self.bunny_ghost_dog = bool(flags >> 25 & 1)
        self.bunny_dream = bool(flags >> 28 & 1)
        self.bunny_lava = bool(flags >> 30 & 1)
        self.bunny_disc_spike = bool(flags >> 31 & 1)

        # Read Startup State
        buffer_size = 2
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x21C, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logger.error("Unable to read Startup State")
            return
        flags = struct.unpack('H', buffer)[0]
        self.key_house = bool(flags >> 4 & 1)

    async def write_to_archipelago(self, ctx):
        """
        Write checked locations to archipelago
        """
        # major items
        if self.b_wand_chest:
            ctx.locations_checked.add(location_name_to_id[lname.b_wand_chest.value])
        if self.bb_wand_chest:
            ctx.locations_checked.add(location_name_to_id[lname.bb_wand_chest.value])
        if self.disc_spot:
            ctx.locations_checked.add(location_name_to_id[lname.disc_spot.value])
        if self.yoyo_chest:
            ctx.locations_checked.add(location_name_to_id[lname.yoyo_chest.value])
        if self.slink_chest:
            ctx.locations_checked.add(location_name_to_id[lname.slink_chest.value])
        if self.flute_chest:
            ctx.locations_checked.add(location_name_to_id[lname.flute_chest.value])
        if self.top_chest:
            ctx.locations_checked.add(location_name_to_id[lname.top_chest.value])
        if self.lantern_chest:
            ctx.locations_checked.add(location_name_to_id[lname.lantern_chest.value])
        if self.uv_lantern_chest:
            ctx.locations_checked.add(location_name_to_id[lname.uv_lantern_chest.value])
        if self.b_ball_chest:
            ctx.locations_checked.add(location_name_to_id[lname.b_ball_chest.value])
        if self.remote_chest:
            ctx.locations_checked.add(location_name_to_id[lname.remote_chest.value])
        if self.wheel_chest:
            ctx.locations_checked.add(location_name_to_id[lname.wheel_chest.value])

        if self.mock_disc_chest:
            ctx.locations_checked.add(location_name_to_id[lname.mock_disc_chest.value])
        if self.fanny_pack_chest:
            ctx.locations_checked.add(location_name_to_id[lname.fanny_pack_chest.value])

        if self.match_start_ceiling:
            ctx.locations_checked.add(location_name_to_id[lname.match_start_ceiling.value])
        if self.match_fish_mural:
            ctx.locations_checked.add(location_name_to_id[lname.match_fish_mural.value])
        if self.match_dog_switch_bounce:
            ctx.locations_checked.add(location_name_to_id[lname.match_dog_switch_bounce.value])
        if self.match_dog_upper_east:
            ctx.locations_checked.add(location_name_to_id[lname.match_dog_upper_east.value])
        if self.match_bear:
            ctx.locations_checked.add(location_name_to_id[lname.match_bear.value])
        if self.match_above_egg_room:
            ctx.locations_checked.add(location_name_to_id[lname.match_above_egg_room.value])
        if self.match_center_well:
            ctx.locations_checked.add(location_name_to_id[lname.match_center_well.value])
        if self.match_guard_room:
            ctx.locations_checked.add(location_name_to_id[lname.match_guard_room.value])
        if self.match_under_mouse_statue:
            ctx.locations_checked.add(location_name_to_id[lname.match_under_mouse_statue.value])

        if self.key_bear_lower:
            ctx.locations_checked.add(location_name_to_id[lname.key_bear_lower.value])
        if self.key_bear_upper:
            ctx.locations_checked.add(location_name_to_id[lname.key_bear_upper.value])
        if self.key_chest_mouse_head_lever:
            ctx.locations_checked.add(location_name_to_id[lname.key_chest_mouse_head_lever.value])
        if self.key_frog_guard_room_west:
            ctx.locations_checked.add(location_name_to_id[lname.key_frog_guard_room_west.value])
        if self.key_frog_guard_room_east:
            ctx.locations_checked.add(location_name_to_id[lname.key_frog_guard_room_east.value])
        if self.key_dog:
            ctx.locations_checked.add(location_name_to_id[lname.key_dog.value])
        if self.key_house:
            ctx.locations_checked.add(location_name_to_id[lname.key_house.value])
        if self.key_office:
            ctx.locations_checked.add(location_name_to_id[lname.key_office.value])

        if self.medal_e:
            ctx.locations_checked.add(location_name_to_id[lname.medal_e.value])
        if self.medal_s:
            ctx.locations_checked.add(location_name_to_id[lname.medal_s.value])
        if self.medal_k:
            ctx.locations_checked.add(location_name_to_id[lname.medal_k.value])

        # eggs, sorted by row top-to-bottom
        if self.egg_reference:
            ctx.locations_checked.add(location_name_to_id[lname.egg_reference.value])
        if self.egg_brown:
            ctx.locations_checked.add(location_name_to_id[lname.egg_brown.value])
        if self.egg_raw:
            ctx.locations_checked.add(location_name_to_id[lname.egg_raw.value])
        if self.egg_pickled:
            ctx.locations_checked.add(location_name_to_id[lname.egg_pickled.value])
        if self.egg_big:
            ctx.locations_checked.add(location_name_to_id[lname.egg_big.value])
        if self.egg_swan:
            ctx.locations_checked.add(location_name_to_id[lname.egg_swan.value])
        if self.egg_forbidden:
            ctx.locations_checked.add(location_name_to_id[lname.egg_forbidden.value])
        if self.egg_shadow:
            ctx.locations_checked.add(location_name_to_id[lname.egg_shadow.value])
        if self.egg_vanity:
            ctx.locations_checked.add(location_name_to_id[lname.egg_vanity.value])
        if self.egg_service:
            ctx.locations_checked.add(location_name_to_id[lname.egg_service.value])

        if self.egg_depraved:
            ctx.locations_checked.add(location_name_to_id[lname.egg_depraved.value])
        if self.egg_chaos:
            ctx.locations_checked.add(location_name_to_id[lname.egg_chaos.value])
        if self.egg_upside_down:
            ctx.locations_checked.add(location_name_to_id[lname.egg_upside_down.value])
        if self.egg_evil:
            ctx.locations_checked.add(location_name_to_id[lname.egg_evil.value])
        if self.egg_sweet:
            ctx.locations_checked.add(location_name_to_id[lname.egg_sweet.value])
        if self.egg_chocolate:
            ctx.locations_checked.add(location_name_to_id[lname.egg_chocolate.value])
        if self.egg_value:
            ctx.locations_checked.add(location_name_to_id[lname.egg_value.value])
        if self.egg_plant:
            ctx.locations_checked.add(location_name_to_id[lname.egg_plant.value])
        if self.egg_red:
            ctx.locations_checked.add(location_name_to_id[lname.egg_red.value])
        if self.egg_orange:
            ctx.locations_checked.add(location_name_to_id[lname.egg_orange.value])
        if self.egg_sour:
            ctx.locations_checked.add(location_name_to_id[lname.egg_sour.value])
        if self.egg_post_modern:
            ctx.locations_checked.add(location_name_to_id[lname.egg_post_modern.value])

        if self.egg_universal:
            ctx.locations_checked.add(location_name_to_id[lname.egg_universal.value])
        if self.egg_lf:
            ctx.locations_checked.add(location_name_to_id[lname.egg_lf.value])
        if self.egg_zen:
            ctx.locations_checked.add(location_name_to_id[lname.egg_zen.value])
        if self.egg_future:
            ctx.locations_checked.add(location_name_to_id[lname.egg_future.value])
        if self.egg_friendship:
            ctx.locations_checked.add(location_name_to_id[lname.egg_friendship.value])
        if self.egg_truth:
            ctx.locations_checked.add(location_name_to_id[lname.egg_truth.value])
        if self.egg_transcendental:
            ctx.locations_checked.add(location_name_to_id[lname.egg_transcendental.value])
        if self.egg_ancient:
            ctx.locations_checked.add(location_name_to_id[lname.egg_ancient.value])
        if self.egg_magic:
            ctx.locations_checked.add(location_name_to_id[lname.egg_magic.value])
        if self.egg_mystic:
            ctx.locations_checked.add(location_name_to_id[lname.egg_mystic.value])
        if self.egg_holiday:
            ctx.locations_checked.add(location_name_to_id[lname.egg_holiday.value])
        if self.egg_rain:
            ctx.locations_checked.add(location_name_to_id[lname.egg_rain.value])
        if self.egg_razzle:
            ctx.locations_checked.add(location_name_to_id[lname.egg_razzle.value])
        if self.egg_dazzle:
            ctx.locations_checked.add(location_name_to_id[lname.egg_dazzle.value])

        if self.egg_virtual:
            ctx.locations_checked.add(location_name_to_id[lname.egg_virtual.value])
        if self.egg_normal:
            ctx.locations_checked.add(location_name_to_id[lname.egg_normal.value])
        if self.egg_great:
            ctx.locations_checked.add(location_name_to_id[lname.egg_great.value])
        if self.egg_gorgeous:
            ctx.locations_checked.add(location_name_to_id[lname.egg_gorgeous.value])
        if self.egg_planet:
            ctx.locations_checked.add(location_name_to_id[lname.egg_planet.value])
        if self.egg_moon:
            ctx.locations_checked.add(location_name_to_id[lname.egg_moon.value])
        if self.egg_galaxy:
            ctx.locations_checked.add(location_name_to_id[lname.egg_galaxy.value])
        if self.egg_sunset:
            ctx.locations_checked.add(location_name_to_id[lname.egg_sunset.value])
        if self.egg_goodnight:
            ctx.locations_checked.add(location_name_to_id[lname.egg_goodnight.value])
        if self.egg_dream:
            ctx.locations_checked.add(location_name_to_id[lname.egg_dream.value])
        if self.egg_travel:
            ctx.locations_checked.add(location_name_to_id[lname.egg_travel.value])
        if self.egg_promise:
            ctx.locations_checked.add(location_name_to_id[lname.egg_promise.value])
        if self.egg_ice:
            ctx.locations_checked.add(location_name_to_id[lname.egg_ice.value])
        if self.egg_fire:
            ctx.locations_checked.add(location_name_to_id[lname.egg_fire.value])

        if self.egg_bubble:
            ctx.locations_checked.add(location_name_to_id[lname.egg_bubble.value])
        if self.egg_desert:
            ctx.locations_checked.add(location_name_to_id[lname.egg_desert.value])
        if self.egg_clover:
            ctx.locations_checked.add(location_name_to_id[lname.egg_clover.value])
        if self.egg_brick:
            ctx.locations_checked.add(location_name_to_id[lname.egg_brick.value])
        if self.egg_neon:
            ctx.locations_checked.add(location_name_to_id[lname.egg_neon.value])
        if self.egg_iridescent:
            ctx.locations_checked.add(location_name_to_id[lname.egg_iridescent.value])
        if self.egg_rust:
            ctx.locations_checked.add(location_name_to_id[lname.egg_rust.value])
        if self.egg_scarlet:
            ctx.locations_checked.add(location_name_to_id[lname.egg_scarlet.value])
        if self.egg_sapphire:
            ctx.locations_checked.add(location_name_to_id[lname.egg_sapphire.value])
        if self.egg_ruby:
            ctx.locations_checked.add(location_name_to_id[lname.egg_ruby.value])
        if self.egg_jade:
            ctx.locations_checked.add(location_name_to_id[lname.egg_jade.value])
        if self.egg_obsidian:
            ctx.locations_checked.add(location_name_to_id[lname.egg_obsidian.value])
        if self.egg_crystal:
            ctx.locations_checked.add(location_name_to_id[lname.egg_crystal.value])
        if self.egg_golden:
            ctx.locations_checked.add(location_name_to_id[lname.egg_golden.value])

        if self.egg_65:
            ctx.locations_checked.add(location_name_to_id[lname.egg_65.value])

        # map things
        if self.map_chest:
            ctx.locations_checked.add(location_name_to_id[lname.map_chest.value])
        if self.stamp_chest:
            ctx.locations_checked.add(location_name_to_id[lname.stamp_chest.value])
        if self.pencil_chest:
            ctx.locations_checked.add(location_name_to_id[lname.pencil_chest.value])

        # bnnnnuyuy
        if self.bunny_mural:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_mural.value])
        if self.bunny_chinchilla_vine:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_chinchilla_vine.value])
        if self.bunny_water_spike:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_water_spike.value])
        if self.bunny_map:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_map.value])
        if self.bunny_uv:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_uv.value])
        if self.bunny_fish:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_fish.value])
        if self.bunny_face:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_face.value])
        if self.bunny_crow:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_crow.value])
        if self.bunny_duck:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_duck.value])
        if self.bunny_dream:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_dream.value])
        if self.bunny_file_bud:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_file_bud.value])
        if self.bunny_lava:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_lava.value])
        if self.bunny_tv:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_tv.value])
        if self.bunny_barcode:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_barcode.value])
        if self.bunny_ghost_dog:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_ghost_dog.value])
        if self.bunny_disc_spike:
            ctx.locations_checked.add(location_name_to_id[lname.bunny_disc_spike.value])

        # extras
        # if self.mama_cha:
        #     ctx.locations_checked.add(location_name_to_id[lname.mama_cha.value])
        # if self.squirrel_acorn:
        #     ctx.locations_checked.add(location_name_to_id[lname.squirrel_acorn.value])
        # kangaroo medal drops

        # TODO other victory conditions
        if not ctx.finished_game and self.key_house:
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True

        locations_checked = []
        for location in ctx.missing_locations:
            if location in ctx.locations_checked:
                locations_checked.append(location)
        if locations_checked:
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
        self.m_disc = False
        self.fanny_pack = False

        self.match = 0
        self.matchbox = False

        self.key = 0
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

        self.firecracker_refill = 0  # TODO Filler
        self.big_blue_fruit = 0  # TODO Filler

    async def read_from_archipelago(self, ctx):
        """
        Read inventory state from archipelago
        """
        items = [item.item for item in ctx.items_received]

        # Major progression items
        self.bubble = len([item for item in items if item == item_name_to_id[iname.bubble.value]])
        # self.disc = item_name_to_id[iname.disc.value] in items
        self.yoyo = item_name_to_id[iname.yoyo.value] in items
        self.slink = item_name_to_id[iname.slink.value] in items
        self.flute = item_name_to_id[iname.flute.value] in items
        self.top = item_name_to_id[iname.top.value] in items
        self.lantern = item_name_to_id[iname.lantern.value] in items
        self.uv = item_name_to_id[iname.uv.value] in items
        self.ball = item_name_to_id[iname.ball.value] in items
        self.remote = item_name_to_id[iname.remote.value] in items
        self.wheel = item_name_to_id[iname.wheel.value] in items
        self.firecrackers = item_name_to_id[iname.firecrackers.value] in items

        # Minor progression items and keys
        self.m_disc = item_name_to_id[iname.m_disc.value] in items
        self.fanny_pack = item_name_to_id[iname.fanny_pack.value] in items

        self.match = len([item for item in items if item == item_name_to_id[iname.match.value]])
        self.matchbox = item_name_to_id[iname.matchbox.value] in items

        self.key = len([item for item in items if item == item_name_to_id[iname.key.value]])
        self.key_ring = item_name_to_id[iname.key_ring.value] in items
        self.house_key = item_name_to_id[iname.house_key.value] in items
        self.office_key = item_name_to_id[iname.office_key.value] in items

        self.e_medal = item_name_to_id[iname.e_medal.value] in items
        self.s_medal = item_name_to_id[iname.s_medal.value] in items
        self.k_shard = len([item for item in items if item == item_name_to_id[iname.k_shard.value]])

        # self.blue_flame = item_name_to_id[iname.blue_flame.value] in items
        # self.green_flame = item_name_to_id[iname.green_flame.value] in items
        # self.violet_flame = item_name_to_id[iname.violet_flame.value] in items
        # self.pink_flame = item_name_to_id[iname.pink_flame.value] in items

        # Eggs
        self.egg_reference = item_name_to_id[iname.egg_reference.value] in items
        self.egg_brown = item_name_to_id[iname.egg_brown.value] in items
        self.egg_raw = item_name_to_id[iname.egg_raw.value] in items
        self.egg_pickled = item_name_to_id[iname.egg_pickled.value] in items
        self.egg_big = item_name_to_id[iname.egg_big.value] in items
        self.egg_swan = item_name_to_id[iname.egg_swan.value] in items
        self.egg_forbidden = item_name_to_id[iname.egg_forbidden.value] in items
        self.egg_shadow = item_name_to_id[iname.egg_shadow.value] in items
        self.egg_vanity = item_name_to_id[iname.egg_vanity.value] in items
        self.egg_service = item_name_to_id[iname.egg_service.value] in items

        self.egg_depraved = item_name_to_id[iname.egg_depraved.value] in items
        self.egg_chaos = item_name_to_id[iname.egg_chaos.value] in items
        self.egg_upside_down = item_name_to_id[iname.egg_upside_down.value] in items
        self.egg_evil = item_name_to_id[iname.egg_evil.value] in items
        self.egg_sweet = item_name_to_id[iname.egg_sweet.value] in items
        self.egg_chocolate = item_name_to_id[iname.egg_chocolate.value] in items
        self.egg_value = item_name_to_id[iname.egg_value.value] in items
        self.egg_plant = item_name_to_id[iname.egg_plant.value] in items
        self.egg_red = item_name_to_id[iname.egg_red.value] in items
        self.egg_orange = item_name_to_id[iname.egg_orange.value] in items
        self.egg_sour = item_name_to_id[iname.egg_sour.value] in items
        self.egg_post_modern = item_name_to_id[iname.egg_post_modern.value] in items

        self.egg_universal = item_name_to_id[iname.egg_universal.value] in items
        self.egg_lf = item_name_to_id[iname.egg_lf.value] in items
        self.egg_zen = item_name_to_id[iname.egg_zen.value] in items
        self.egg_future = item_name_to_id[iname.egg_future.value] in items
        self.egg_friendship = item_name_to_id[iname.egg_friendship.value] in items
        self.egg_truth = item_name_to_id[iname.egg_truth.value] in items
        self.egg_transcendental = item_name_to_id[iname.egg_transcendental.value] in items
        self.egg_ancient = item_name_to_id[iname.egg_ancient.value] in items
        self.egg_magic = item_name_to_id[iname.egg_magic.value] in items
        self.egg_mystic = item_name_to_id[iname.egg_mystic.value] in items
        self.egg_holiday = item_name_to_id[iname.egg_holiday.value] in items
        self.egg_rain = item_name_to_id[iname.egg_rain.value] in items
        self.egg_razzle = item_name_to_id[iname.egg_razzle.value] in items
        self.egg_dazzle = item_name_to_id[iname.egg_dazzle.value] in items

        self.egg_virtual = item_name_to_id[iname.egg_virtual.value] in items
        self.egg_normal = item_name_to_id[iname.egg_normal.value] in items
        self.egg_great = item_name_to_id[iname.egg_great.value] in items
        self.egg_gorgeous = item_name_to_id[iname.egg_gorgeous.value] in items
        self.egg_planet = item_name_to_id[iname.egg_planet.value] in items
        self.egg_moon = item_name_to_id[iname.egg_moon.value] in items
        self.egg_galaxy = item_name_to_id[iname.egg_galaxy.value] in items
        self.egg_sunset = item_name_to_id[iname.egg_sunset.value] in items
        self.egg_goodnight = item_name_to_id[iname.egg_goodnight.value] in items
        self.egg_dream = item_name_to_id[iname.egg_dream.value] in items
        self.egg_travel = item_name_to_id[iname.egg_travel.value] in items
        self.egg_promise = item_name_to_id[iname.egg_promise.value] in items
        self.egg_ice = item_name_to_id[iname.egg_ice.value] in items
        self.egg_fire = item_name_to_id[iname.egg_fire.value] in items

        self.egg_bubble = item_name_to_id[iname.egg_bubble.value] in items
        self.egg_desert = item_name_to_id[iname.egg_desert.value] in items
        self.egg_clover = item_name_to_id[iname.egg_clover.value] in items
        self.egg_brick = item_name_to_id[iname.egg_brick.value] in items
        self.egg_neon = item_name_to_id[iname.egg_neon.value] in items
        self.egg_iridescent = item_name_to_id[iname.egg_iridescent.value] in items
        self.egg_rust = item_name_to_id[iname.egg_rust.value] in items
        self.egg_scarlet = item_name_to_id[iname.egg_scarlet.value] in items
        self.egg_sapphire = item_name_to_id[iname.egg_sapphire.value] in items
        self.egg_ruby = item_name_to_id[iname.egg_ruby.value] in items
        self.egg_jade = item_name_to_id[iname.egg_jade.value] in items
        self.egg_obsidian = item_name_to_id[iname.egg_obsidian.value] in items
        self.egg_crystal = item_name_to_id[iname.egg_crystal.value] in items
        self.egg_golden = item_name_to_id[iname.egg_golden.value] in items

        self.egg_65 = item_name_to_id[iname.egg_65.value] in items

        self.firecracker_refill = len([item for item in items if item == "Firecracker Refill"])
        self.big_blue_fruit = len([item for item in items if item == "Big Blue Fruit"])

    async def write_to_game(self, process_handle, game_slot, start_address: int, ctx):

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

        # Read Opened Doors?
        # TODO find how many keys have been used
        keys_used = 0

        # Write Keys
        if self.key < 0 or self.key > 6:
            raise AssertionError("Invalid number of keys %d", self.key)
        buffer = bytes([self.key - keys_used])
        if self.key_ring:
            buffer = bytes([1])
        bytes_written = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.WriteProcessMemory(process_handle, slot_address + 0x1B1, buffer, len(buffer),
                                                         ctypes.byref(bytes_written)):
            logger.warning("Unable to write Keys")

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
        buffer = bytes([self.match - candles_lit])
        if self.matchbox:
            buffer = bytes([1])
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
        disc = bool(flags >> 5 & 1)

        # Write Owned Equipment
        bits = ("0" +
                ("1" if self.firecrackers else "0") +
                ("1" if self.flute else "0") +
                ("1" if self.lantern else "0") +
                ("1" if self.top else "0") +
                ("1" if disc else "0") +
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
        possess_m_disc = self.m_disc and (bool(flags >> 0 & 1) or ctx.first_m_disc)

        if self.m_disc:
            ctx.first_m_disc = False

        # Write Other Items
        bits = (("1" if possess_m_disc else "0") +
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
    items_handling = 0b111  # get sent remote and starting items

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
        self.game = 'ANIMAL WELL'
        self.first_m_disc = True

    async def server_auth(self, password_requested: bool = False):
        """
        Authenticate with the Archipelago server
        """
        if password_requested and not self.password:
            await super(AnimalWellContext, self).server_auth(password_requested)
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
                await ctx.items.write_to_game(ctx.process_handle, active_slot, ctx.start_address, ctx)
                await asyncio.sleep(0.1)
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
