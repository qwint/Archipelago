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

    def read_from_game(self):
        pass

    def write_to_archipelago(self):
        pass


class Items:
    """
    The items the player has received
    """

    def __init__(self):
        pass

    def read_from_archipelago(self):
        pass

    def write_to_game(self):
        pass


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

        version = int.from_bytes(buffer.value, "little")
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
        locations.read_from_game()
        locations.write_to_archipelago()
        items.read_from_archipelago()
        items.write_to_game()

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
