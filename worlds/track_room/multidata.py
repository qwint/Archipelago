from __future__ import annotations

import os.path
import json
import typing
import requests
import collections


# TODO: switch these as requested
# BASE_API = "https://archipelago.gg/api/"
BASE_API = "http://localhost:8080/api/"
VERSION_API = f"{BASE_API}version"
BASE_TRACKER_API = f"{BASE_API}tracker/"
BASE_STATIC_API = f"{BASE_API}static_tracker/"
BASE_SLOTDATA_API = f"{BASE_API}slot_data_tracker/"

from Utils import KeyedDefaultDict, load_data_package_for_checksum, cache_path
from NetUtils import NetworkItem, Hint


class MultiData:
    suuid: str
    version: int
    item_id_to_name: KeyedDefaultDict[int, dict[int, str]]
    location_id_to_name: KeyedDefaultDict[int, dict[int, str]]
    slot_to_game: dict[int, str]
    game_to_checksum: dict[str, str]
    slot_names: dict[int, str]
    slot_to_locations: dict[int, list[int]]
    player_items_received: dict[int: list[NetworkItem]]
    player_locations_checked: dict[int, set[int]]
    hint_data: dict[int, list[int, int, int, int, int, str, int, int]]
    player_status: dict[int, int]
    player_alias: dict[int, str | None]
    player_slot_data: dict[int, typing.Any]

    def __init__(self, suuid: str):
        self.suuid = suuid
        self.version = self.get_tracker_version()
        self.init_static_data()
        self.item_id_to_name = KeyedDefaultDict(self.lookup_item_datapackage)
        self.location_id_to_name = KeyedDefaultDict(self.lookup_location_datapackage)
        self.init_tracker_data()
        self.init_slot_data_data()

    def get_tracker_version(self):
        with requests.get(VERSION_API) as response:
            if response.status_code != 200:
                return 1
            data = response.json()
        return int(data["tracker_api_version"])

    def init_static_data(self) -> None:
        # TODO: reimplement this
        if False and os.path.exists(os.path.join("cached_static", f"{self.suuid}.json")):
            with open(os.path.join("cached_static", f"{self.suuid}.json")) as f:
                static_data = json.load(f)
        else:
            with requests.get(BASE_STATIC_API + self.suuid) as response:
                assert response.status_code == 200
                static_data = response.json()
#            with open(os.path.join("cached_static", f"{self.suuid}.json"), "w") as f:
#                json.dump(static_data, f)

        if self.version == 1:
            self.slot_to_game: dict[int, str] = {
                obj["player"]: obj["game"]
                for obj in static_data["player_game"]
            }
            groups = {
                obj["slot"]: self.slot_to_game[obj["members"][0]]
                for obj in static_data["groups"]
            }
            self.slot_to_game.update(groups)
            if "players" not in static_data:
                self.slot_names = KeyedDefaultDict(lambda player: f"Unknown player #{player}")
            else:
                self.slot_names = {
                    obj["slot"]: obj["name"]
                    for obj in static_data["players"]
                }
            self.slot_to_locations = {}  # we don't have the info
        elif self.version == 2:
            player_data = dict(enumerate(static_data["player_data"], start=1))
            assert all(slot == data["player"] for slot, data in player_data.items()), player_data
            self.slot_to_game: dict[int, str] = {
                slot: data["game"]
                for slot, data in player_data.items()
            }
            groups = {
                # TODO
            }
            self.slot_to_game.update(groups)

            self.slot_names: dict[int, str] = {
                slot: data["name"]
                for slot, data in player_data.items()
            }
            self.slot_to_locations: dict[int, list[str]] = {
                slot: data["locations"]
                for slot, data in player_data.items()
            }
        else:
            raise Exception(f"Unknown version {self.version}")

        # datapackage key didn't change between version 1&2
        self.game_to_checksum: dict[str, str] = {
            game_name: sub_obj["checksum"]
            for game_name, sub_obj in static_data["datapackage"].items()
        }


    def lookup_item_datapackage(self, player: int):
        game = self.slot_to_game[player]
        checksum = self.game_to_checksum[game]
        lookup = load_data_package_for_checksum(checksum)["item_name_to_id"]

#        with open(os.path.join(DATAPACKAGE_CACHE, game, f"{checksum}.json")) as f:
#            lookup = json.load(f)["item_name_to_id"]
        return {item_id: name for name, item_id in lookup.items()}

    def lookup_location_datapackage(self, player: int):
        game = self.slot_to_game[player]
        checksum = self.game_to_checksum[game]
        lookup = load_data_package_for_checksum(checksum)["item_name_to_id"]

#        with open(os.path.join(DATAPACKAGE_CACHE, game, f"{checksum}.json")) as f:
#            lookup = json.load(f)["location_name_to_id"]
        return {location_id: name for name, location_id in lookup.items()}

    def init_tracker_data(self):
        with requests.get(BASE_TRACKER_API + self.suuid) as response:
            assert response.status_code == 200
            tracker_data = response.json()
        if self.version == 1:
            self.player_items_received = {
                obj["player"]: [NetworkItem(*item) for item in obj["items"]] for obj in tracker_data["player_items_received"]
                }
            self.player_locations_checked = {
                obj["player"]: obj["locations"] for obj in tracker_data["player_checks_done"]
            }
            self.hint_data = {
                obj["player"]: [Hint(*hint) for hint in obj["hints"]] for obj in tracker_data["hints"]
            }
            self.player_status = {
                obj["player"]: obj["status"] for obj in tracker_data["player_status"]
            }
            self.player_alias = dict.fromkeys([obj["player"] for obj in tracker_data["player_status"]])
            # hijack another field because we don't have aliases in this version
        elif self.version == 2:
            player_data = dict(enumerate(tracker_data["player_data"], start=1))
            self.player_items_received = {
                slot: [NetworkItem(*item) for item in data["items"]] for slot, data in player_data.items()
            }
            self.player_locations_checked = {
                slot: data["checked_locations"] for slot, data in player_data.items()
            }
            self.hint_data = {
                slot: [Hint(*hint) for hint in data["hints"]] for slot, data in player_data.items()
            }
            self.player_status = {
                slot: data["status"] for slot, data in player_data.items()
            }
            self.player_alias = {
                slot: data["alias"] for slot, data in player_data.items()
            }
        else:
            raise Exception(f"Unknown version {self.version}")

    def init_slot_data_data(self):
        with requests.get(BASE_SLOTDATA_API + self.suuid) as response:
            assert response.status_code == 200
            slot_data = response.json()
        if self.version not in (1, 2):
            raise Exception(f"Unknown version {self.version}")
        self.player_slot_data = {obj["player"]: obj["slot_data"] for obj in slot_data}

