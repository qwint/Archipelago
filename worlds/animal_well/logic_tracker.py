from typing import Dict, List, Set
from enum import IntEnum

from .locations import location_name_to_id
from .region_data import AWData, AWType, LocType, traversal_requirements
from .region_scripts import helper_reference
from .names import ItemNames as iname, LocationNames as lname, RegionNames as rname
from .options import (Goal, EggsNeeded, KeyRing, Matchbox, BunniesAsChecks, BunnyWarpsInLogic, CandleChecks,
                      BubbleJumping, DiscHopping, WheelHopping, WeirdTricks)


class CheckStatus(IntEnum):
    unreachable = 0
    out_of_logic = 1
    in_logic = 2
    checked = 3


class AnimalWellTracker:
    # todo: when hooking this in, have these get set based on the options sent in slot data, or read it directly
    player_options: Dict[str, int] = {
        Goal.internal_name: 0,
        EggsNeeded.internal_name: 64,
        KeyRing.internal_name: 1,
        Matchbox.internal_name: 1,
        BunniesAsChecks.internal_name: 2,
        BunnyWarpsInLogic.internal_name: 1,
        CandleChecks.internal_name: 1,
        BubbleJumping.internal_name: 2,
        DiscHopping.internal_name: 2,
        WheelHopping.internal_name: 2,
        WeirdTricks.internal_name: 1,
    }

    # key is location name, value is its spot status. Can change the key later to something else if wanted
    check_logic_status: Dict[str, int] = {loc_name: 0 for loc_name in location_name_to_id.keys()}

    # the player's current inventory, including event items, excluding eggs
    full_inventory: Set[str] = set()
    egg_count: int = 0
    upgraded_b_wand: bool = False
    has_all_keys: bool = False
    has_all_matches: bool = False

    regions_in_logic: Set[str] = [rname.menu]
    # includes regions accessible in logic
    regions_out_of_logic: Set[str] = [rname.menu]

    # update check_logic_status and the regions logic status
    # set in_logic to True for regions_in_logic, False for regions_out_of_logic
    def update_spots_status(self, in_logic: bool) -> None:
        regions_set = self.regions_in_logic if in_logic else self.regions_out_of_logic
        region_count = len(regions_set)
        for origin, destinations in traversal_requirements.items():
            if origin not in regions_set:
                continue
            for destination_name, destination_data in destinations.items():
                if destination_data.type == AWType.region:
                    if destination_name in regions_set:
                        continue
                    # if it's a bunny warp, bunny warps in logic is off, and we're updating the in logic regions
                    if (destination_data.bunny_warp and in_logic
                            and not self.player_options[BunnyWarpsInLogic.internal_name]):
                        continue
                # bools are ints
                if destination_data.type == AWType.location:
                    if self.check_logic_status[destination_name] >= 1 + in_logic:
                        continue
                    # skip bunnies that aren't included in the location pool
                    if (destination_data.loc_type == LocType.bunny
                        and (self.player_options[BunniesAsChecks.internal_name] == BunniesAsChecks.option_off
                             or (self.player_options[BunniesAsChecks.internal_name] == BunniesAsChecks.option_exclude_tedious
                                 and destination_name in [lname.bunny_mural, lname.bunny_dream,
                                                          lname.bunny_uv, lname.bunny_lava]))):
                        continue

                met: bool = False
                for req_list in destination_data.rules:
                    # if the rules for this spot are just [[]] (the default), then met is aleady true
                    if len(req_list) == 0:
                        met = True
                        break
                    # todo: make sure this actually works
                    if set(req_list).issubset(self.full_inventory):
                        met = True
                        break

                if self.egg_count < destination_data.eggs_required:
                    met = False

                if met:
                    if destination_data.type == AWType.region:
                        regions_set.add(destination_name)
                    elif destination_data.type == AWType.location:
                        self.check_logic_status[destination_name] = CheckStatus.out_of_logic + in_logic
        # if the length of the region set changed, loop through again
        if region_count != len(regions_set):
            self.update_spots_status(in_logic)

    def update_inventory_with_events(self) -> None:
        for origin, destinations in traversal_requirements.items():
            for destination_name, destination_data in destinations.items():
                if destination_data.event and self.check_logic_status[destination_name] == CheckStatus.checked:
                    self.full_inventory.add(destination_data.event)

    def put_logic_items_in_inventory(self) -> None:
        # hacky but whatever
        if self.upgraded_b_wand:
            self.full_inventory.add(iname.bubble_long_real)
        if self.has_all_keys:
            self.full_inventory.add(iname.key_ring)
        if self.has_all_matches:
            self.full_inventory.add(iname.matchbox)

        if iname.bubble_long_real in self.full_inventory:
            self.full_inventory.add(iname.bubble_short)
            self.full_inventory.add(iname.bubble_long)
        elif iname.bubble in self.full_inventory:
            if self.player_options[BubbleJumping.internal_name] >= BubbleJumping.option_exclude_long_chains:
                self.full_inventory.add(iname.bubble_short)
            if self.player_options[BubbleJumping.internal_name] >= BubbleJumping.option_on:
                self.full_inventory.add(iname.bubble_long)

        if iname.wheel in self.full_inventory:
            if self.player_options[WheelHopping.internal_name] >= WheelHopping.option_simple:
                self.full_inventory.add(iname.wheel_hop)
                self.full_inventory.add(iname.wheel_climb)
            if self.player_options[WheelHopping.internal_name] >= WheelHopping.option_advanced:
                self.full_inventory.add(iname.wheel_hard)

        # this is temporary -- remove if we detect when the player has traded the mock disc for the real disc
        if iname.m_disc in self.full_inventory:
            self.full_inventory.add(iname.disc)

        if iname.disc in self.full_inventory:
            if self.player_options[DiscHopping.internal_name] >= DiscHopping.option_single:
                self.full_inventory.add(iname.disc_hop)
            if self.player_options[DiscHopping.internal_name] >= DiscHopping.option_multiple:
                self.full_inventory.add(iname.disc_hop_hard)

        if self.player_options[WeirdTricks.internal_name]:
            self.full_inventory.add(iname.weird_tricks)
            self.full_inventory.add(iname.tanking_damage)

        for helper_name, items in helper_reference.items():
            for item in items:
                if item in self.full_inventory:
                    self.full_inventory.add(helper_name)
                    break

    def update_checks_and_regions(self) -> None:
        self.put_logic_items_in_inventory()
        self.update_inventory_with_events()
        self.update_spots_status(in_logic=True)
        self.update_spots_status(in_logic=False)
