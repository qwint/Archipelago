import logging
import itertools
import operator

from copy import deepcopy
from collections import Counter
from typing import List, Dict, Any, Tuple, NamedTuple, Optional, cast

from BaseClasses import Location, Item, ItemClassification, Tutorial, CollectionState, MultiWorld, Region, Entrance, LocationProgressType
from worlds.AutoWorld import WebWorld

from .template_world import RandomizerCoreWorld

from .state_mixin import HKLogicMixin  # all that's needed to add the mixin
from .region_data import regions, transitions, locations
from .Options import hollow_knight_options, hollow_knight_randomize_options, Goal, WhitePalace, CostSanity, \
    shop_to_option, HKOptions
from .Rules import cost_terms, _hk_can_beat_thk, _hk_siblings_ending, _hk_can_beat_radiance
from .Charms import names as charm_names

from .ExtractedData import pool_options, logic_options, items as extracted_items, logic_items, item_effects, multi_locations
from .Items import item_name_groups, item_name_to_id, location_name_to_id  # item_table, lookup_type_to_names, item_name_groups

logger = logging.getLogger("Hollow Knight")

# Shop cost types.
shop_cost_types: Dict[str, Tuple[str, ...]] = {
    "Egg_Shop": ("RANCIDEGGS",),
    "Grubfather": ("GRUBS",),
    "Seer": ("ESSENCE",),
    "Salubra_(Requires_Charms)": ("CHARMS", "GEO"),
    "Sly": ("GEO",),
    "Sly_(Key)": ("GEO",),
    "Iselda": ("GEO",),
    "Salubra": ("GEO",),
    "Leg_Eater": ("GEO",),
}

randomizable_starting_items: Dict[str, Tuple[str, ...]] = {
    "RandomizeFocus": ("Focus",),
    "RandomizeSwim": ("Swim",),
    "RandomizeNail": ('Upslash', 'Leftslash', 'Rightslash')
}


class HKWeb(WebWorld):
    tutorials = [Tutorial(
        "Mod Setup and Use Guide",
        "A guide to playing Hollow Knight with Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Ijwu"]
    )]

    bug_report_page = "https://github.com/Ijwu/Archipelago.HollowKnight/issues/new?assignees=&labels=bug%2C+needs+investigation&template=bug_report.md&title="


gamename = "Hollow Knight"
base_id = 0x1000000


class HK_state_diff(NamedTuple):
    shadeskip: int
    # shade health needed, 0 if unneeded

    damage: int
    # health needed for damage boosts

    twister_required: bool
    # shortcut logic if any step in a spell skip needs 4 casts

    total_casts: int
    # shortcut logic for the total casts for all steps in spell stalls

    before: bool
    # determined in parsing that we have beforesoul

    after: bool
    # determined in parsing that we have afteresoul


class HKClause(NamedTuple):
    hk_item_requirements: Counter[str]
    hk_region_requirements: List[str]
    hk_state_requirements: HK_state_diff
    hk_state_modifiers: Any  # figure this out later


default_hk_rule = HKClause(
    hk_item_requirements=Counter({"True": 1}),
    hk_region_requirements=[],
    hk_state_requirements=HK_state_diff(shadeskip=0, damage=0, twister_required=False, total_casts=0, before=False, after=False),
    hk_state_modifiers=[],
    )


class HKLocation(Location):
    game: str = gamename
    costs: Optional[Dict[str, int]]  # = None
    vanilla: bool  # = False
    basename: str
    hk_rule: List[HKClause]

    def __init__(
            self, player: int, name: str, code=None, parent=None,
            costs: Optional[Dict[str, int]] = None, vanilla: bool = False, basename: Optional[str] = None
    ):
        super(HKLocation, self).__init__(player, name, code if code else None, parent)
        self.basename = basename or name
        self.vanilla = vanilla
        self.hk_rule = default_hk_rule
        if costs:
            self.costs = dict(costs)
            self.sort_costs()
        else:
            self.costs = None

    def access_rule(self, state: CollectionState) -> bool:
        if self.costs:
            logic_costs = {term: amount for term, amount in self.costs.items() if term != "GEO"}
            if not state.has_all_counts(logic_costs, self.player):
                return False

        if self.hk_rule == default_hk_rule:
            return True

        for clause in self.hk_rule:
            if state.has_all_counts(clause.hk_item_requirements, self.player) \
                    and all(state.can_reach(region, "Region", self.player) for region in clause.hk_region_requirements) \
                    and state._hk_any_state_valid_for_region(clause.hk_state_requirements, self.parent_region):
                return True
        # no clause was True,
        return False

    def sort_costs(self):
        if self.costs is None:
            return
        self.costs = {k: self.costs[k] for k in sorted(self.costs.keys(), key=lambda x: cost_terms[x].sort)}

    def cost_text(self, separator=" and "):
        if self.costs is None:
            return None
        return separator.join(
            f"{value} {cost_terms[term].singular if value == 1 else cost_terms[term].plural}"
            for term, value in self.costs.items()
        )


class HKItem(Item):
    game = gamename


class HKEntrance(Entrance):
    hk_rule: List[HKClause]

    def __init__(self, *args, **kwargs):
        super(HKEntrance, self).__init__(*args, **kwargs)
        self.hk_rule = default_hk_rule

    def access_rule(self, state: CollectionState) -> bool:
        # TODO pass on states and return True
        if self.hk_rule == default_hk_rule:
            state._hk_apply_state_to_region(self, None)
            return True
        if not state._hk_entrance_clause_cache[self.player].get(self.name, None):
            # if there's no cache for this entrance, make one with everything False
            state._hk_entrance_clause_cache[self.player][self.name] = {index: False for index in range(len(self.hk_rule))}

        # check every clause, caching item state accessibility
        valid_clauses = {}
        for index, clause in enumerate(self.hk_rule):
            if state._hk_entrance_clause_cache[self.player][self.name][index]:
                state._hk_apply_state_to_region(self, clause)
                valid_clauses[index] = True
            elif state.has_all_counts(clause.hk_item_requirements, self.player) \
                    and all(state.can_reach(region, "Region", self.player) for region in clause.hk_region_requirements):
                state._hk_entrance_clause_cache[self.player][self.name][index] = True
                if state._hk_any_state_valid_for_region(clause.hk_state_requirements, self.parent_region):
                    state._hk_apply_state_to_region(self, clause)
                    valid_clauses[index] = True

        if self.parent_region == "Menu":
            print(valid_clauses)
        if any(clause for clause in valid_clauses.values()):
            return True
        else:
            return False


