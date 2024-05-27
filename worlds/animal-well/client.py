"""
Animal Well Archipelago Client
"""

import argparse
import ctypes
import logging
import platform
import struct
import subprocess
import sys


class Locations:
    """
    The checks the player has found
    """

    def __init__(self):
        # major items
        self.b_wand_chest = False
        self.bb_wand_chest = False
        # self.disc_spot = False
        self.yoyo_chest = False
        self.slink_chest = False
        self.flute_chest = False
        self.top_chest = False
        self.lantern_chest = False
        self.uv_lantern_chest = False
        self.b_ball_chest = False
        self.remote_chest = False
        self.wheel_chest = False
        # self.firecracker_first = False

        # self.mock_disc_chest = False  # TODO possession logic
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

        # self.key_bear_lower = False  # TODO find out how many doors have been unlocked
        # self.key_bear_upper = False  # TODO find out how many doors have been unlocked
        # self.key_chest_mouse_head_lever = False  # TODO find out how many doors have been unlocked
        # self.key_frog_guard_room_west = False  # TODO find out how many doors have been unlocked
        # self.key_frog_guard_room_east = False  # TODO find out how many doors have been unlocked
        # self.key_dog = False  # TODO find out how many doors have been unlocked
        # self.key_house = False
        # self.key_office = False

        self.medal_e = False
        self.medal_s = False
        # self.medal_k = False  # TODO K shard logic

        # self.flame_blue = False
        # self.flame_green = False
        # self.flame_violet = False
        # self.flame_pink = False

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

        # all locations beyond this point have no corresponding item in the item pool
        # self.map_chest = False
        # self.stamp_chest = False
        # self.pencil_chest = False
        # self.mama_cha = False
        # self.squirrel_acorn = False

        # bnnnnuyuy
        # self.bunny_barcode = False
        # self.bunny_chinchilla_vine = False
        # self.bunny_crow = False
        # self.bunny_disc_spike = False
        # self.bunny_dream = False
        # self.bunny_duck = False
        # self.bunny_face = False
        # self.bunny_file_bud = False
        # self.bunny_fish = False
        # self.bunny_ghost_dog = False
        # self.bunny_lava = False
        # self.bunny_map = False
        # self.bunny_mural = False
        # self.bunny_tv = False
        # self.bunny_uv = False
        # self.bunny_water_spike = False

    def read_from_game(self, process_handle, game_slot, start_address: int):
        """
        Read checked locations from the process
        """
        slot_address = start_address + 0x18 + (0x27010 * (game_slot - 1))

        # Read Chests
        buffer_size = 8
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x120, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logging.error("Unable to read Chests")
            return
        flags = bytearray(struct.unpack('Q', buffer)[0].to_bytes(8, byteorder="little"))

        buffer_size = 8
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x128, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logging.error("Unable to read Chests")
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

    def write_to_archipelago(self):
        """
        Write checked locations to archipelago
        """
        # TODO
        pass


class Items:
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
        # self.m_disc = False  # TODO possession logic
        self.fanny_pack = False

        self.match = 0
        # self.matchbox = False

        # self.key = 0  # TODO find out how many doors have been unlocked
        # self.keyring = False
        self.house_key = False
        self.office_key = False

        self.e_medal = False
        self.s_medal = False
        # self.k_shard = 0  # TODO K shard logic

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

        # self.firecracker_refill = 0
        # self.big_blue_fruit = 0

    def read_from_archipelago(self):
        """
        Read inventory state from archipelago
        """
        # TODO
        pass

    def write_to_game(self, process_handle, game_slot, start_address: int):
        """
        Write inventory state to the process
        """
        slot_address = start_address + 0x18 + (0x27010 * (game_slot - 1))

        # Read Quest State
        buffer_size = 4
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x1EC, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logging.error("Unable to read Quest State")
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
            logging.warning("Unable to write Quest State")

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
            logging.warning("Unable to write Eggs")

        # Read Candles Lit
        buffer_size = 2
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x1E0, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logging.error("Unable to read Candles Lit")
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
            logging.warning("Unable to write Matches")

        # Read Owned Equipment
        buffer_size = 2
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x1DC, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logging.error("Unable to read Owned Equipment")
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
            logging.warning("Unable to write Owned Equipment")

        # Read Other Items
        buffer_size = 1
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, slot_address + 0x1DE, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logging.error("Unable to read Other Items")
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
            logging.warning("Unable to write Other Items")


