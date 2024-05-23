from itertools import groupby
from typing import Dict, List, Set, NamedTuple
from BaseClasses import ItemClassification
from names import item_names as iname


class AnimalWellItemData(NamedTuple):
    classification: ItemClassification
    quantity_in_item_pool: int
    item_group: str = ""


item_base_id = 11553377

# todo: fill this out
# do this after the logic is all set up mostly
item_table: Dict[str, AnimalWellItemData] = {

    # Major progression items
    iname.bubble: AnimalWellItemData(ItemClassification.progression, 2, "Toys"),  # are we treating this as progressive? what's the plan here. currently 2 items for this
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
    #iname.firecrackers: AnimalWellItemData(ItemClassification.progression, 2, "Toys"),  # consideration: progressive fanny pack

    iname.m_disc: AnimalWellItemData(ItemClassification.progression, 1, "Toys"),
    iname.fanny_pack: AnimalWellItemData(ItemClassification.useful, 1, "Toys"),
    iname.match: AnimalWellItemData(ItemClassification.progression, 9, "Toys"),

    iname.e_medal: AnimalWellItemData(ItemClassification.progression, 1, "Keys"),
    iname.s_medal: AnimalWellItemData(ItemClassification.progression, 1, "Keys"),
    iname.k_shard: AnimalWellItemData(ItemClassification.progression, 3, "Keys"),
    iname.key: AnimalWellItemData(ItemClassification.progression, 6, "Keys"),
    iname.house_key: AnimalWellItemData(ItemClassification.progression, 1, "Keys"),
    iname.office_key: AnimalWellItemData(ItemClassification.progression, 1, "Keys"),

    iname.blue_flame: AnimalWellItemData(ItemClassification.progression, 1, "Flames"),
    iname.green_flame: AnimalWellItemData(ItemClassification.progression, 1, "Flames"),
    iname.violet_flame: AnimalWellItemData(ItemClassification.progression, 1, "Flames"),
    iname.purple_flame: AnimalWellItemData(ItemClassification.progression, 1, "Flames"),

    "Clover Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Gorgeous Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Magic Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Great Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Normal Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Mystic Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Razzle Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Dazzle Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Future Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Virtual Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Travel Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Rust Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Jade Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Sweet Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Desert Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Planet Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Laissez-faire Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Chaos Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Shadow Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Swan Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Evil Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Depraved Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Sour Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Upside Down Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Forbidden Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Plant Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Raw Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Reference Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Brown Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Goodnight Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Fire Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Transcendental Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Rain Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Holiday Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Truth Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Post Modern Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Bubble Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Dream Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Scarlet Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Golden Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Iridescent Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Ice Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Pickled Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Big Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Vanity Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Sweet Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Chocolate Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Value Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Red Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Orange Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Universal Basic Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Zen Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Ancient Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Moon Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Galaxy Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Sunset Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Promise Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Brick Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Neon Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Sapphire Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Ruby Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Obsidian Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Crystal Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
    "Egg As A Service": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),

    "65th Egg": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, "Eggs"),
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
