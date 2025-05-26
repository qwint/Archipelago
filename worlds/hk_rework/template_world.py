from BaseClasses import Region, Location, Item, ItemClassification, CollectionState
from typing import Any, Callable, ClassVar


class RandomizerCoreWorld:
    # location_name_to_id = {
    #     name: index for index, name in enumerate([location["name"] for location in locations], base_id)
    # }
    # item_name_to_id = {name: index for index, name in enumerate([item["name"] for item in item_table], base_id)}
    rc_regions: ClassVar[list[dict[str, Any]]] = {}
    rc_locations: ClassVar[list[dict[str, Any]]] = {}
    item_class = Item
    location_class = Location
    region_class = Region

    def get_region_list(self) -> list[str]:
        return [region["name"] for region in self.rc_regions]

    def get_connections(self) -> list[tuple[str, str, Any | None]]:
        return [
            (region["name"], exit["target"], exit["logic"])
            for region in self.rc_regions for exit in region["exits"]
            ]

    def get_location_map(self) -> list[tuple[str, str, Any | None]]:
        rule_lookup = {location["name"]: location["logic"] for location in self.rc_locations}
        return [
            (region["name"], location, rule_lookup[location])
            for region in self.rc_regions for location in region["locations"]
            ]

# # black box methods
    def set_victory(self) -> None:
        """Called at the end of create_regions() to set self.multiworld.completion_condition[self.player]"""
        pass

    def create_rule(self, rule: Any) -> Callable[[CollectionState], bool]:
        """Used to parse the logic format into an access_rule for Entrances and Locations."""
        return staticmethod(lambda state: True)

    def get_item_list(self) -> list[str]:
        """
        Called by create_items() to get a full list of item names to create for the world.
        Items sould be added to the list multiple times if you need multiple copies,
        and any alterations to the items in the pool based on options should be done here as well.
        """
        return []

    def get_item_classification(self, name: str) -> ItemClassification:
        """Used to get the Item Classification by name for every item added to the Multiworld"""
        return ItemClassification.progression

# common methods
    def create_regions(self) -> None:
        # create a local map of get_region_list names to region object for referencing in create_regions
        # and adding those regions to the multiworld
        regions = dict.fromkeys(self.get_region_list(), None)
        for region in regions.keys():
            regions[region] = self.region_class(region, self.player, self.multiworld)
            self.multiworld.regions.append(regions[region])

        # loop through get_region_map, adding the rules per self.create_rule(rule) if present to the connections
        for region1, region2, rule in self.get_connections():
            ent = regions[region1].connect(regions[region2])
            if rule:
                self.set_rule(ent, self.create_rule(rule))

        # loop through get_location_map, adding the rules per self.create_rule(rule) if present to the location
        for region, location, rule in self.get_location_map():
            code = self.location_name_to_id.get(location, None)
            loc = self.location_class(self.player, location, code, regions[region])
            if rule:
                self.set_rule(loc, self.create_rule(rule))
            if not code:
                loc.place_locked_item(self.item_class(location, ItemClassification.progression, None, self.player))
                loc.show_in_spoiler = False
            regions[region].locations.append(loc)

        self.set_victory()

    def set_rule(self, spot, rule):
        """override for alternative access_rule formats"""
        spot.access_rule = rule

    def set_rules(self):
        pass

    def create_items(self) -> int:
        # create all items in get_item_list()
        itempool = []
        for item in self.get_item_list():
            itempool.append(self.create_item(item))

        # fill in any difference in itempool with filler item and submit to multiworld
        total_locations = len(self.multiworld.get_unfilled_locations(self.player))
        while len(itempool) < total_locations:
            itempool.append(self.create_filler())
        self.multiworld.itempool += itempool
        return len(itempool)

    def create_item(self, name: str) -> "Item":
        classification = self.get_item_classification(name)
        return self.item_class(name, classification, self.item_name_to_id.get(name, None), self.player)
