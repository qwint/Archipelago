from typing import Dict, List, Any, Tuple, TypedDict
from BaseClasses import Region, Location, Item, Tutorial, ItemClassification, MultiWorld
from .items import item_name_to_id, item_table, item_name_groups, filler_items
from .locations import location_table, location_name_groups, location_name_to_id
from .rules import create_regions_and_set_rules
from .options import AnimalWellOptions, aw_option_groups
from .names import ItemNames
from worlds.AutoWorld import WebWorld, World
# todo: remove animal_well_map.pdn


class AnimalWellWeb(WebWorld):
    tutorials = [
        Tutorial(
            tutorial_name="Multiworld Setup Guide",
            description="A guide to setting up the ANIMAL WELL Randomizer for Archipelago multiworld games.",
            language="English",
            file_name="setup_en.md",
            link="setup/en",
            authors=["Scipio Wright"]
        )
    ]
    theme = "jungle"
    game = "ANIMAL WELL"
    option_groups = aw_option_groups


class AWItem(Item):
    game: str = "ANIMAL WELL"


class AnimalWellWorld(World):
    """
    Hatch from your flower and spelunk through the beautiful and sometimes haunting world of ANIMAL WELL, a pixelated
    action-exploration game rendered in intricate audio and visual detail. Encounter lively creatures small and large,
    helpful and ominous as you discover unconventional upgrades and unravel the well’s secrets.
    """
    game = "ANIMAL WELL"
    web = AnimalWellWeb()

    options: AnimalWellOptions
    options_dataclass = AnimalWellOptions
    item_name_groups = item_name_groups
    location_name_groups = location_name_groups

    item_name_to_id = item_name_to_id
    location_name_to_id = location_name_to_id

    ability_unlocks: Dict[str, int]
    slot_data_items: List[AWItem]

    def generate_early(self) -> None:
        # Universal tracker stuff, shouldn't do anything in standard gen
        if hasattr(self.multiworld, "re_gen_passthrough"):
            if "ANIMAL WELL" in self.multiworld.re_gen_passthrough:
                passthrough = self.multiworld.re_gen_passthrough["ANIMAL WELL"]
                self.options.goal.value = passthrough["goal"]
                self.options.eggs_needed.value = passthrough["eggs_needed"]
                self.options.key_ring.value = passthrough["key_ring"]
                self.options.matchbox.value = passthrough["matchbox"]
                self.options.evil_egg_location = self.options.evil_egg_location.option_randomized
                self.options.bunnies_as_checks.value = passthrough["bunnies_as_checks"]
                self.options.candle_checks.value = passthrough["candle_checks"]
                self.options.bubble_jumping.value = passthrough["bubble_jumping"]
                self.options.disc_riding.value = passthrough["disc_riding"]
                self.options.wheel_hopping.value = passthrough["wheel_hopping"]

    def create_item(self, name: str) -> AWItem:
        item_data = item_table[name]
        return AWItem(name, item_data.classification, self.item_name_to_id[name], self.player)

    def create_items(self) -> None:
        aw_items: List[AWItem] = []

        # if we ever shuffle firecrackers, remove this
        self.multiworld.push_precollected(self.create_item(ItemNames.firecrackers))

        items_to_create: Dict[str, int] = {item: data.quantity_in_item_pool for item, data in item_table.items()}

        if self.options.key_ring:
            items_to_create["Key"] = 0
            items_to_create["Key Ring"] = 1

        if self.options.matchbox:
            items_to_create["Match"] = 0
            items_to_create["Matchbox"] = 1

        # if there are more locations than items, add filler until there are enough items
        filler_count = len(self.multiworld.get_unfilled_locations(self.player)) - len(aw_items)
        for _ in range(filler_count):
            items_to_create[self.get_filler_item_name()] += 1

        for item_name, quantity in items_to_create.items():
            for _ in range(quantity):
                aw_item: AWItem = self.create_item(item_name)
                aw_items.append(aw_item)

        self.multiworld.itempool += aw_items

    def create_regions(self) -> None:
        create_regions_and_set_rules(self)

    def set_rules(self) -> None:
        pass  # will do this later on, might do it in create_regions

    def get_filler_item_name(self) -> str:
        return self.random.choice(filler_items)

    def fill_slot_data(self) -> Dict[str, Any]:
        return self.options.as_dict(
            "goal",
            "65th_egg_location"
            "eggs_needed",
            "key_ring",
            "matchbox",
            "bunnies_as_checks",
            "candle_checks",
            "bubble_jumping",
            "disc_riding",
            "wheel_hopping",
        )

    # for the universal tracker, doesn't get called in standard gen
    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        # returning slot_data so it regens, giving it back in multiworld.re_gen_passthrough
        return slot_data
