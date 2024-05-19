from typing import Dict, NamedTuple, Set, Optional


class AnimalWellLocationData(NamedTuple):
    region: str
    location_group: Optional[str] = None


location_base_id = 11553377

location_table: Dict[str, AnimalWellLocationData] = {
    "Reference Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Brown Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Raw Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Pickled Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Big Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Swan Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Forbidden Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Shadow Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Vanity Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Egg as a Service Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Depraved Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Chaos Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Upside Down Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Evil Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Sweet Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Chocolate Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Value Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Plant Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Red Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Orange Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Sour Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Post Modern Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Universal Basic Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Laissez-Faire Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Zen Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Future Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Friendship Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Truth Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Transcendental Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Ancient Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Magic Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Mystic Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Holiday Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Rain Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Razzle Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Dazzle Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Virtual Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Normal Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Great Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Gorgeous Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Planet Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Moon Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Galaxy Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Sunset Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Goodnight Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Dream Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Travel Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Promise Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Ice Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Fire Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Bubble Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Desert Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Clover Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Brick Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Neon Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Iridescent Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Rust Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Scarlet Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Sapphire Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Ruby Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Jade Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Obsidian Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Crystal Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "Golden Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
    "65th Egg Chest": AnimalWellLocationData("Menu", "Eggs"),
}

location_name_to_id: Dict[str, int] = {name: location_base_id + index for index, name in enumerate(location_table)}

location_name_groups: Dict[str, Set[str]] = {}
for loc_name, loc_data in location_table.items():
    if loc_data.location_group:
        location_name_groups.setdefault(loc_data.location_group, set()).add(loc_name)