class HKRegion(Region):
    entrance_type = HKEntrance


# TODO clean this up
item_datapackage = list({item for pairs in pool_options.values() for item in pairs[0]})
item_datapackage += ["One_Geo", "Soul_Refill"]


location_datapackage = [location["name"] for location in cast(List[Dict[str, Any]], locations)]
event_locations = ['Can_Replenish_Geo', 'Can_Replenish_Geo-Crossroads', 'Rescued_Sly', 'Rescued_Bretta', 'Rescued_Deepnest_Zote', 'Defeated_Colosseum_Zote', 'Lever-Shade_Soul', 'Lever-City_Fountain', 'Lever-Path_of_Pain', 'Completed_Path_of_Pain', 'Lever-Dung_Defender', 'Defeated_Gruz_Mother', 'Defeated_False_Knight', 'Defeated_Brooding_Mawlek', 'Defeated_Hornet_1', 'Defeated_Mantis_Lords', 'Defeated_Sanctum_Warrior', 'Defeated_Soul_Master', 'Defeated_Elegant_Warrior', 'Defeated_Crystal_Guardian', 'Defeated_Enraged_Guardian', 'Defeated_Flukemarm', 'Defeated_Dung_Defender', 'Defeated_Broken_Vessel', 'Defeated_Hornet_2', 'Defeated_Watcher_Knights', 'Defeated_Uumuu', 'Defeated_Nosk', 'Defeated_Traitor_Lord', 'Defeated_Grimm', 'Defeated_Collector', 'Defeated_Hive_Knight', 'Defeated_Pale_Lurker', 'Defeated_Elder_Hu', 'Defeated_Xero', 'Defeated_Gorb', 'Defeated_Marmu', 'Defeated_No_Eyes', 'Defeated_Galien', 'Defeated_Markoth', 'Defeated_Failed_Champion', 'Defeated_Soul_Tyrant', 'Defeated_Lost_Kin', 'Defeated_White_Defender', 'Defeated_Grey_Prince_Zote', 'Defeated_Colosseum_1', 'Defeated_Colosseum_2', 'Defeated_Ancestral_Mound_Baldur', 'Defeated_Crossroads_Baldur', 'Defeated_Right_Cliffs_Baldur', 'Defeated_Shrumal_Ogre_Arena', "Defeated_King's_Station_Arena", "Defeated_West_Queen's_Gardens_Arena", 'Defeated_Path_of_Pain_Arena', 'Can_Visit_Lemm', 'Can_Repair_Fragile_Charms', 'Can_Deliver_Flower', 'First_Grimmchild_Upgrade', 'Second_Grimmchild_Upgrade', 'Nightmare_Lantern_Lit', 'Opened_Waterways_Manhole', 'Opened_Dung_Defender_Wall', 'Opened_Resting_Grounds_Floor', 'Broke_Crypts_One_Way_Floor', 'Opened_Resting_Grounds_Catacombs_Wall', 'Opened_Pleasure_House_Wall', 'Opened_Gardens_Stag_Exit', 'Opened_Mawlek_Wall', 'Opened_Shaman_Pillar', 'Opened_Archives_Exit_Wall', 'Opened_Tramway_Exit_Gate', 'Broke_Camp_Bench_Wall', 'Broke_Sanctum_Glass_Floor', 'Broke_Goam_Entry_Quake_Floor', "Broke_Pilgrim's_Way_Quake_Floor", 'Broke_Sanctum_Geo_Rock_Quake_Floor', 'Broke_Quake_Floor_After_Soul_Master_1', 'Broke_Quake_Floor_After_Soul_Master_2', 'Broke_Quake_Floor_After_Soul_Master_3', 'Broke_Quake_Floor_After_Soul_Master_4', 'Broke_Sanctum_Escape_Quake_Floor_1', 'Broke_Sanctum_Escape_Quake_Floor_2', 'Broke_Crystal_Peak_Entrance_Quake_Floor', 'Broke_Crystal_Peak_Dive_Egg_Quake_Floor', "Broke_Hallownest's_Crown_Quake_Floor", 'Broke_Crystallized_Mound_Quake_Floor', 'Broke_Resting_Grounds_Quake_Floor', 'Broke_Cliffs_Dark_Room_Quake_Floor', 'Broke_Basin_Grub_Quake_Floor', 'Broke_Lower_Edge_Quake_Floor', 'Broke_Oro_Quake_Floor_1', 'Broke_Oro_Quake_Floor_2', 'Broke_Oro_Quake_Floor_3', 'Broke_420_Rock_Quake_Floor_1', 'Broke_420_Rock_Quake_Floor_2', 'Broke_420_Rock_Quake_Floor_3', 'Broke_420_Rock_Quake_Floor_4', 'Broke_420_Rock_Quake_Floor_5', 'Broke_420_Rock_Quake_Floor_6', 'Broke_420_Rock_Quake_Floor_7', 'Broke_420_Rock_Quake_Floor_8', 'Broke_420_Rock_Quake_Floor_9', 'Broke_420_Rock_Quake_Floor_10', 'Broke_420_Rock_Quake_Floor_11', 'Broke_Waterways_Bench_Quake_Floor_1', 'Broke_Waterways_Bench_Quake_Floor_2', 'Broke_Waterways_Bench_Quake_Floor_3', 'Broke_Flukemarm_Quake_Floor', 'Broke_Dung_Defender_Quake_Floor', 'Broke_Edge_Journal_Quake_Floor', 'Opened_Emilitia_Door', 'Lit_Abyss_Lighthouse', "Opened_Lower_Kingdom's_Edge_Wall", 'Opened_Glade_Door', 'Opened_Waterways_Exit', 'Palace_Entrance_Lantern_Lit', 'Palace_Left_Lantern_Lit', 'Palace_Right_Lantern_Lit', 'Palace_Atrium_Gates_Opened', 'Opened_Black_Egg_Temple', 'Start']  # 'Can_Warp_To_DG_Bench', 'Can_Warp_To_Bench',
shop_locations = ['Sly', 'Sly_(Key)', 'Iselda', 'Salubra', 'Leg_Eater', 'Grubfather', 'Seer']
shop_locations += ['Salubra_(Requires_Charms)', 'Egg_Shop']
location_datapackage = [loc for loc in location_datapackage if loc not in event_locations and loc not in shop_locations]
location_datapackage += [f"{shop}_{i+1}" for shop in shop_locations for i in range(16)]