def _get_process_handle():
    """
    Get the process handle of Animal Well
    """
    if platform.uname()[0] == "Windows":
        logging.debug("Getting process handle on Windows")

        # https://stackoverflow.com/a/67788291 ##
        pid_list = []
        command = subprocess.Popen(['tasklist', '/FI', f'IMAGENAME eq Animal Well.exe', '/fo', 'CSV'],
                                   stdout=subprocess.PIPE)
        msg = command.communicate()
        output = str(msg[0])
        if 'INFO' not in output:
            output_list = output.split("Animal Well.exe")
            for i in range(1, len(output_list)):
                j = int(output_list[i].replace("\"", '')[1:].split(',')[0])
                if j not in pid_list:
                    pid_list.append(j)
        #########################################

        if len(pid_list) != 1:
            raise AssertionError(f"There are {len(pid_list)} Animal Wells running when there should be 1")

        logging.debug("Found PID %d", pid_list[0])
        return ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid_list[0])
    else:
        raise NotImplementedError("Only Windows is implemented right now")


def _close_process_handle(process_handle):
    """
    Close the process handle of Animal Well
    """
    if platform.uname()[0] == "Windows":
        logging.debug("Closing process handle on Windows")
        ctypes.windll.kernel32.CloseHandle(process_handle)
    else:
        raise NotImplementedError("Only Windows is implemented right now")


def _assert_version(process_handle, start_address: int):
    """
    Make sure the Animal Well version is the one we support
    """
    if platform.uname()[0] == "Windows":
        logging.debug("Checking Animal Well version number on Windows")

        buffer_size = 4
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, start_address, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            raise RuntimeError("Unable to read memory")
        version = struct.unpack('I', buffer)[0]
        logging.debug("Found version number %d", version)

        if version != 9:
            raise AssertionError(f"Animal Well version {version} detected, only version 9 supported")
    else:
        raise NotImplementedError("Only Windows is implemented right now")


def client(server_url: str, slot_name: str, game_slot: int, start_address: int, password: str | None, **kwargs) -> int:
    """
    The main loop of the client
    """
    del kwargs

    logging.info("Connecting to Archipelago at %s and slot name %s", server_url, slot_name)
    # TODO

    process_handle = _get_process_handle()
    _assert_version(process_handle, start_address)

    locations = Locations()
    items = Items()
    while True:
        try:
            locations.read_from_game(process_handle, game_slot, start_address)
            locations.write_to_archipelago()
            items.read_from_archipelago()
            items.write_to_game(process_handle, game_slot, start_address)
        except KeyboardInterrupt:
            break

    _close_process_handle(process_handle)
    return 0


def main() -> int:
    """
    Main function of Animal Well Archipelago Client
    """
    parser = argparse.ArgumentParser(
        prog="Animal Well Archipelago Client",
        description="Connects a running Animal Well game to an Archipelago server"
    )

    parser.add_argument("server_url",
                        type=str,
                        help="The URL of the archipelago server, usually something like 'archipelago.gg:12345"
                        )
    parser.add_argument("slot_name",
                        type=str,
                        help="The name of your slot"
                        )
    parser.add_argument("game_slot",
                        type=int,
                        choices=[1, 2, 3],
                        help="The slot number in Animal Well"
                        )
    parser.add_argument("start_address",
                        type=int,
                        help="The start of memory in the running process (will be removed eventually)"
                        )
    parser.add_argument("-p", "--password",
                        default=None,
                        type=str,
                        required=False,
                        help="The password for the archipelago server"
                        )
    parser.add_argument("-l", "--log_level",
                        default="INFO",
                        type=str,
                        required=False,
                        help="The logging level"
                        )
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())
    logging.info("Log Level set to %s", args.log_level.upper())

    return client(**vars(args))


if __name__ == "__main__":
    sys.exit(main())
