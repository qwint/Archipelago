from typing import Dict, List, Set

tunic_regions: Dict[str, Set[str]] = {
    "Menu": {"Overworld"},
    "Overworld": {"Overworld Holy Cross", "East Forest", "Dark Tomb", "Beneath the Well", "West Garden",
                  "Ruined Atoll", "Eastern Vault Fortress", "Beneath the Vault", "Quarry Back", "Quarry", "Swamp",
                  "Spirit Arena"},
    "Overworld Holy Cross": set(),
    "East Forest": set(),
    "Dark Tomb": {"West Garden"},
    "Beneath the Well": set(),
    "West Garden": set(),
    "Ruined Atoll": {"Frog's Domain", "Library"},
    "Frog's Domain": set(),
    "Library": set(),
    "Eastern Vault Fortress": {"Beneath the Vault"},
    "Beneath the Vault": {"Eastern Vault Fortress"},
    "Quarry Back": {"Quarry"},
    "Quarry": {"Lower Quarry"},
    "Lower Quarry": {"Rooted Ziggurat"},
    "Rooted Ziggurat": set(),
    "Swamp": {"Cathedral"},
    "Cathedral": set(),
    "Spirit Arena": set()
}

traversal_requirements: Dict[str, Dict[str, List[List[str]]]] = {
    "Library Lab": {
        "Library Lab Lower":
            [["Hyperdash"]],
        "Library Portal":
            [],
        "Library Lab to Librarian":
            [],
    },
    "Starting Area": {
        "Central Area":
            [["Firecrackers"]],  # needed to get past ghost, not sure if randomizing this yet?
        "Candle Room":
            [["Light All Candles"]]  # turn this into an event later
    }
}
