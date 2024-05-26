"""
Animal Well Archipelago Client
"""

import argparse
import ctypes
import logging
import platform
import subprocess
import sys

START_ADDRESS = 0x10A88440


class Locations:
    """
    The checks the player has found
    """

    def __init__(self):
        pass

    def read_from_game(self, process_handle, game_slot):
        """
        Read checked locations from the process
        """
        # TODO
        pass

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
        self.bubble = 0
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

        # self.key = 0  # TODO find out how many doors have been unlocked
        self.house_key = False
        self.office_key = False

        self.e_medal = False
        self.s_medal = False
        # self.k_shard = 0  # TODO K shard logic

        # self.blue_flame = False  # TODO flame logic
        # self.green_flame = False  # TODO flame logic
        # self.violet_flame = False  # TODO flame logic
        # self.pink_flame = False  # TODO flame logic

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

    def read_from_archipelago(self):
        """
        Read inventory state from archipelago
        """
        # TODO
        pass

    def write_to_game(self, process_handle, game_slot):
        """
        Write inventory state to the process
        """
        slot_address = START_ADDRESS + 0x18 + (0x27010 * (game_slot - 1))

        # Read Quest State
        buffer_size = 4
        buffer = ctypes.c_char_p(b"1" * buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, START_ADDRESS + 0x1EC, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logging.error("Unable to read Quest State")
            return
        flags = int.from_bytes(buffer.value, "little")
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
        buffer = ctypes.c_char_p(b"1" * buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, START_ADDRESS + 0x1E0, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logging.error("Unable to read Candles Lit")
            return
        flags = int.from_bytes(buffer.value, "little")
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
        buffer = ctypes.c_char_p(b"1" * buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, START_ADDRESS + 0x1DC, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logging.error("Unable to read Owned Equipment")
            return
        flags = int.from_bytes(buffer.value, "little")

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
        buffer = ctypes.c_char_p(b"1" * buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, START_ADDRESS + 0x1DE, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            logging.error("Unable to read Other Items")
            return
        flags = int.from_bytes(buffer.value, "little")

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


def _assert_version(process_handle):
    """
    Make sure the Animal Well version is the one we support
    """
    if platform.uname()[0] == "Windows":
        logging.debug("Checking Animal Well version number on Windows")

        buffer_size = 4
        buffer = ctypes.c_char_p(b"1" * buffer_size)
        bytes_read = ctypes.c_ulong(0)
        if not ctypes.windll.kernel32.ReadProcessMemory(process_handle, START_ADDRESS, buffer, buffer_size,
                                                        ctypes.byref(bytes_read)):
            raise RuntimeError("Unable to read memory")

        version = int.from_bytes(buffer.value, byteorder="little")
        logging.debug("Found version number %d", version)

        if version != 9:
            raise AssertionError(f"Animal Well version {version} detected, only version 9 supported")
    else:
        raise NotImplementedError("Only Windows is implemented right now")


def client(server_url: str, slot_name: str, game_slot: int, password: str | None, **kwargs) -> int:
    """
    The main loop of the client
    """
    del kwargs

    logging.info("Connecting to Archipelago at %s and slot name %s", server_url, slot_name)
    # TODO

    process_handle = _get_process_handle()
    _assert_version(process_handle)

    locations = Locations()
    items = Items()
    while True:
        try:
            locations.read_from_game(process_handle, game_slot)
            locations.write_to_archipelago()
            items.read_from_archipelago()
            items.write_to_game(process_handle, game_slot)
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
