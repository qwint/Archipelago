from itertools import groupby
from typing import Dict, List, Set, NamedTuple
from BaseClasses import ItemClassification


class AnimalWellItemData(NamedTuple):
    classification: ItemClassification
    quantity_in_item_pool: int
    item_id_offset: int
    item_group: str = ""


item_base_id = 11553377

# todo: fill this out
# do this after the logic is all set up mostly
item_table: Dict[str, AnimalWellItemData] = {
    "Firecracker x2": AnimalWellItemData(ItemClassification.filler, 3, 0, "Bombs"),
    "Firecracker x3": AnimalWellItemData(ItemClassification.filler, 3, 1, "Bombs"),
    "Firecracker x4": AnimalWellItemData(ItemClassification.filler, 3, 2, "Bombs"),
    "Firecracker x5": AnimalWellItemData(ItemClassification.filler, 1, 3, "Bombs"),
    "Firecracker x6": AnimalWellItemData(ItemClassification.filler, 2, 4, "Bombs"),
    "Fire Bomb x2": AnimalWellItemData(ItemClassification.filler, 2, 5, "Bombs"),
    "Fire Bomb x3": AnimalWellItemData(ItemClassification.filler, 1, 6, "Bombs"),
    "Ice Bomb x2": AnimalWellItemData(ItemClassification.filler, 2, 7, "Bombs"),
    "Ice Bomb x3": AnimalWellItemData(ItemClassification.filler, 2, 8, "Bombs"),
    "Ice Bomb x5": AnimalWellItemData(ItemClassification.filler, 1, 9, "Bombs"),
    "Lure": AnimalWellItemData(ItemClassification.filler, 4, 10, "Consumables"),
    "Lure x2": AnimalWellItemData(ItemClassification.filler, 1, 11, "Consumables"),
    "Pepper x2": AnimalWellItemData(ItemClassification.filler, 4, 12, "Consumables"),
    "Ivy x3": AnimalWellItemData(ItemClassification.filler, 2, 13, "Consumables"),
    "Effigy": AnimalWellItemData(ItemClassification.useful, 12, 14, "Money"),
    "HP Berry": AnimalWellItemData(ItemClassification.filler, 2, 15, "Consumables"),
    "HP Berry x2": AnimalWellItemData(ItemClassification.filler, 4, 16, "Consumables"),
    "HP Berry x3": AnimalWellItemData(ItemClassification.filler, 2, 17, "Consumables"),
    "MP Berry": AnimalWellItemData(ItemClassification.filler, 4, 18, "Consumables"),
    "MP Berry x2": AnimalWellItemData(ItemClassification.filler, 2, 19, "Consumables"),
    "MP Berry x3": AnimalWellItemData(ItemClassification.filler, 7, 20, "Consumables"),
    "Fairy": AnimalWellItemData(ItemClassification.progression, 20, 21),
    "Stick": AnimalWellItemData(ItemClassification.progression, 1, 22, "Weapons"),
    "Sword": AnimalWellItemData(ItemClassification.progression, 3, 23, "Weapons"),
    "Sword Upgrade": AnimalWellItemData(ItemClassification.progression, 4, 24, "Weapons"),
    "Magic Wand": AnimalWellItemData(ItemClassification.progression, 1, 25, "Weapons"),
    "Magic Dagger": AnimalWellItemData(ItemClassification.progression, 1, 26),
    "Magic Orb": AnimalWellItemData(ItemClassification.progression, 1, 27),
    "Hero's Laurels": AnimalWellItemData(ItemClassification.progression, 1, 28),
    "Lantern": AnimalWellItemData(ItemClassification.progression, 1, 29),
    "Gun": AnimalWellItemData(ItemClassification.useful, 1, 30, "Weapons"),
    "Shield": AnimalWellItemData(ItemClassification.useful, 1, 31),
    "Dath Stone": AnimalWellItemData(ItemClassification.useful, 1, 32),
    "Hourglass": AnimalWellItemData(ItemClassification.useful, 1, 33),
    "Old House Key": AnimalWellItemData(ItemClassification.progression, 1, 34, "Keys"),
    "Key": AnimalWellItemData(ItemClassification.progression, 2, 35, "Keys"),
    "Fortress Vault Key": AnimalWellItemData(ItemClassification.progression, 1, 36, "Keys"),
    "Flask Shard": AnimalWellItemData(ItemClassification.useful, 12, 37),
    "Potion Flask": AnimalWellItemData(ItemClassification.useful, 5, 38, "Flask"),
    "Golden Coin": AnimalWellItemData(ItemClassification.progression, 17, 39),
    "Card Slot": AnimalWellItemData(ItemClassification.useful, 4, 40),
    "Red Questagon": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, 41, "Hexagons"),
    "Green Questagon": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, 42, "Hexagons"),
    "Blue Questagon": AnimalWellItemData(ItemClassification.progression_skip_balancing, 1, 43, "Hexagons"),
    "Gold Questagon": AnimalWellItemData(ItemClassification.progression_skip_balancing, 0, 44, "Hexagons"),
    "ATT Offering": AnimalWellItemData(ItemClassification.useful, 4, 45, "Offerings"),
    "DEF Offering": AnimalWellItemData(ItemClassification.useful, 4, 46, "Offerings"),
    "Potion Offering": AnimalWellItemData(ItemClassification.useful, 3, 47, "Offerings"),
    "HP Offering": AnimalWellItemData(ItemClassification.useful, 6, 48, "Offerings"),
    "MP Offering": AnimalWellItemData(ItemClassification.useful, 3, 49, "Offerings"),
    "SP Offering": AnimalWellItemData(ItemClassification.useful, 2, 50, "Offerings"),
    "Hero Relic - ATT": AnimalWellItemData(ItemClassification.useful, 1, 51, "Hero Relics"),
    "Hero Relic - DEF": AnimalWellItemData(ItemClassification.useful, 1, 52, "Hero Relics"),
    "Hero Relic - HP": AnimalWellItemData(ItemClassification.useful, 1, 53, "Hero Relics"),
    "Hero Relic - MP": AnimalWellItemData(ItemClassification.useful, 1, 54, "Hero Relics"),
    "Hero Relic - POTION": AnimalWellItemData(ItemClassification.useful, 1, 55, "Hero Relics"),
    "Hero Relic - SP": AnimalWellItemData(ItemClassification.useful, 1, 56, "Hero Relics"),
    "Orange Peril Ring": AnimalWellItemData(ItemClassification.useful, 1, 57, "Cards"),
    "Tincture": AnimalWellItemData(ItemClassification.useful, 1, 58, "Cards"),
    "Scavenger Mask": AnimalWellItemData(ItemClassification.progression, 1, 59, "Cards"),
    "Cyan Peril Ring": AnimalWellItemData(ItemClassification.useful, 1, 60, "Cards"),
    "Bracer": AnimalWellItemData(ItemClassification.useful, 1, 61, "Cards"),
    "Dagger Strap": AnimalWellItemData(ItemClassification.useful, 1, 62, "Cards"),
    "Inverted Ash": AnimalWellItemData(ItemClassification.useful, 1, 63, "Cards"),
    "Lucky Cup": AnimalWellItemData(ItemClassification.useful, 1, 64, "Cards"),
    "Magic Echo": AnimalWellItemData(ItemClassification.useful, 1, 65, "Cards"),
    "Anklet": AnimalWellItemData(ItemClassification.useful, 1, 66, "Cards"),
    "Muffling Bell": AnimalWellItemData(ItemClassification.useful, 1, 67, "Cards"),
    "Glass Cannon": AnimalWellItemData(ItemClassification.useful, 1, 68, "Cards"),
    "Perfume": AnimalWellItemData(ItemClassification.useful, 1, 69, "Cards"),
    "Louder Echo": AnimalWellItemData(ItemClassification.useful, 1, 70, "Cards"),
    "Aura's Gem": AnimalWellItemData(ItemClassification.useful, 1, 71, "Cards"),
    "Bone Card": AnimalWellItemData(ItemClassification.useful, 1, 72, "Cards"),
    "Mr Mayor": AnimalWellItemData(ItemClassification.useful, 1, 73, "Golden Treasures"),
    "Secret Legend": AnimalWellItemData(ItemClassification.useful, 1, 74, "Golden Treasures"),
    "Sacred Geometry": AnimalWellItemData(ItemClassification.useful, 1, 75, "Golden Treasures"),
    "Vintage": AnimalWellItemData(ItemClassification.useful, 1, 76, "Golden Treasures"),
    "Just Some Pals": AnimalWellItemData(ItemClassification.useful, 1, 77, "Golden Treasures"),
    "Regal Weasel": AnimalWellItemData(ItemClassification.useful, 1, 78, "Golden Treasures"),
    "Spring Falls": AnimalWellItemData(ItemClassification.useful, 1, 79, "Golden Treasures"),
    "Power Up": AnimalWellItemData(ItemClassification.useful, 1, 80, "Golden Treasures"),
    "Back To Work": AnimalWellItemData(ItemClassification.useful, 1, 81, "Golden Treasures"),
    "Phonomath": AnimalWellItemData(ItemClassification.useful, 1, 82, "Golden Treasures"),
    "Dusty": AnimalWellItemData(ItemClassification.useful, 1, 83, "Golden Treasures"),
    "Forever Friend": AnimalWellItemData(ItemClassification.useful, 1, 84, "Golden Treasures"),
    "Fool Trap": AnimalWellItemData(ItemClassification.trap, 0, 85),
    "Money x1": AnimalWellItemData(ItemClassification.filler, 3, 86, "Money"),
    "Money x10": AnimalWellItemData(ItemClassification.filler, 1, 87, "Money"),
    "Money x15": AnimalWellItemData(ItemClassification.filler, 10, 88, "Money"),
    "Money x16": AnimalWellItemData(ItemClassification.filler, 1, 89, "Money"),
    "Money x20": AnimalWellItemData(ItemClassification.filler, 17, 90, "Money"),
    "Money x25": AnimalWellItemData(ItemClassification.filler, 14, 91, "Money"),
    "Money x30": AnimalWellItemData(ItemClassification.filler, 4, 92, "Money"),
    "Money x32": AnimalWellItemData(ItemClassification.filler, 4, 93, "Money"),
    "Money x40": AnimalWellItemData(ItemClassification.filler, 3, 94, "Money"),
    "Money x48": AnimalWellItemData(ItemClassification.filler, 1, 95, "Money"),
    "Money x50": AnimalWellItemData(ItemClassification.filler, 7, 96, "Money"),
    "Money x64": AnimalWellItemData(ItemClassification.filler, 1, 97, "Money"),
    "Money x100": AnimalWellItemData(ItemClassification.filler, 5, 98, "Money"),
    "Money x128": AnimalWellItemData(ItemClassification.useful, 3, 99, "Money"),
    "Money x200": AnimalWellItemData(ItemClassification.useful, 1, 100, "Money"),
    "Money x255": AnimalWellItemData(ItemClassification.useful, 1, 101, "Money"),
    "Pages 0-1": AnimalWellItemData(ItemClassification.useful, 1, 102, "Pages"),
    "Pages 2-3": AnimalWellItemData(ItemClassification.useful, 1, 103, "Pages"),
    "Pages 4-5": AnimalWellItemData(ItemClassification.useful, 1, 104, "Pages"),
    "Pages 6-7": AnimalWellItemData(ItemClassification.useful, 1, 105, "Pages"),
    "Pages 8-9": AnimalWellItemData(ItemClassification.useful, 1, 106, "Pages"),
    "Pages 10-11": AnimalWellItemData(ItemClassification.useful, 1, 107, "Pages"),
    "Pages 12-13": AnimalWellItemData(ItemClassification.useful, 1, 108, "Pages"),
    "Pages 14-15": AnimalWellItemData(ItemClassification.useful, 1, 109, "Pages"),
    "Pages 16-17": AnimalWellItemData(ItemClassification.useful, 1, 110, "Pages"),
    "Pages 18-19": AnimalWellItemData(ItemClassification.useful, 1, 111, "Pages"),
    "Pages 20-21": AnimalWellItemData(ItemClassification.useful, 1, 112, "Pages"),
    "Pages 22-23": AnimalWellItemData(ItemClassification.useful, 1, 113, "Pages"),
    "Pages 24-25 (Prayer)": AnimalWellItemData(ItemClassification.progression, 1, 114, "Pages"),
    "Pages 26-27": AnimalWellItemData(ItemClassification.useful, 1, 115, "Pages"),
    "Pages 28-29": AnimalWellItemData(ItemClassification.useful, 1, 116, "Pages"),
    "Pages 30-31": AnimalWellItemData(ItemClassification.useful, 1, 117, "Pages"),
    "Pages 32-33": AnimalWellItemData(ItemClassification.useful, 1, 118, "Pages"),
    "Pages 34-35": AnimalWellItemData(ItemClassification.useful, 1, 119, "Pages"),
    "Pages 36-37": AnimalWellItemData(ItemClassification.useful, 1, 120, "Pages"),
    "Pages 38-39": AnimalWellItemData(ItemClassification.useful, 1, 121, "Pages"),
    "Pages 40-41": AnimalWellItemData(ItemClassification.useful, 1, 122, "Pages"),
    "Pages 42-43 (Holy Cross)": AnimalWellItemData(ItemClassification.progression, 1, 123, "Pages"),
    "Pages 44-45": AnimalWellItemData(ItemClassification.useful, 1, 124, "Pages"),
    "Pages 46-47": AnimalWellItemData(ItemClassification.useful, 1, 125, "Pages"),
    "Pages 48-49": AnimalWellItemData(ItemClassification.useful, 1, 126, "Pages"),
    "Pages 50-51": AnimalWellItemData(ItemClassification.useful, 1, 127, "Pages"),
    "Pages 52-53 (Icebolt)": AnimalWellItemData(ItemClassification.progression, 1, 128, "Pages"),
    "Pages 54-55": AnimalWellItemData(ItemClassification.useful, 1, 129, "Pages"),
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