hk_regions = [region for region in cast(List[Dict[str, Any]], regions) if not region["name"].startswith("$")]
hk_locations = [location for location in cast(List[Dict[str, Any]], locations) if location["name"] not in ("Can_Warp_To_DG_Bench", "Can_Warp_To_Bench")]


class HKWorld(RandomizerCoreWorld):
    """Beneath the fading town of Dirtmouth sleeps a vast, ancient kingdom. Many are drawn beneath the surface, 
    searching for riches, or glory, or answers to old secrets.

    As the enigmatic Knight, you’ll traverse the depths, unravel its mysteries and conquer its evils.
    """  # from https://www.hollowknight.com

    game = gamename
    web = HKWeb()
    location_name_to_id = location_name_to_id
    item_name_to_id = item_name_to_id
    options_dataclass = HKOptions
    options: HKOptions
    item_name_groups = item_name_groups

    rc_regions: List[Dict[str, Any]] = hk_regions
    rc_locations: List[Dict[str, Any]] = hk_locations
    item_class = HKItem
    location_class = HKLocation
    region_class = HKRegion

    rule_lookup = {location["name"]: location["logic"] for location in hk_locations}
    region_lookup = {location: region["name"] for region in hk_regions for location in region["locations"]}
    pool_lookup = {
        location if location not in multi_locations else f"{location}_{item}": item
        for option, pairs in pool_options.items()
        for item, location in zip(pairs[0], pairs[1])
        }

    cached_filler_items: Dict[int, List[str]] = {}  # per player cache
    event_locations: List[str]
    ranges: Dict[str, Tuple[int, int]]
    charm_costs: List[int]

    def __init__(self, multiworld, player):
        from .ExtractedData import vanilla_shop_costs
        super(HKWorld, self).__init__(multiworld, player)
        self.created_multi_locations: Dict[str, List[HKLocation]] = {
            location: list() for location in multi_locations
        }
        self.ranges = {}
        self.created_shop_items = 0
        self.vanilla_shop_costs = deepcopy(vanilla_shop_costs)
        self.event_locations = deepcopy(event_locations)

    # def get_region_list(self) -> List[str]:
    #     return super().get_region_list()

# RandomizerCoreWorld overrides
    def create_regions(self):
        from .ExtractedData import vanilla_location_costs
        super().create_regions()
        self.add_vanilla_connections()
        self.add_all_events()
        self.add_shop_locations()

        # TODO remove once proper can_reach get into region_data
        self.multiworld.get_location("Can_Visit_Lemm", self.player).access_rule = lambda state: state.can_reach("Ruins1_27[left1]", "Region", self.player)
        # TODO confirm we don't have to handle the other exclusions
        if "King_Fragment" in self.white_palace_exclusions():
            self.multiworld.get_location("King_Fragment", self.player).progress_type = LocationProgressType.EXCLUDED

        for location, costs in vanilla_location_costs.items():
            try:
                self.multiworld.get_location(location, self.player).costs = costs
            except KeyError as e:
                print(f"could not find location {location}")
                raise e

    def create_items(self):
        super().create_items()

        # TODO see if there's a better way to get these numbers
        item_difference = len([item for item in self.multiworld.itempool if item.player == self.player]) - len(self.multiworld.get_unfilled_locations(self.player))
        if item_difference > 0:
            self.add_extra_shop_locations(item_difference)

        self.handle_starting_inventory()
        self.apply_costsanity()
        # self.sort_shops_by_cost()

