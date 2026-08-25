from __future__ import annotations

import logging

from worlds.AutoWorld import AutoWorldRegister
from worlds.tracker import DeferredEntranceMode
from worlds.tracker.TrackerCore import TrackerCore, REGEN_WORLDS  # import first so we can stop early
from .multidata import MultiData

def track_suuid(suuid: str):
    multidata = MultiData(suuid)
    relevant_players = [slot for slot, game in multidata.slot_to_game.items() if game in REGEN_WORLDS]
    print(f"not tracking {[name for slot, name in multidata.slot_names.items() if slot not in relevant_players]}")
    output = {}
    for slot in relevant_players:
        slot_data = multidata.player_slot_data[slot]
        slot_name = multidata.slot_names[slot]
        game = multidata.slot_to_game[slot]
        world_cls = AutoWorldRegister.world_types[game]

        core = TrackerCore(logging.getLogger(), print_list=False, print_count=False)
        core.enforce_deferred_connections = DeferredEntranceMode.disabled  # we can't track these
        core.set_slot_params(game, slot, slot_name, 0)  # hardcoding team
        core.initalize_tracker_core(world_cls, slot_data)  # [sic]
        core.set_missing_locations(
            set(multidata.slot_to_locations[slot]).difference(  # consider making the raw data a set
                multidata.player_locations_checked[slot]
            )
        )
        core.set_items_received(multidata.player_items_received[slot])
        state = core.updateTracker()
        output[slot_name] = state.in_logic_locations.copy()

    for player, locations in output.items():
        print(f"{player}:")
        for location in locations:
            print(f"  {location}")

if __name__ == "__main__":
    SUUID = "7uY2WJHPQwiIVPS-TtGATw"
    track_suuid(SUUID)
