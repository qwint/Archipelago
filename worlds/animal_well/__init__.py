from typing import Dict, List, Any
from copy import deepcopy
from BaseClasses import Tutorial
from .items import item_name_to_id, item_table, item_name_groups, filler_items, AWItem
from .locations import location_name_groups, location_name_to_id
from .region_data import AWData, traversal_requirements
from .region_scripts import create_regions_and_set_rules
from .options import AnimalWellOptions, aw_option_presets  # , aw_option_groups
from .names import ItemNames, LocationNames
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import Component, components, icon_paths, launch_subprocess, Type
from Utils import local_path
# todo: remove animal_well_map.pdn


def launch_client():
    """
    Launch the Animal Well Client
    """
    from .client import launch
    launch_subprocess(launch, name="AnimalWellClient")


components.append(Component("ANIMAL WELL Client", "AnimalWellClient", func=launch_client,
                            component_type=Type.CLIENT, icon='Potate'))

icon_paths['Potate'] = local_path('data', 'Potate.png')


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
    # option_groups = aw_option_groups
    option_presets = aw_option_presets


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

    topology_present = True

    traversal_requirements: Dict[str, Dict[str, AWData]]

    def generate_early(self) -> None:
        # Universal tracker stuff, shouldn't do anything in standard gen
        if hasattr(self.multiworld, "re_gen_passthrough"):
            if "ANIMAL WELL" in self.multiworld.re_gen_passthrough:
                passthrough = self.multiworld.re_gen_passthrough["ANIMAL WELL"]
                self.options.goal.value = passthrough["goal"]
                self.options.eggs_needed.value = passthrough["eggs_needed"]
                self.options.key_ring.value = passthrough["key_ring"]
                self.options.matchbox.value = passthrough["matchbox"]
                self.options.final_egg_location = self.options.final_egg_location.option_randomized
                self.options.bunnies_as_checks.value = passthrough["bunnies_as_checks"]
                self.options.candle_checks.value = passthrough["candle_checks"]
                self.options.bubble_jumping.value = passthrough["bubble_jumping"]
                self.options.disc_hopping.value = passthrough["disc_hopping"]
                self.options.wheel_hopping.value = passthrough["wheel_hopping"]
                self.options.weird_tricks.value = passthrough["weird_tricks"]

    def create_regions(self) -> None:
        self.traversal_requirements = deepcopy(traversal_requirements)
        create_regions_and_set_rules(self)

    def create_item(self, name: str) -> AWItem:
        item_data = item_table[name]
        return AWItem(name, item_data.classification, self.item_name_to_id[name], self.player)

    def create_items(self) -> None:
        aw_items: List[AWItem] = []

        # if we ever shuffle firecrackers, remove this
        self.multiworld.push_precollected(self.create_item(ItemNames.firecrackers))

        items_to_create: Dict[str, int] = {item: data.quantity_in_item_pool for item, data in item_table.items()}

        if self.options.goal == self.options.goal.option_fireworks:
            items_to_create[ItemNames.house_key] = 0
            self.get_location(LocationNames.key_house).place_locked_item(self.create_item(ItemNames.house_key))

        if self.options.key_ring:
            items_to_create[ItemNames.key] = 0
            items_to_create[ItemNames.key_ring] = 1

        if self.options.matchbox:
            items_to_create[ItemNames.match] = 0
            items_to_create[ItemNames.matchbox] = 1

        # if self.options.final_egg_location or self.options.goal == self.options.goal.option_egg_hunt:
        #     items_to_create[ItemNames.egg_65] = 0
        #     self.get_location(LocationNames.egg_65).place_locked_item(self.create_item(ItemNames.egg_65))

        for item_name, quantity in items_to_create.items():
            for _ in range(quantity):
                aw_item: AWItem = self.create_item(item_name)
                aw_items.append(aw_item)

        # if there are more locations than items, add filler until there are enough items
        filler_count = len(self.multiworld.get_unfilled_locations(self.player)) - len(aw_items)
        for _ in range(filler_count):
            aw_items.append(self.create_item(self.get_filler_item_name()))

        self.multiworld.itempool += aw_items

    def get_filler_item_name(self) -> str:
        return self.random.choice(filler_items)

    def fill_slot_data(self) -> Dict[str, Any]:
        # todo: remove this, remove the changes done to Utils
        # import Utils
        # state = self.multiworld.get_all_state(False)
        # state.update_reachable_regions(self.player)
        # Utils.visualize_regions(self.multiworld.get_region("Menu", self.player), "awtest.puml",
        #                         show_entrance_names=True,
        #                         highlight_regions=state.reachable_regions[self.player])
        return self.options.as_dict(
            "goal",
            "eggs_needed",
            "key_ring",
            "matchbox",
            "bunnies_as_checks",
            "candle_checks",
            "bubble_jumping",
            "disc_hopping",
            "wheel_hopping",
            "weird_tricks",
        )

    # for the universal tracker, doesn't get called in standard gen
    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        # returning slot_data so it regens, giving it back in multiworld.re_gen_passthrough
        return slot_data
