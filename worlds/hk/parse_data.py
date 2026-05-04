from collections import defaultdict
from typing import Any, cast

from .data import ids, item_effects, location_data, option_data, region_structure, trando_data

__all__ = [
    "datapackage_items",
    "datapackage_locations",

    "effects_terms_by_item",
    "effects_items_by_term",
    "effects_non_prog",
    "effects_prog_lookup",

    "metadata_location_areas",
    "metadata_location_multi",

    "options_logic_mappings",
    "options_pool_mappings",

    "structure_locations",
    "structure_regions",
    "structure_transition_to_region_map",

    "trando_starts",
    "trando_transitions",

    "shop_locations",
    "vanilla_shop_costs",
    "vanilla_location_costs",

    "hk_regions",
    "hk_locations",
]

datapackage_items = ids.item_name_to_id
datapackage_locations = ids.location_name_to_id

effects_terms_by_item = item_effects.affected_terms_by_item
effects_items_by_term = item_effects.affecting_items_by_term
effects_non_prog = item_effects.non_progression_items
effects_prog_lookup = item_effects.progression_effect_lookup

metadata_location_areas = location_data.locations
metadata_location_multi = location_data.multi_locations

options_logic_mappings = option_data.logic_options
options_pool_mappings = option_data.pool_options

structure_locations = region_structure.locations
structure_regions = region_structure.regions
structure_transition_to_region_map = region_structure.transition_to_region_map

trando_starts = trando_data.starts
trando_transitions = trando_data.transitions

# TODO: loop through additional sources

shop_locations = metadata_location_multi
event_locations = [location["name"] for location in structure_locations if location["is_event"]
                   and location["name"] not in ("Can_Warp_To_DG_Bench", "Can_Warp_To_Bench")]
vanilla_cost_data = [pair for option in options_pool_mappings.values() for pair in option["vanilla"] if pair["costs"]]
vanilla_location_costs = {
    pair["location"]: {cost["term"]: cost["amount"] for cost in pair["costs"]}
    for pair in vanilla_cost_data
    if pair["location"] not in metadata_location_multi
    }
vanilla_shop_costs = defaultdict(list)
for i in vanilla_cost_data:
    if i["location"] not in metadata_location_multi:
        continue
    costs = {cost["term"]: cost["amount"] for cost in i["costs"]}
    vanilla_shop_costs[(i["location"], i["item"])].append(costs)

hk_regions = [
    region for region in cast(list[dict[str, Any]], structure_regions)
    if not region["name"].startswith("$") and not region["name"] == "Bench-Godhome_Roof"
]
hk_locations = cast(list[dict[str, Any]], list(structure_locations))