# extra handling
    def add_vanilla_connections(self):
        import pkgutil
        import json
        data = pkgutil.get_data(__name__, f"transitions.json").decode("utf-8")
        trans_data = json.loads(data)

        transition_name_to_region = {transition: region["name"] for region in self.rc_regions for transition in region["transitions"]}
        vanilla_connections = [
            (transition_name_to_region[name], transition_name_to_region[t["VanillaTarget"]], name)
            for name, t in trans_data.items() if t["Sides"] != "OneWayOut"
            ]

        for connection in vanilla_connections:
            region1 = self.multiworld.get_region(connection[0], self.player)
            region2 = self.multiworld.get_region(connection[1], self.player)
            region1.connect(region2, connection[2])

    # TODO revisit all this create location code and see if some can be abstracted
    def add_all_events(self):
        # Vanilla placements of the following items have no impact on logic, thus we can avoid creating these items and
        # locations entirely when the option to randomize them is disabled.
        logicless_options = {
            "RandomizeVesselFragments", "RandomizeGeoChests", "RandomizeJunkPitChests", "RandomizeRelics",
            "RandomizeMaps", "RandomizeJournalEntries", "RandomizeGeoRocks", "RandomizeBossGeo",
            "RandomizeLoreTablets", "RandomizeSoulTotems", "RandomizeLifebloodCocoons",
        }

        # meant to add events used in logic and to add any non-randomized item/locations as events
        # also makes the unshuffled ap items if add_unshuffled is true
        unshuffled_location_lookup = {
            location if location not in self.created_multi_locations else f"{location}_{item}": option
            for option, pairs in pool_options.items()
            for item, location in zip(pairs[0], pairs[1])
            if (self.options.AddUnshuffledLocations and option not in logicless_options)
            # TODO double check logic
            }

        for event_location in self.event_locations:
            def create_location(location: Tuple[str, Optional[int]], rule: Any, item: Optional[Tuple[str, Optional[int]]], region: "Region"):
                loc = self.location_class(self.player, location[0], location[1], region)
                if rule:
                    self.set_rule(loc, self.create_rule(rule))
                if item:
                    loc.place_locked_item(self.item_class(item[0], ItemClassification.progression, item[1], self.player))
                    loc.show_in_spoiler = False
                return loc

            if event_location.startswith("Start"):
                continue
                # # TODO handle this better / get better extracted itemdata

            if event_location in unshuffled_location_lookup:
                item_name = self.pool_lookup[event_location]
                item = (item_name, self.item_name_to_id[item_name])
            else:
                item_name = self.pool_lookup.get(event_location, event_location)
                item = (item_name, None)
                # if we don't have an item for the location it is a pure event, name the item same as the location

            if event_location in self.pool_lookup and event_location.split(f"_{self.pool_lookup[event_location]}")[0] in shop_locations:
                shop = event_location.split(f"_{self.pool_lookup[event_location]}")[0]
                # TODO see if this can be cleaned up

                # if we're placing a shop location it will be formatted as "shop_item" but we only have data per shop prefix
                location_name = f"{shop}_{len(self.created_multi_locations[shop])+1}"
                lookup_shop = shop if "(Requires_Charms)" not in shop else "Salubra"
                # fix because Salubra_(Requires_Charms) isn't actually in the source data

                rule = self.rule_lookup[lookup_shop]
                code = None if event_location not in unshuffled_location_lookup else self.location_name_to_id[location_name]
                region = self.multiworld.get_region(self.region_lookup[lookup_shop], self.player)

                loc = create_location((location_name, code), rule, item, region)
                costs = self.vanilla_shop_costs.get((shop, item[0]))
                if costs:
                    loc.costs = costs.pop()
                    loc.sort_costs()
                    loc.vanilla = True
                    # TODO remove/rework based on how sort_shops_by_cost ends up
                    # setting vanilla=True so shop sorting doesn't shuffle the price around
                self.created_multi_locations[shop].append(loc)
                loc.basename = shop  # for costsanity pool checking
                region.locations.append(loc)
                continue

            rule = self.rule_lookup[event_location]
            code = None if event_location not in unshuffled_location_lookup else self.location_name_to_id[event_location]
            region = self.multiworld.get_region(self.region_lookup[event_location], self.player)

            loc = create_location((event_location, code), rule, item, region)
            region.locations.append(loc)

    def add_shop_locations(self):
        for shop, locations in self.created_multi_locations.items():
            for index in range(len(locations), getattr(self.options, shop_to_option[shop]).value):
            # start index may be important if we pre-create unshuffled items in shops
                lookup_shop = shop if "(Requires_Charms)" not in shop else "Salubra"
                # fix because Salubra_(Requires_Charms) isn't actually in the source data

                costs = None
                if shop in shop_cost_types:
                    costs = {
                        term: self.random.randint(*self.ranges[term])
                        for term in shop_cost_types[shop]
                    }

                rule = self.rule_lookup[lookup_shop]
                region = self.multiworld.get_region(self.region_lookup[lookup_shop], self.player)
                location_name = f"{shop}_{index+1}"
                code = self.location_name_to_id[location_name]

                loc = self.location_class(self.player, location_name, code, region, )
                if rule:
                    self.set_rule(loc, self.create_rule(rule))
                if costs:
                    loc.costs = costs
                    loc.sort_costs()
                self.created_multi_locations[shop].append(loc)
                loc.basename = shop  # for costsanity pool checking
                region.locations.append(loc)
        self.add_extra_shop_locations(self.options.ExtraShopSlots.value)

    def add_extra_shop_locations(self, count):
        def create_location(shop):
            lookup_shop = shop if "(Requires_Charms)" not in shop else "Salubra"
            # fix because Salubra_(Requires_Charms) isn't actually in the source data

            costs = None
            if shop in shop_cost_types:
                costs = {
                    term: self.random.randint(*self.ranges[term])
                    for term in shop_cost_types[shop]
                }

            rule = self.rule_lookup[lookup_shop]
            region = self.multiworld.get_region(self.region_lookup[lookup_shop], self.player)
            index = len(self.created_multi_locations[shop])
            location_name = f"{shop}_{index+1}"
            code = self.location_name_to_id[location_name]

            loc = self.location_class(self.player, location_name, code, region)
            if rule:
                self.set_rule(loc, self.create_rule(rule))
            if costs:
                loc.costs = costs
                loc.sort_costs()
            self.created_multi_locations[shop].append(loc)
            loc.basename = shop  # for costsanity pool checking
            region.locations.append(loc)

        # Add additional shop items, as needed.
        if count > 0:
            shops = list(shop for shop, locations in self.created_multi_locations.items() if len(locations) < 16)
            if not self.options.EggShopSlots.value:  # No eggshop, so don't place items there
                shops.remove('Egg_Shop')

            if shops:
                for _ in range(count):
                    shop = self.random.choice(shops)
                    loc = create_location(shop)
                    if len(self.created_multi_locations[shop]) >= 16:
                        shops.remove(shop)
                        if not shops:
                            break

    def handle_starting_inventory(self):
        def precollect(item, code):
            self.multiworld.push_precollected(self.item_class(item, ItemClassification.progression, code, self.player))
        precollect("Downslash", self.item_name_to_id["Downslash"])
        for option, items in randomizable_starting_items.items():
            if not getattr(self.options, option):
                for item in items:
                    precollect(item, self.item_name_to_id[item])

