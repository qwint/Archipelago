from typing import Dict, NamedTuple, Set, Optional
from .names import location_names as lname


class AnimalWellLocationData(NamedTuple):
    region: str
    location_group: Optional[str] = None


location_base_id = 11553377

location_table: Dict[str, AnimalWellLocationData] = {
    # eggs, sorted by row top-to-bottom
    lname.egg_reference: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_brown: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_raw: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_pickled: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_big: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_swan: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_forbidden: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_shadow: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_vanity: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_service: AnimalWellLocationData("Menu", "Eggs"),

    lname.egg_depraved: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_chaos: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_upside_down: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_evil: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_sweet: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_chocolate: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_value: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_plant: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_red: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_orange: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_sour: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_post_modern: AnimalWellLocationData("Menu", "Eggs"),

    lname.egg_universal: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_lf: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_zen: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_future: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_friendship: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_truth: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_transcendental: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_ancient: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_magic: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_mystic: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_holiday: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_rain: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_razzle: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_dazzle: AnimalWellLocationData("Menu", "Eggs"),

    lname.egg_virtual: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_normal: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_great: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_gorgeous: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_planet: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_moon: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_galaxy: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_sunset: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_goodnight: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_dream: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_travel: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_promise: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_ice: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_fire: AnimalWellLocationData("Menu", "Eggs"),

    lname.egg_bubble: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_desert: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_clover: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_brick: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_neon: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_iridescent: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_rust: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_scarlet: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_sapphire: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_ruby: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_jade: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_obsidian: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_crystal: AnimalWellLocationData("Menu", "Eggs"),
    lname.egg_golden: AnimalWellLocationData("Menu", "Eggs"),

    lname.egg_65: AnimalWellLocationData("Menu", "Eggs"),
}

location_name_to_id: Dict[str, int] = {name: location_base_id + index for index, name in enumerate(location_table)}

location_name_groups: Dict[str, Set[str]] = {}
for loc_name, loc_data in location_table.items():
    if loc_data.location_group:
        location_name_groups.setdefault(loc_data.location_group, set()).add(loc_name)
