from itertools import groupby
from typing import Dict, List, Set, NamedTuple
from BaseClasses import ItemClassification, Item
from .names import ItemNames as iname
IClass = ItemClassification  # just to make the lines shorter


class AWItem(Item):
    game: str = "ANIMAL WELL"


class AWItemData(NamedTuple):
    classification: ItemClassification
    quantity_in_item_pool: int  # put 0 for things not in the pool by default
    offset: int
    item_group: str = ""


item_base_id = 11553377

item_table: Dict[str, AWItemData] = {
    # Major progression items
    iname.bubble: AWItemData(IClass.progression | IClass.useful, 2, 0, "Toys"),  # progressive
    # iname.disc: AWItemData(IClass.progression | IClass.useful, 1, 1, "Toys"),
    iname.yoyo: AWItemData(IClass.progression | IClass.useful, 1, 2, "Toys"),
    iname.slink: AWItemData(IClass.progression | IClass.useful, 1, 3, "Toys"),
    iname.flute: AWItemData(IClass.progression | IClass.useful, 1, 4, "Toys"),
    iname.top: AWItemData(IClass.progression | IClass.useful, 1, 5, "Toys"),
    iname.lantern: AWItemData(IClass.progression | IClass.useful, 1, 6, "Toys"),
    iname.uv: AWItemData(IClass.progression | IClass.useful, 1, 7, "Toys"),
    iname.ball: AWItemData(IClass.progression | IClass.useful, 1, 8, "Toys"),
    iname.remote: AWItemData(IClass.progression | IClass.useful, 1, 9, "Toys"),
    iname.wheel: AWItemData(IClass.progression | IClass.useful, 1, 10, "Toys"),
    iname.firecrackers: AWItemData(IClass.progression | IClass.useful, 0, 11, "Toys"),

    # Minor progression items and keys
    # iname.m_disc: AWItemData(IClass.progression | IClass.useful, 1, 12, "Toys"),
    iname.fanny_pack: AWItemData(IClass.useful, 1, 13, "Toys"),

    iname.match: AWItemData(IClass.progression, 9, 14, "Toys"),
    # iname.matchbox: AWItemData(IClass.progression | IClass.useful, 0, 15, "Toys"),

    iname.key: AWItemData(IClass.progression, 6, 16, "Keys"),
    # iname.key_ring: AWItemData(IClass.progression | IClass.useful, 0, 17, "Keys"),
    iname.house_key: AWItemData(IClass.progression, 1, 18, "Keys"),
    iname.office_key: AWItemData(IClass.progression, 1, 19, "Keys"),

    iname.e_medal: AWItemData(IClass.progression, 1, 20, "Keys"),
    iname.s_medal: AWItemData(IClass.progression, 1, 21, "Keys"),
    # iname.k_shard: AWItemData(IClass.progression, 3, 22, "Keys"),

    # iname.blue_flame: AWItemData(IClass.progression | IClass.useful, 1, 23, "Flames"),
    # iname.green_flame: AWItemData(IClass.progression | IClass.useful, 1, 24, "Flames"),
    # iname.violet_flame: AWItemData(IClass.progression | IClass.useful, 1, 25, "Flames"),
    # iname.pink_flame: AWItemData(IClass.progression | IClass.useful, 1, 26, "Flames"),

    # Eggs
    iname.egg_reference: AWItemData(IClass.progression_skip_balancing, 1, 27, "Eggs"),
    iname.egg_brown: AWItemData(IClass.progression_skip_balancing, 1, 28, "Eggs"),
    iname.egg_raw: AWItemData(IClass.progression_skip_balancing, 1, 29, "Eggs"),
    iname.egg_pickled: AWItemData(IClass.progression_skip_balancing, 1, 30, "Eggs"),
    iname.egg_big: AWItemData(IClass.progression_skip_balancing, 1, 31, "Eggs"),
    iname.egg_swan: AWItemData(IClass.progression_skip_balancing, 1, 32, "Eggs"),
    iname.egg_forbidden: AWItemData(IClass.progression_skip_balancing, 1, 33, "Eggs"),
    iname.egg_shadow: AWItemData(IClass.progression_skip_balancing, 1, 34, "Eggs"),
    iname.egg_vanity: AWItemData(IClass.progression_skip_balancing, 1, 35, "Eggs"),
    iname.egg_service: AWItemData(IClass.progression_skip_balancing, 1, 36, "Eggs"),

    iname.egg_depraved: AWItemData(IClass.progression_skip_balancing, 1, 37, "Eggs"),
    iname.egg_chaos: AWItemData(IClass.progression_skip_balancing, 1, 38, "Eggs"),
    iname.egg_upside_down: AWItemData(IClass.progression_skip_balancing, 1, 39, "Eggs"),
    iname.egg_evil: AWItemData(IClass.progression_skip_balancing, 1, 40, "Eggs"),
    iname.egg_sweet: AWItemData(IClass.progression_skip_balancing, 1, 41, "Eggs"),
    iname.egg_chocolate: AWItemData(IClass.progression_skip_balancing, 1, 42, "Eggs"),
    iname.egg_value: AWItemData(IClass.progression_skip_balancing, 1, 43, "Eggs"),
    iname.egg_plant: AWItemData(IClass.progression_skip_balancing, 1, 44, "Eggs"),
    iname.egg_red: AWItemData(IClass.progression_skip_balancing, 1, 45, "Eggs"),
    iname.egg_orange: AWItemData(IClass.progression_skip_balancing, 1, 46, "Eggs"),
    iname.egg_sour: AWItemData(IClass.progression_skip_balancing, 1, 47, "Eggs"),
    iname.egg_post_modern: AWItemData(IClass.progression_skip_balancing, 1, 48, "Eggs"),

    iname.egg_universal: AWItemData(IClass.progression_skip_balancing, 1, 49, "Eggs"),
    iname.egg_lf: AWItemData(IClass.progression_skip_balancing, 1, 50, "Eggs"),
    iname.egg_zen: AWItemData(IClass.progression_skip_balancing, 1, 51, "Eggs"),
    iname.egg_future: AWItemData(IClass.progression_skip_balancing, 1, 52, "Eggs"),
    iname.egg_friendship: AWItemData(IClass.progression_skip_balancing, 1, 53, "Eggs"),
    iname.egg_truth: AWItemData(IClass.progression_skip_balancing, 1, 54, "Eggs"),
    iname.egg_transcendental: AWItemData(IClass.progression_skip_balancing, 1, 55, "Eggs"),
    iname.egg_ancient: AWItemData(IClass.progression_skip_balancing, 1, 56, "Eggs"),
    iname.egg_magic: AWItemData(IClass.progression_skip_balancing, 1, 57, "Eggs"),
    iname.egg_mystic: AWItemData(IClass.progression_skip_balancing, 1, 58, "Eggs"),
    iname.egg_holiday: AWItemData(IClass.progression_skip_balancing, 1, 59, "Eggs"),
    iname.egg_rain: AWItemData(IClass.progression_skip_balancing, 1, 60, "Eggs"),
    iname.egg_razzle: AWItemData(IClass.progression_skip_balancing, 1, 61, "Eggs"),
    iname.egg_dazzle: AWItemData(IClass.progression_skip_balancing, 1, 62, "Eggs"),

    iname.egg_virtual: AWItemData(IClass.progression_skip_balancing, 1, 63, "Eggs"),
    iname.egg_normal: AWItemData(IClass.progression_skip_balancing, 1, 64, "Eggs"),
    iname.egg_great: AWItemData(IClass.progression_skip_balancing, 1, 65, "Eggs"),
    iname.egg_gorgeous: AWItemData(IClass.progression_skip_balancing, 1, 66, "Eggs"),
    iname.egg_planet: AWItemData(IClass.progression_skip_balancing, 1, 67, "Eggs"),
    iname.egg_moon: AWItemData(IClass.progression_skip_balancing, 1, 68, "Eggs"),
    iname.egg_galaxy: AWItemData(IClass.progression_skip_balancing, 1, 69, "Eggs"),
    iname.egg_sunset: AWItemData(IClass.progression_skip_balancing, 1, 70, "Eggs"),
    iname.egg_goodnight: AWItemData(IClass.progression_skip_balancing, 1, 71, "Eggs"),
    iname.egg_dream: AWItemData(IClass.progression_skip_balancing, 1, 72, "Eggs"),
    iname.egg_travel: AWItemData(IClass.progression_skip_balancing, 1, 73, "Eggs"),
    iname.egg_promise: AWItemData(IClass.progression_skip_balancing, 1, 74, "Eggs"),
    iname.egg_ice: AWItemData(IClass.progression_skip_balancing, 1, 75, "Eggs"),
    iname.egg_fire: AWItemData(IClass.progression_skip_balancing, 1, 76, "Eggs"),

    iname.egg_bubble: AWItemData(IClass.progression_skip_balancing, 1, 77, "Eggs"),
    iname.egg_desert: AWItemData(IClass.progression_skip_balancing, 1, 78, "Eggs"),
    iname.egg_clover: AWItemData(IClass.progression_skip_balancing, 1, 79, "Eggs"),
    iname.egg_brick: AWItemData(IClass.progression_skip_balancing, 1, 80, "Eggs"),
    iname.egg_neon: AWItemData(IClass.progression_skip_balancing, 1, 81, "Eggs"),
    iname.egg_iridescent: AWItemData(IClass.progression_skip_balancing, 1, 82, "Eggs"),
    iname.egg_rust: AWItemData(IClass.progression_skip_balancing, 1, 83, "Eggs"),
    iname.egg_scarlet: AWItemData(IClass.progression_skip_balancing, 1, 84, "Eggs"),
    iname.egg_sapphire: AWItemData(IClass.progression_skip_balancing, 1, 85, "Eggs"),
    iname.egg_ruby: AWItemData(IClass.progression_skip_balancing, 1, 86, "Eggs"),
    iname.egg_jade: AWItemData(IClass.progression_skip_balancing, 1, 87, "Eggs"),
    iname.egg_obsidian: AWItemData(IClass.progression_skip_balancing, 1, 88, "Eggs"),
    iname.egg_crystal: AWItemData(IClass.progression_skip_balancing, 1, 89, "Eggs"),
    iname.egg_golden: AWItemData(IClass.progression_skip_balancing, 1, 90, "Eggs"),

    iname.egg_65: AWItemData(IClass.progression_skip_balancing, 1, 91, "Eggs"),
    
    # "Firecracker Refill": AWItemData(IClass.filler, 0, 92, "Filler"),
    # "Big Blue Fruit": AWItemData(IClass.filler, 0, 93, "Filler"),
}

item_name_to_id: Dict[str, int] = {name: item_base_id + index for index, name in enumerate(item_table)}

filler_items: List[str] = [name for name, data in item_table.items() if data.classification == IClass.filler]


def get_item_group(item_name: str) -> str:
    return item_table[item_name].item_group


item_name_groups: Dict[str, Set[str]] = {
    group: set(item_names) for group, item_names in groupby(sorted(item_table, key=get_item_group), get_item_group) if group != ""
}

# # extra groups for the purpose of aliasing items
# extra_groups: Dict[str, Set[str]] = {
#     "Laurels": {"Hero's Laurels"},
# }
#
# item_name_groups.update(extra_groups)