# black box methods
    def create_rule(self, rule: Any) -> List[HKClause]:
        def parse_item_logic(reqs: list) -> Tuple[bool, Counter[str]]:  # Mapping[str, int]:
            # handle both keys of item name and keys of itemname>count
            ret: Counter[str] = Counter()
            for full_req in reqs:
                if "Grimmchild" == full_req:
                    full_req = "GRIMMCHILD"  # TODO fix in data
                if full_req.split("=0")[0] in logic_options:
                    req = full_req.split("=")
                    if len(req) == 2 and req[1] == "0":
                        # handle RANDOMELEVATORS=0 checking for the option off
                        logic_bool = False
                    else:
                        logic_bool = True
                    if getattr(self.options, logic_options[req[0]]) == logic_bool:
                        # if the option is true, remove the requirement and let continue
                        continue
                    else:
                        # else return skip_clause=True because the rest of the clause doesn't matter
                        return True, Counter({"FALSE": 1})

                req = full_req.split(">")
                if len(req) == 2:
                    ret[req[0]] = max(int(req[1]) + 1, ret[req[0]])
                    # handle item1>count so that another item1 in the clause is valid
                else:
                    ret[req[0]] = max(1, ret[req[0]])

            return False, ret

        def parse_refill_logic(reqs: List[str], valid_keys) -> bool:
            # i'm only expecting one req but it may be an empty list
            if reqs:
                key = reqs[0].split(":")[1]  # grab the second half
                if key in valid_keys:
                    return True
            return False

        def parse_cast_logic(req: str, valid_keys) -> Tuple[List[int], bool, bool]:
            search = re.search(r".*\[(.*)\]", req)
            if not search:
                # assume it means 1 cast
                return [1], False, False
            params = search.groups(1)[0].split(",")
            casts = [int(cast) for cast in params if not cast.startswith("before") and not cast.startswith("after")]
            before = parse_refill_logic([i for i in params if i.startswith("before")], valid_keys)
            after = parse_refill_logic([i for i in params if i.startswith("after")], valid_keys)
            return casts, before, after

        import re
        assert rule != []
        hk_rule = []
        for clause in rule:
            item_requirements = clause["item_requirements"]
            skip_clause = False
            shadeskips = [0]
            damage = [0]
            casts = [0]
            before = False
            after = False
            valid_keys = {key for key in ("ROOMSOUL", "AREASOUL", "MAPAREASOUL")}
            # TODO with ER change this logic
            if self.options.RandomizeCharms:  # TODO confirm
                valid_keys.update("ITEMSOUL")

            for req in clause["state_modifiers"]:
                # "$CASTSPELL", "$EQUIPPEDCHARM", "$SHRIEKPOGO", "$SHADESKIP", "$BENCHRESET", "$TAKEDAMAGE", "$HOTSPRINGRESET", "$STAGSTATEMODIFIER", "$SLOPEBALL", "$WARPTOSTART", "$FLOWERGET", "NOFLOWER=FALSE"
                if req.startswith("$EQUIPPEDCHARM"):
                    charm = re.search(r"\$EQUIPPEDCHARM\[(.*)\]", req).group(1)
                    if charm == "Kingsoul":
                        charm = "WHITEFRAGMENT"
                        item_requirements.append(charm)

                if req.startswith("$SHADESKIP"):
                    if not self.options.ShadeSkips:
                        skip_clause = True
                    else:
                        search = re.search(r".*\[(.*)HITS\]", req)
                        if not search:
                            shadeskip.append(1)
                        else:
                            shadeskip.append(search.groups(1)[0])

                if req.startswith("$CASTSPELL"):
                    # any skips will be marked, this covers dive uses too
                    c, b, a = parse_cast_logic(req, valid_keys)
                    casts += c
                    before = b if b else before
                    after = a if a else after
                if req.startswith("$SHRIEKPOGO"):
                    if True or not self.options.ShriekPogo:  # currently unsupported
                        skip_clause = True
                    else:
                        c, b, a = parse_cast_logic(req, valid_keys)
                        casts += c
                        before = b if b else before
                        after = a if a else after
                        item_requirements.append("SCREAM>1")
                if req.startswith("$SLOPEBALL"):
                    if True or not self.options.SlopeBall:  # currently unsupported
                        skip_clause = True
                    else:
                        c, b, a = parse_cast_logic(req, valid_keys)
                        casts += c
                        before = b if b else before
                        after = a if a else after
                        item_requirements.append("FIREBALL")
                    # can roll back to vs in mod
                # handled in logic directly
                if req.startswith("$TAKEDAMAGE"):
                    search = re.search(r".*\[(.*)HITS\]", req)
                    if not search:
                        damage.append(1)
                    else:
                        damage.append(search.groups(1)[0])
                    # if not self.options.DamageBoosts:
                    #     skip_clause = True

            # checking for a False condidtion before and after item parsing for short circuiting
            if skip_clause:
                continue
            state_requirements = HK_state_diff(
                shadeskip=max(*shadeskips, 0),
                damage=max(*damage, 0),
                twister_required=any(cast > 3 for cast in casts),
                total_casts=sum(casts),
                before=before,
                after=after,
                )
            skip_clause, items = parse_item_logic(item_requirements)
            if skip_clause:
                continue
            for item in items:
                assert item == "FALSE" or item in item_effects or item in logic_items or item in event_locations, \
                 f"{item} not found in advancements"
            hk_rule.append(HKClause(
                hk_item_requirements=items,
                hk_region_requirements=clause["location_requirements"],  # TODO: update
                hk_state_requirements=state_requirements,
                hk_state_modifiers=clause["state_modifiers"],
                ))

        # TODO seems unnecessary now that default_hk_rule exists
        # if len(hk_rule) == 0:
        #     return [HKClause(  # this rule can never be satisfied based on Options
        #         hk_item_requirements={"FALSE": 1},
        #         hk_region_requirements=[],  # TODO: update
        #         hk_state_modifiers=[],
        #         )]
        return hk_rule

    def set_rule(self, spot, rule):
        # set hk_rule instead of access_rule because our Location class defines a custom access_rule
        spot.hk_rule = rule

    def get_connections(self) -> "List[Tuple[str, str, Optional[Any]]]":
        from .ExtractedData import starts
        connection_map = super().get_connections()

        # find the correct StartLocation connection and make it accessible
        logic = [
                    {
                        "item_requirements": [],
                        "location_requirements": [],
                        "state_modifiers": []
                    }
                ]
        index, menu, start_location = [
            (index, connection[0], connection[1])
            for index, connection in enumerate(connection_map)
            if connection[0] == "Menu"
            and connection[1].startswith(starts[self.options.StartLocation.current_key])
            ][0]
        connection_map[index] = (menu, start_location, logic)

        return connection_map

    def get_location_map(self) -> "List[Tuple[str, str, Optional[Any]]]":
        # make our location_list off of location per option
        # and add any necessary location for logic to event_locations to be create later
        exclusions = self.white_palace_exclusions()
        self.event_locations += [
            location if location not in self.created_multi_locations else f"{location}_{item}"
            for option, pairs in pool_options.items()
            for item, location in zip(pairs[0], pairs[1])
            if not getattr(self.options, option)
            or location in exclusions
            ]
        location_list = [
            location
            for option, pairs in pool_options.items()
            for location in pairs[1]
            if location not in self.event_locations  # getattr(self.options, option)
            and location not in self.created_multi_locations
            ]

        # options not handled in pool_options
        if self.options.RandomizeElevatorPass:
            location_list.append("Elevator_Pass")
        else:
            self.event_locations.append("Elevator_Pass")

        if self.options.SplitCrystalHeart:
            if "Crystal_Heart" in location_list:
                location_list.append("Split_Crystal_Heart")
            else:
                self.event_locations.append("Split_Crystal_Heart")

        if self.options.SplitMantisClaw:
            location_name = "Mantis_Claw"
            if "Mantis_Claw" in location_list:
                location_list.remove(location_name)
                location_list += [f"{prefix}_{location_name}" for prefix in ["Left", "Right"]]
            else:
                self.event_locations.remove(location_name)
                self.event_locations += [f"{prefix}_{location_name}" for prefix in ["Left", "Right"]]

        if self.options.SplitMothwingCloak:
            if "Mothwing_Cloak" in location_list:
                location_list.append("Split_Mothwing_Cloak")
            else:
                self.event_locations.append("Split_Mothwing_Cloak")

        if self.options.RandomizeFocus:
            location_list.append("Focus")

        # TODO remove this bandaid
        if "Whispering_Root-Greenpath" in location_list:
            location_list.remove("Whispering_Root-Greenpath")
        if "Whispering_Root-Greenpath" in self.event_locations:
            self.event_locations.remove("Whispering_Root-Greenpath")

        # build out the map per location in the list
        location_map = [(region["name"], location, self.rule_lookup[location]) for region in self.rc_regions for location in region["locations"] if location in location_list]

        # TODO bandaid fix to make sure these don't ever get added to the pool
        assert not [obj for obj in location_map if obj[1] in ("Can_Warp_To_DG_Bench", "Can_Warp_To_Bench")]
        location_map = [obj for obj in location_map if obj[1] not in ("Can_Warp_To_DG_Bench", "Can_Warp_To_Bench")]
        return location_map

    def get_item_list(self) -> List[str]:
        junk: set[str] = set(("Downslash",))
        if self.options.RemoveSpellUpgrades:
            junk.update(("Abyss_Shriek", "Shade_Soul", "Descending_Dark"))
        exclusions = self.white_palace_exclusions()
        junk.update(exclusions)

        # build out item_table (including counts) by option, excluding items in junk
        item_table = [item for option, pairs in pool_options.items() for item in pairs[0] if getattr(self.options, option) and item not in junk]

        # options not handled in pool_options
        if self.options.SplitMothwingCloak and self.options.RandomizeSkills:
            item_name = "Mothwing_Cloak"
            item_table.remove(item_name)
            item_table += [f"{prefix}_{item_name}" for prefix in ["Left", "Right"]]

            item_table.remove("Shade_Cloak")
            item_table.append("Left_Mothwing_Cloak" if self.split_cloak_direction else "Right_Mothwing_Cloak")

        if self.options.SplitCrystalHeart and self.options.RandomizeSkills:
            item_name = "Crystal_Heart"
            item_table.remove(item_name)
            item_table += [f"{prefix}_{item_name}" for prefix in ["Left", "Right"]]

        if self.options.SplitMantisClaw and self.options.RandomizeSkills:
            item_name = "Mantis_Claw"
            item_table.remove(item_name)
            item_table += [f"{prefix}_{item_name}" for prefix in ["Left", "Right"]]

        # Grimmchild 2 always gets added, switch if needed
        if self.options.RandomizeGrimmkinFlames and self.options.RandomizeCharms:
            item_table.remove("Grimmchild2")
            item_table.append("Grimmchild1")

        if self.options.RandomizeElevatorPass:
            item_table.append("Elevator_Pass")

        return item_table

