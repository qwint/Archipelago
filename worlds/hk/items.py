from .parse_data import options_pool_mappings, effects_items_by_term, effects_non_prog, effects_prog_lookup

# strip "Randomize" from pool options and use their names as group names
item_name_groups = {
    key[9:]: set(value["randomized"]["items"])
    for key, value in options_pool_mappings.items()

    # TODO dynamically exclude these if possible
    if key not in ("RandomizeSwim", "RandomizeFocus")
    }

# override to remove world sense
item_name_groups["Dreamers"] = set(effects_items_by_term["DREAMER"])

item_name_groups["CDash"] = set(effects_items_by_term["LEFTSUPERDASH"] + effects_items_by_term["RIGHTSUPERDASH"])
item_name_groups["Claw"] = set(effects_items_by_term["LEFTCLAW"] + effects_items_by_term["RIGHTCLAW"])
item_name_groups["Cloak"] = set(effects_items_by_term["LEFTDASH"] + effects_items_by_term["RIGHTDASH"])
item_name_groups["Dive"] = set(effects_items_by_term["QUAKE"])
item_name_groups["Fireball"] = set(effects_items_by_term["FIREBALL"])
item_name_groups["Scream"] = set(effects_items_by_term["SCREAM"])
item_name_groups["Grimmchild"] = set(effects_items_by_term["Grimmchild"])
item_name_groups["Charms"] |= item_name_groups["Grimmchild"]  # Grimmchild1 isn't in the options_pool_mappings for charms
item_name_groups["WhiteFragments"] = set(effects_items_by_term["WHITEFRAGMENT"])
item_name_groups["DreamNails"] = set(effects_items_by_term["DREAMNAIL"])

# TODO
# item_name_groups["PalaceLore"] = set(effects_items_by_term["DREAMER"])
# item_name_groups["PalaceTotem"] = set(effects_items_by_term["DREAMER"])


item_name_groups["Horizontal"] = item_name_groups["Cloak"] | item_name_groups["CDash"]
item_name_groups["Vertical"] = item_name_groups["Claw"] | {"Monarch_Wings"}
# add split movement to skills
item_name_groups["Skills"] |= item_name_groups["Vertical"] | item_name_groups["Horizontal"]

item_name_groups["SoulTotems"].add("Soul_Refill")


items = set(effects_prog_lookup.keys()) | set(effects_non_prog)
items |= {"One_Geo", "Soul_Refill"}
