from itertools import groupby
from typing import Dict, List, Set, NamedTuple
from BaseClasses import ItemClassification
from .names import item_names as iname


class AnimalWellItemData(NamedTuple):
    classification: ItemClassification
    quantity_in_item_pool: int
    item_group: str = ""


item_base_id = 11553377

# todo: fill this out
# do this after the logic is all set up mostly
item_table: Dict[str, AnimalWellItemData] = {

    # Major progression items
    iname.bubble: AnimalWellItemData(ItemClassification.progression, 2, "Toys"),  # progressive
    iname.disc: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    iname.yoyo: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    iname.slink: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    iname.flute: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    iname.top: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    iname.lantern: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    iname.uv: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    iname.ball: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    iname.remote: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    iname.wheel: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    # iname.firecrackers: AnimalWellItemData(ItemClassification.progression, 2, "Toys"),

    iname.m_disc: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    iname.fanny_pack: AnimalWellItemData(ItemClassification.useful, 1, "Toys"),

    iname.match: AnimalWellItemData(ItemClassification.progression, 9, "Toys"),

    iname.key: AnimalWellItemData(ItemClassification.progression, 6, "Keys"),
    iname.house_key: AnimalWellItemData(ItemClassification.progression, 1, "Keys"),
    iname.office_key: AnimalWellItemData(ItemClassification.progression, 1, "Keys"),

    iname.e_medal: AnimalWellItemData(ItemClassification.progression, 1, "Keys"),
    iname.s_medal: AnimalWellItemData(ItemClassification.progression, 1, "Keys"),
    iname.k_shard: AnimalWellItemData(ItemClassification.progression, 3, "Keys"),

    iname.blue_flame: AnimalWellItemData(ItemClassification.progression, 1, "Flames"),
    iname.green_flame: AnimalWellItemData(ItemClassification.progression, 1, "Flames"),
    iname.violet_flame: AnimalWellItemData(ItemClassification.progression, 1, "Flames"),
    iname.pink_flame: AnimalWellItemData(ItemClassification.progression, 1, "Flames"),

    # todo: reorder this so it's the same order as locations.py

    iname.egg_reference: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_brown: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_raw: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_pickled: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_big: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_swan: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_forbidden: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_shadow: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_vanity: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_service: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),

    iname.egg_depraved: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_chaos: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_upside_down: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_evil: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_sweet: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_chocolate: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_value: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_plant: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_red: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_orange: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_sour: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_post_modern: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),

    iname.egg_universal: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_lf: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_zen: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_future: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_friendship: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_truth: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_transcendental: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_ancient: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_magic: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_mystic: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_holiday: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_rain: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_razzle: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_dazzle: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),

    iname.egg_virtual: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_normal: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_great: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_gorgeous: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_planet: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_moon: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_galaxy: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_sunset: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_goodnight: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_dream: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_travel: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_promise: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_ice: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_fire: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),

    iname.egg_bubble: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_desert: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_clover: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_brick: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_neon: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_iridescent: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_rust: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_scarlet: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_sapphire: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_ruby: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_jade: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_obsidian: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_crystal: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    iname.egg_golden: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),

    iname.egg_65: AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
}

item_name_to_id: Dict[str, int] = {name: item_base_id + data.item_id_offset for name, data in item_table.items()}

filler_items: List[str] = [name for name, data in item_table.items() if data.classification == ItemClassification.filler]


def get_item_group(item_name: str) -> str:
    return item_table[item_name].item_group


item_name_groups: Dict[str, Set[str]] = {
    group: set(item_names) for group, item_names in groupby(sorted(item_table, key=get_item_group), get_item_group) if group != ""
}

# extra groups for the purpose of aliasing items
extra_groups: Dict[str, Set[str]] = {
    "Laurels": {"Hero's Laurels"},
    "Orb": {"Magic Orb"},
    "Dagger": {"Magic Dagger"},
    "Wand": {"Magic Wand"},
    "Magic Rod": {"Magic Wand"},
    "Fire Rod": {"Magic Wand"},
    "Holy Cross": {"Pages 42-43 (Holy Cross)"},
    "Prayer": {"Pages 24-25 (Prayer)"},
    "Icebolt": {"Pages 52-53 (Icebolt)"},
    "Ice Rod": {"Pages 52-53 (Icebolt)"},
    "Melee Weapons": {"Stick", "Sword", "Sword Upgrade"},
    "Progressive Sword": {"Sword Upgrade"},
    "Abilities": {"Pages 24-25 (Prayer)", "Pages 42-43 (Holy Cross)", "Pages 52-53 (Icebolt)"},
    "Questagons": {"Red Questagon", "Green Questagon", "Blue Questagon", "Gold Questagon"},
    "Ladder to Atoll": {"Ladder to Ruined Atoll"},  # fuzzy matching made it hint Ladders in Well, now it won't
    "Ladders to Bell": {"Ladders to West Bell"},
    "Ladders to Well": {"Ladders in Well"},  # fuzzy matching decided ladders in well was ladders to west bell
}

item_name_groups.update(extra_groups)
