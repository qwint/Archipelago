from typing import Dict, List, Any, Tuple, TypedDict
from BaseClasses import Region, Location, Item, Tutorial, ItemClassification, MultiWorld
from .items import item_name_to_id, item_table, item_name_groups, filler_items
from .locations import location_table, location_name_groups, location_name_to_id
from .regions import traversal_requirements
from .options import AnimalWellOptions
from worlds.AutoWorld import WebWorld, World


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


class AnimalWellItem(Item):
    game: str = "ANIMAL WELL"


class AnimalWellLocation(Location):
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
    slot_data_items: List[AnimalWellItem]

    def generate_early(self) -> None:
        # Universal tracker stuff, shouldn't do anything in standard gen
        if hasattr(self.multiworld, "re_gen_passthrough"):
            if "ANIMAL WELL" in self.multiworld.re_gen_passthrough:
                passthrough = self.multiworld.re_gen_passthrough["ANIMAL WELL"]
                self.options.goal.value = passthrough["goal"]

    def create_item(self, name: str) -> AnimalWellItem:
        item_data = item_table[name]
        return AnimalWellItem(name, item_data.classification, self.item_name_to_id[name], self.player)

    def create_items(self) -> None:
        aw_items: List[AnimalWellItem] = []

        items_to_create: Dict[str, int] = {item: data.quantity_in_item_pool for item, data in item_table.items()}

        self.multiworld.itempool += aw_items

    def create_regions(self) -> None:
        pass  # will do this later on when I have the effort

    def set_rules(self) -> None:
        pass  # will do this later on, might do it in create_regions

    def get_filler_item_name(self) -> str:
        return self.random.choice(filler_items)

    def fill_slot_data(self) -> Dict[str, Any]:
        return self.options.as_dict(
            "goal",
            "65th_egg_location"
            "eggs_needed",
            "bunnies_as_checks",
            "candle_checks",
            "bubble_jumping",
            "disc_riding",
        )

    # for the universal tracker, doesn't get called in standard gen
    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        # returning slot_data so it regens, giving it back in multiworld.re_gen_passthrough
        return slot_data
