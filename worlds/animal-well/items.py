from itertools import groupby
from typing import Dict, List, Set, NamedTuple
from BaseClasses import ItemClassification
from .names import item_names as iname
IClass = ItemClassification


class AnimalWellItemData(NamedTuple):
    classification: ItemClassification
    quantity_in_item_pool: int  # put 0 for things not in the pool by default
    item_group: str = ""


item_base_id = 11553377

item_table: Dict[str, AnimalWellItemData] = {

    # Major progression items
    iname.bubble: AnimalWellItemData(IClass.progression | IClass.useful, 2, "Toys"),  # progressive
    iname.disc: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Toys"),
    iname.yoyo: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Toys"),
    iname.slink: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Toys"),
    iname.flute: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Toys"),
    iname.top: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Toys"),
    iname.lantern: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Toys"),
    iname.uv: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Toys"),
    iname.ball: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Toys"),
    iname.remote: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Toys"),
    iname.wheel: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Toys"),
    iname.firecrackers: AnimalWellItemData(IClass.progression | IClass.useful, 0, "Toys"),

    iname.m_disc: AnimalWellItemData(IClass.progression, 1, "Toys"),
    iname.fanny_pack: AnimalWellItemData(IClass.useful, 1, "Toys"),

    iname.match: AnimalWellItemData(IClass.progression, 9, "Toys"),
    iname.matchbox: AnimalWellItemData(IClass.progression | IClass.useful, 0, "Toys"),

    iname.key: AnimalWellItemData(IClass.progression, 6, "Keys"),
    iname.key_ring: AnimalWellItemData(IClass.progression | IClass.useful, 0, "Keys"),
    iname.house_key: AnimalWellItemData(IClass.progression, 1, "Keys"),
    iname.office_key: AnimalWellItemData(IClass.progression, 1, "Keys"),

    iname.e_medal: AnimalWellItemData(IClass.progression, 1, "Keys"),
    iname.s_medal: AnimalWellItemData(IClass.progression, 1, "Keys"),
    iname.k_shard: AnimalWellItemData(IClass.progression, 3, "Keys"),

    iname.blue_flame: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Flames"),
    iname.green_flame: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Flames"),
    iname.violet_flame: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Flames"),
    iname.pink_flame: AnimalWellItemData(IClass.progression | IClass.useful, 1, "Flames"),

    # todo: reorder this so it's the same order as locations.py

    iname.egg_reference: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_brown: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_raw: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_pickled: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_big: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_swan: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_forbidden: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_shadow: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_vanity: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_service: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),

    iname.egg_depraved: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_chaos: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_upside_down: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_evil: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_sweet: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_chocolate: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_value: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_plant: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_red: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_orange: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_sour: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_post_modern: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),

    iname.egg_universal: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_lf: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_zen: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_future: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_friendship: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_truth: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_transcendental: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_ancient: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_magic: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_mystic: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_holiday: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_rain: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_razzle: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_dazzle: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),

    iname.egg_virtual: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_normal: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_great: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_gorgeous: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_planet: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_moon: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_galaxy: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_sunset: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_goodnight: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_dream: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_travel: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_promise: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_ice: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_fire: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),

    iname.egg_bubble: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_desert: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_clover: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_brick: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_neon: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_iridescent: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_rust: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_scarlet: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_sapphire: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_ruby: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_jade: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_obsidian: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_crystal: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
    iname.egg_golden: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),

    iname.egg_65: AnimalWellItemData(IClass.progression_skip_balancing, 1, "Eggs"),
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
