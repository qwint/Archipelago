from .data.option_data import pool_options
from .data.location_data import multi_locations
from .data.item_data import affecting_items_by_term, progression_effect_lookup, non_progression_items

# strip "Randomize" from pool options and use their names as group names
item_name_groups = {
    key[9:]: {pair["item"] for pair in value}
    for key, value in pool_options.items()

    # TODO dynamically exclude these if possible
    if key not in ("RandomizeSwim", "RandomizeFocus")
    }

# override to remove world sense
item_name_groups["Dreamers"] = set(affecting_items_by_term["DREAMER"])

item_name_groups["CDash"] = set(affecting_items_by_term["LEFTSUPERDASH"] + affecting_items_by_term["RIGHTSUPERDASH"])
item_name_groups["Claw"] = set(affecting_items_by_term["LEFTCLAW"] + affecting_items_by_term["RIGHTCLAW"])
item_name_groups["Cloak"] = set(affecting_items_by_term["LEFTDASH"] + affecting_items_by_term["RIGHTDASH"])
item_name_groups["Dive"] = set(affecting_items_by_term["QUAKE"])
item_name_groups["Fireball"] = set(affecting_items_by_term["FIREBALL"])
item_name_groups["Scream"] = set(affecting_items_by_term["SCREAM"])
item_name_groups["Grimmchild"] = set(affecting_items_by_term["Grimmchild"])
item_name_groups["WhiteFragments"] = set(affecting_items_by_term["WHITEFRAGMENT"])

# TODO
# item_name_groups["PalaceLore"] = set(affecting_items_by_term["DREAMER"])
# item_name_groups["PalaceTotem"] = set(affecting_items_by_term["DREAMER"])


item_name_groups['Horizontal'] = item_name_groups['Cloak'] | item_name_groups['CDash']
item_name_groups['Vertical'] = item_name_groups['Claw'] | {'Monarch_Wings'}
# add split movement to skills
item_name_groups['Skills'] |= item_name_groups['Vertical'] | item_name_groups['Horizontal']


items = {item for item in progression_effect_lookup.keys()} | set(non_progression_items)
items |= {"One_Geo", "Soul_Refill"}
item_name_to_id = {
    item_name: item_id for item_id, item_name in
    enumerate(sorted(items), start=0x1000000)
}