# ported from original HK
    def set_victory(self) -> None:
        multiworld = self.multiworld
        player = self.player
        goal = self.options.Goal
        if goal == Goal.option_hollowknight:
            multiworld.completion_condition[player] = lambda state: _hk_can_beat_thk(state, player)
        elif goal == Goal.option_siblings:
            multiworld.completion_condition[player] = lambda state: _hk_siblings_ending(state, player)
        elif goal == Goal.option_radiance:
            multiworld.completion_condition[player] = lambda state: _hk_can_beat_radiance(state, player)
        elif goal == Goal.option_godhome:
            multiworld.completion_condition[player] = lambda state: state.has("Defeated_Pantheon_5", player)
        elif goal == Goal.option_godhome_flower:
            multiworld.completion_condition[player] = lambda state: state.has("Godhome_Flower_Quest", player)
        else:
            # Any goal
            multiworld.completion_condition[player] = lambda state: _hk_can_beat_thk(state, player) or _hk_can_beat_radiance(state, player)

    def get_item_classification(self, name: str) -> ItemClassification:
        item_type = extracted_items[name]

        progression_charms = {
            # Baldur Killers
            "Grubberfly's_Elegy", "Weaversong", "Glowing_Womb",
            # Spore Shroom spots in fungal wastes and elsewhere
            "Spore_Shroom",
            # Tuk gives egg,
            "Defender's_Crest",
            # Unlocks Grimm Troupe
            "Grimmchild1", "Grimmchild2"
        }

        if name == "Mimic_Grub":
            classification = ItemClassification.trap
        elif name == "Godtuner":
            classification = ItemClassification.progression
        elif item_type in ("Grub", "DreamWarrior", "Root", "Egg", "Dreamer"):
            classification = ItemClassification.progression_skip_balancing
        elif item_type == "Charm" and name not in progression_charms:
            classification = ItemClassification.progression_skip_balancing
        elif item_type in ("Map", "Journal"):
            classification = ItemClassification.filler
        elif item_type in ("Ore", "Vessel"):
            classification = ItemClassification.useful
        elif name in item_effects or name in logic_items:
            classification = ItemClassification.progression
        else:
            classification = ItemClassification.filler
        return classification

    def get_filler_items(self) -> List[str]:
        if self.player not in self.cached_filler_items:
            fillers = ["One_Geo", "Soul_Refill"]
            exclusions = self.white_palace_exclusions()
            for group in (
                    'RandomizeGeoRocks', 'RandomizeSoulTotems', 'RandomizeLoreTablets', 'RandomizeJunkPitChests',
                    'RandomizeRancidEggs'
            ):
                if getattr(self.options, group):
                    # TODO hollow_knight_randomize_options and pool_options seem equivilant
                    fillers.extend(item for item in hollow_knight_randomize_options[group].items if item not in
                                   exclusions)
            self.cached_filler_items[self.player] = fillers
        return self.cached_filler_items[self.player]

    def get_filler_item_name(self) -> str:
        return self.random.choice(self.get_filler_items())

    def generate_early(self):
        options = self.options
        hybrid_chance = getattr(options, f"CostSanityHybridChance").value
        weights = {
            data.term: getattr(options, f"CostSanity{data.option}Weight").value
            for data in cost_terms.values()
        }
        if options.CostSanity:
            from Options import OptionError
            player_name = self.multiworld.get_player_name(self.player)
            if all(weight == 0 for weight in weights.values()):
                raise OptionError(f"CostSanity was on for {player_name} but no currencies are enabled")
            if all(weight == 0 for name, weight in weights.items() if name != "GEO"):
                raise OptionError(f"CostSanityHybridChance was on for {player_name} but no non-geo currencies are enabled for non-geo shops")
            # if hybrid_chance and len([name for name, weight in weights.items() if name is not "GEO" and weight != 0]):
            #     raise OptionError(f"temp")

        charm_costs = options.RandomCharmCosts.get_costs(self.random)
        self.charm_costs = options.PlandoCharmCosts.get_costs(charm_costs)
        for term, data in cost_terms.items():
            mini = getattr(options, f"Minimum{data.option}Price")
            maxi = getattr(options, f"Maximum{data.option}Price")
            # if minimum > maximum, flip them
            if mini.value > maxi.value:
                self.ranges[term] = maxi.value, mini.value
            else:
                self.ranges[term] = mini.value, maxi.value

        self.split_cloak_direction = self.random.randint(0, 1)

    @classmethod
    def stage_generate_early(cls, multiworld):
        groups = [
            group for id, group in multiworld.groups.items()
            if id in multiworld.get_game_groups(cls.game)
            and "Left_Mothwing_Cloak" in group["item_pool"]
            ]
        for group in groups:
            # for a group sharing split cloaks make sure they share the same direction
            split_cloak_direction = multiworld.random.randint(0, 1)
            for player in group["players"]:
                # override the random value set in generate_early
                multiworld.worlds[player].split_cloak_direction = split_cloak_direction

    @classmethod
    def stage_write_spoiler(cls, multiworld: MultiWorld, spoiler_handle):
        # hk_players = multiworld.get_game_players(cls.game)
        hk_worlds = multiworld.get_game_worlds(cls.game)
        spoiler_handle.write('\n\nCharm Notches:')
        # for player in hk_players:
        for hk_world in hk_worlds:
            player = hk_world.player
            name = multiworld.get_player_name(player)
            spoiler_handle.write(f'\n{name}\n')
            # hk_world: HKWorld = multiworld.worlds[player]
            for charm_number, cost in enumerate(hk_world.charm_costs):
                spoiler_handle.write(f"\n{charm_names[charm_number]}: {cost}")

        spoiler_handle.write('\n\nShop Prices:')
        # for player in hk_players:
        for hk_world in hk_worlds:
            player = hk_world.player
            name = multiworld.get_player_name(player)
            spoiler_handle.write(f'\n{name}\n')
            # hk_world: HKWorld = multiworld.worlds[player]

            if hk_world.options.CostSanity.value:
                for loc in sorted(
                    (
                        loc for loc in itertools.chain(*(region.locations for region in multiworld.get_regions(player)))
                        if loc.costs
                    ), key=operator.attrgetter('name')
                ):
                    spoiler_handle.write(f"\n{loc}: {loc.item} costing {loc.cost_text()}")
            else:
                for shop_name, locations in hk_world.created_multi_locations.items():
                    for loc in locations:
                        spoiler_handle.write(f"\n{loc}: {loc.item} costing {loc.cost_text()}")

    def white_palace_exclusions(self):
        path_of_pain_locations = {
            "Soul_Totem-Path_of_Pain_Below_Thornskip",
            "Lore_Tablet-Path_of_Pain_Entrance",
            "Soul_Totem-Path_of_Pain_Left_of_Lever",
            "Soul_Totem-Path_of_Pain_Hidden",
            "Soul_Totem-Path_of_Pain_Entrance",
            "Soul_Totem-Path_of_Pain_Final",
            "Soul_Totem-Path_of_Pain_Below_Lever",
            "Soul_Totem-Path_of_Pain_Second",
            "Journal_Entry-Seal_of_Binding",
            "Warp-Path_of_Pain_Complete",
            "Defeated_Path_of_Pain_Arena",
            "Completed_Path_of_Pain",
        }

        white_palace_checks = {
            "Soul_Totem-White_Palace_Final",
            "Soul_Totem-White_Palace_Entrance",
            "Lore_Tablet-Palace_Throne",
            "Soul_Totem-White_Palace_Left",
            "Lore_Tablet-Palace_Workshop",
            "Soul_Totem-White_Palace_Hub",
            "Soul_Totem-White_Palace_Right"
        }

        white_palace_events = {
            "White_Palace_03_hub",
            "White_Palace_13",
            "White_Palace_01",
            "Palace_Entrance_Lantern_Lit",
            "Palace_Left_Lantern_Lit",
            "Palace_Right_Lantern_Lit",
            "Palace_Atrium_Gates_Opened",
            "Warp-White_Palace_Atrium_to_Palace_Grounds",
            "Warp-White_Palace_Entrance_to_Palace_Grounds",
        }
        exclusions = set()
        wp = self.options.WhitePalace
        if wp <= WhitePalace.option_nopathofpain:
            exclusions.update(path_of_pain_locations)
        if wp <= WhitePalace.option_kingfragment:
            exclusions.update(white_palace_checks)
        if wp == WhitePalace.option_exclude:
            exclusions.add("King_Fragment")
            if self.options.RandomizeCharms:
                exclusions.update(white_palace_events)
        return exclusions

    def edit_effects(self, state, player: int, item: str, add: bool):
        for effect_name, effect_value in item_effects.get(item, {}).items():
            if add:
                state.prog_items[player][effect_name] += effect_value
            else:
                state.prog_items[player][effect_name] -= effect_value
                if state.prog_items[player][effect_name] < 1:
                    del (state.prog_items[player][effect_name])

    def collect(self, state, item: HKItem) -> bool:
        change = super(HKWorld, self).collect(state, item)
        if change:
            prog_items = state.prog_items[item.player]
            if item.name in {"Left_Mothwing_Cloak", "Right_Mothwing_Cloak"}:
                # # reset dash effects to 0 and recalc
                # prog_items['RIGHTDASH'] = 0
                # prog_items['LEFTDASH'] = 0
                # for _ in range(prog_items["Right_Mothwing_Cloak"]):
                #     self.edit_effects(state, "Right_Mothwing_Cloak", add=True)
                # for _ in range(prog_items["Left_Mothwing_Cloak"]):
                #     self.edit_effects(state, "Left_Mothwing_Cloak", add=True)

                # should just be able to add the new effect
                self.edit_effects(state, item.player, item.name, add=True)

                # if we have both cloaks keep them in step to account for shade cloak
                if prog_items.get('RIGHTDASH', 0) and \
                        prog_items.get('LEFTDASH', 0):
                    (prog_items["RIGHTDASH"], prog_items["LEFTDASH"]) = \
                        ([max(prog_items["RIGHTDASH"], prog_items["LEFTDASH"])] * 2)    
            else:
                self.edit_effects(state, item.player, item.name, add=True)

        return change

    def remove(self, state, item: HKItem) -> bool:
        change = super(HKWorld, self).remove(state, item)
        if change:
            prog_items = state.prog_items[item.player]
            if item.name in {"Left_Mothwing_Cloak", "Right_Mothwing_Cloak"}:
                # reset dash effects to 0 and recalc
                prog_items['RIGHTDASH'] = 0
                prog_items['LEFTDASH'] = 0
                for _ in range(prog_items["Right_Mothwing_Cloak"]):
                    self.edit_effects(state, item.player, "Right_Mothwing_Cloak", add=True)
                for _ in range(prog_items["Left_Mothwing_Cloak"]):
                    self.edit_effects(state, item.player, "Left_Mothwing_Cloak", add=True)

                # if we have both cloaks keep them in step to account for shade cloak
                if prog_items.get('RIGHTDASH', 0) and \
                        prog_items.get('LEFTDASH', 0):
                    (prog_items["RIGHTDASH"], prog_items["LEFTDASH"]) = \
                        ([max(prog_items["RIGHTDASH"], prog_items["LEFTDASH"])] * 2)
            else:
                self.edit_effects(state, item.player, item.name, add=False)

        return change

    def fill_slot_data(self):
        slot_data = {}

        options = slot_data["options"] = {}
        for option_name in hollow_knight_options:
            option = getattr(self.options, option_name)
            try:
                optionvalue = int(option.value)
            except TypeError:
                pass  # C# side is currently typed as dict[str, int], drop what doesn't fit
            else:
                options[option_name] = optionvalue

        # 32 bit int
        slot_data["seed"] = self.random.randint(-2147483647, 2147483646)

        # Backwards compatibility for shop cost data (HKAP < 0.1.0)
        if not self.options.CostSanity:
            for shop, terms in shop_cost_types.items():
                unit = cost_terms[next(iter(terms))].option
                if unit == "Geo":
                    continue
                slot_data[f"{unit}_costs"] = {
                    loc.name: next(iter(loc.costs.values()))
                    for loc in self.created_multi_locations[shop]
                }

        # HKAP 0.1.0 and later cost data.
        location_costs = {}
        for region in self.multiworld.get_regions(self.player):
            for location in region.locations:
                if location.costs:
                    location_costs[location.name] = location.costs
        slot_data["location_costs"] = location_costs

        slot_data["notch_costs"] = self.charm_costs

        return slot_data

    def sort_shops_by_cost(self):
        for shop, locations in self.created_multi_locations.items():
            randomized_locations = list(loc for loc in locations if not loc.vanilla)
            prices = sorted(
                (loc.costs for loc in randomized_locations),
                key=lambda costs: (len(costs),) + tuple(costs.values())
            )
            for loc, costs in zip(randomized_locations, prices):
                loc.costs = costs

    def apply_costsanity(self):
        setting = self.options.CostSanity.value
        if not setting:
            return  # noop

        def _compute_weights(weights: dict, desc: str) -> Dict[str, int]:
            if all(x == 0 for x in weights.values()):
                logger.warning(
                    f"All {desc} weights were zero for {self.multiworld.player_name[self.player]}."
                    f" Setting them to one instead."
                )
                weights = {k: 1 for k in weights}

            return {k: v for k, v in weights.items() if v}

        random = self.random
        hybrid_chance = getattr(self.options, f"CostSanityHybridChance").value
        weights = {
            data.term: getattr(self.options, f"CostSanity{data.option}Weight").value
            for data in cost_terms.values()
        }
        weights_geoless = dict(weights)
        del weights_geoless["GEO"]

        weights = _compute_weights(weights, "CostSanity")
        weights_geoless = _compute_weights(weights_geoless, "Geoless CostSanity")

        if hybrid_chance > 0:
            if len(weights) == 1:
                logger.warning(
                    f"Only one cost type is available for CostSanity in {self.multiworld.player_name[self.player]}'s world."
                    f" CostSanityHybridChance will not trigger in geo shop locations."
                )
            if len(weights_geoless) == 1:
                logger.warning(
                    f"Only one cost type is available for CostSanity in {self.multiworld.player_name[self.player]}'s world."
                    f" CostSanityHybridChance will not trigger in geoless locations."
                )

        for region in self.multiworld.get_regions(self.player):
            for location in region.locations:
                if location.vanilla:
                    continue
                if not location.costs:
                    continue
                if location.name == "Vessel_Fragment-Basin":
                    continue
                if setting == CostSanity.option_notshops and location.basename in self.created_multi_locations:   # multi_locations:
                    continue
                if setting == CostSanity.option_shopsonly and location.basename not in self.created_multi_locations:  # multi_locations:
                    continue
                if location.basename in {'Grubfather', 'Seer', 'Egg_Shop'}:
                    our_weights = dict(weights_geoless)
                else:
                    our_weights = dict(weights)

                rolls = 1
                if random.randrange(100) < hybrid_chance:
                    rolls = 2

                if rolls > len(our_weights):
                    terms = list(our_weights.keys())  # Can't randomly choose cost types, using all of them.
                else:
                    terms = []
                    for _ in range(rolls):
                        term = random.choices(list(our_weights.keys()), list(our_weights.values()))[0]
                        del our_weights[term]
                        terms.append(term)

                location.costs = {term: random.randint(*self.ranges[term]) for term in terms}
                location.sort_costs()
