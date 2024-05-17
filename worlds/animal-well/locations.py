from typing import Dict, NamedTuple, Set, Optional


class AnimalWellLocationData(NamedTuple):
    region: str
    location_group: Optional[str] = None

location_base_id = 11553377

location_table: Dict[str, AnimalWellLocationData] = {
    "Reference Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Brown Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Raw Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Pickled Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Big Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Swan Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Forbidden Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Shadow Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Vanity Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Egg as a Service": AnimalWellLocationData("Menu", "Eggs"),
    "Depraved Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Chaos Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Upside Down Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Evil Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Sweet Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Chocolate Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Value Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Plant Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Red Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Orange Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Sour Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Post Modern Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Universal Basic Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Laissez-Faire Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Zen Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Future Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Friendship Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Truth Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Transcendental Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Ancient Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Magic Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Mystic Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Holiday Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Rain Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Razzle Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Dazzle Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Virtual Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Normal Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Great Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Gorgeous Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Planet Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Moon Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Galaxy Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Sunset Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Goodnight Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Dream Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Travel Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Promise Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Ice Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Fire Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Bubble Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Desert Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Clover Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Brick Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Neon Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Iridescent Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Rust Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Scarlet Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Sapphire Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Ruby Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Jade Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Obsidian Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Crystal Egg": AnimalWellLocationData("Menu", "Eggs"),
    "Golden Egg": AnimalWellLocationData("Menu", "Eggs"),
    "65th Egg": AnimalWellLocationData("Menu", "Eggs"),
}

location_name_to_id: Dict[str, int] = {name: location_base_id + index for index, name in enumerate(location_table)}

location_name_groups: Dict[str, Set[str]] = {}
for loc_name, loc_data in location_table.items():
    if loc_data.location_group:
        location_name_groups.setdefault(loc_data.location_group, set()).add(loc_name)
