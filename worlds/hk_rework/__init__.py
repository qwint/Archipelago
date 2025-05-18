import logging
import itertools
import operator

from copy import deepcopy
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple, NamedTuple, Optional, cast, Set

from BaseClasses import Location, Item, ItemClassification, Tutorial, CollectionState, MultiWorld, Region, Entrance, LocationProgressType
from worlds.AutoWorld import WebWorld

from .template_world import RandomizerCoreWorld

from .state_mixin import resource_state_handler, RCStateVariable, HKLogicMixin  # all that's needed to add the mixin
from .data.region_data import regions, locations, transition_to_region_map  # transitions
from .data.location_data import multi_locations, locations as locations_metadata
from .data.option_data import logic_options, pool_options
from .data.item_data import progression_effect_lookup, non_progression_items, affected_terms_by_item, affecting_items_by_term

from .constants import shop_cost_types, randomizable_starting_items, gamename, base_id, SIMPLE_STATE_LOGIC
from .Options import hollow_knight_options, hollow_knight_randomize_options, Goal, WhitePalace, CostSanity, \
    shop_to_option, HKOptions
from .Rules import cost_terms, _hk_can_beat_thk, _hk_siblings_ending, _hk_can_beat_radiance
from .Charms import names as charm_names, charm_name_to_id

from .Items import item_name_groups, item_name_to_id  # item_table, lookup_type_to_names, item_name_groups

logger = logging.getLogger("Hollow Knight")


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


class HKClause(NamedTuple):
    # Dict of item: count for state.has_all_counts()
    hk_item_requirements: Dict[str, int]

    # list of regions that need to reachable
    hk_region_requirements: List[str]

    # list of resource state terms for the clause
    hk_state_requirements: List[RCStateVariable]


# default logicless rule for short circuting
default_hk_rule = [HKClause(
    hk_item_requirements={"True": 1},
    hk_region_requirements=[],
    hk_state_requirements=[],
    )]


def cacheless_hk_access_rule(spot: Location | Entrance, state: CollectionState) -> bool:
    for clause in spot.hk_rule:
        # check regions first when evaluating locations because cache should be set by now
        for region in clause.hk_region_requirements:
            if not state.can_reach_region(region, spot.player):
                return False
        if state.has_all_counts(clause.hk_item_requirements, spot.player):
            if state._hk_apply_and_validate_state(clause, spot.parent_region):
                return True
    # no clause was True,
    return False


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
        self.access_set = False
        self.basename = basename or name
        self.vanilla = vanilla
        if costs:
            self.costs = dict(costs)
            self.sort_costs()
        else:
            self.costs = None

    def set_hk_rule(self, rules: List[HKClause]):
        # pass
        self.hk_rule = rules
        self.access_set = True
        # self.current_access_rule = self.hk_access_rule

    def access_rule(self, state: CollectionState) -> bool:
        if self.costs:
            logic_costs = {term: amount for term, amount in self.costs.items() if term != "GEO"}
            if not state.has_all_counts(logic_costs, self.player):
                return False
        return self.hk_access_rule(state) if self.access_set else True

    hk_access_rule = cacheless_hk_access_rule

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

    def set_hk_rule(self, rules: List[HKClause]):
        if rules == default_hk_rule:
            return
        self.hk_rule = rules
        indirection_connections = [region for clause in rules for region in clause.hk_region_requirements]
        if indirection_connections:
            multiworld = self.parent_region.multiworld
            for region in indirection_connections:
                reg = multiworld.get_region(region, self.player)
                multiworld.register_indirect_condition(reg, self)
        self.access_rule = self.hk_access_rule

    def access_rule(self, state: CollectionState) -> bool:
        state._hk_entrance_clause_cache[self.player][self.name] = {0: True}
        state._hk_apply_and_validate_state(default_hk_rule[0], self.parent_region, target_region=self.connected_region)
        return True

    if SIMPLE_STATE_LOGIC:
        hk_access_rule = cacheless_hk_access_rule
    else:
        def hk_access_rule(self, state: CollectionState) -> bool:
            assert self.hk_rule != default_hk_rule, "should never have to be here"
            # if self.hk_rule == default_hk_rule:
            #     state._hk_entrance_clause_cache[self.player][self.name] = {0: True}
            #     state._hk_apply_and_validate_state(default_hk_rule[0], self.parent_region, target_region=self.connected_region)
            #     return True
            if self.name not in state._hk_entrance_clause_cache[self.player]:
                # if there's no cache for this entrance, make one with everything False
                cache = state._hk_entrance_clause_cache[self.player][self.name] = \
                    {index: False for index in range(len(self.hk_rule))}
            else:
                cache = state._hk_entrance_clause_cache[self.player][self.name]

            # check every clause, caching item state accessibility
            valid_clauses = False
            for index, clause in enumerate(self.hk_rule):
                if cache[index] or state.has_all_counts(clause.hk_item_requirements, self.player):
                    cache[index] = True

                    # region sweep might not be done, so checking items is likely faster
                    reachable = True
                    for region in clause.hk_region_requirements:
                        if not state.can_reach_region(region, self.player):
                            reachable = False
                    if reachable and state._hk_apply_and_validate_state(clause, self.parent_region, target_region=self.connected_region):
                        valid_clauses = True

            return valid_clauses


class HKRegion(Region):
    entrance_type = HKEntrance

    if not SIMPLE_STATE_LOGIC:
        def can_reach(self, state) -> bool:
            if self in state.reachable_regions[self.player]:
                return True
            if not state.stale[self.player] and not state._hk_stale[self.player]:
                # if the cache is updated we can use the cache
                return super().can_reach(state)
            if state._hk_stale[self.player]:
                state._hk_sweep(self.player)
            return super().can_reach(state)


shop_locations = multi_locations
event_locations = [location["name"] for location in locations if location["is_event"]
                   and location["name"] not in ("Can_Warp_To_DG_Bench", "Can_Warp_To_Bench")]
vanilla_cost_data = [pair for option in pool_options.values() for pair in option if pair["costs"]]
vanilla_location_costs = {
    pair["location"]: {cost["term"]: cost["amount"] for cost in pair["costs"]}
    for pair in vanilla_cost_data
    if pair["location"] not in multi_locations
    }
vanilla_shop_costs = defaultdict(list)
for i in vanilla_cost_data:
    if i["location"] not in multi_locations:
        continue
    costs = {cost["term"]: cost["amount"] for cost in i["costs"]}
    vanilla_shop_costs[(i["location"], i["item"])].append(costs)

hk_regions = [region for region in cast(List[Dict[str, Any]], regions) if not region["name"].startswith("$")]
hk_locations = [location for location in cast(List[Dict[str, Any]], locations)]


datapackage_locs = {loc["name"] for loc in locations if not loc["is_event"]}
datapackage_locs = [loc for loc in datapackage_locs if loc not in multi_locations]
datapackage_locs += [f"{shop}_{i+1}" for shop in multi_locations for i in range(16) if shop != "Start"]
location_name_to_id = {
    location_name: location_id for location_id, location_name in
    enumerate(sorted(datapackage_locs), start=0x1000000)
}


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
        pair["location"] if pair["location"] not in multi_locations else f"{pair['location']}_{pair['item']}": pair["item"]
        for option, pairs in pool_options.items()
        for pair in pairs
        }
    entrance_by_term: Dict[str, List[str]]

    cached_filler_items: Dict[int, List[str]] = {}  # per player cache
    event_locations: List[str]
    ranges: Dict[str, Tuple[int, int]]
    charm_costs: List[int]
    charm_names_and_costs: dict[int, dict[str, int]] = {}  # per player cache

    def __init__(self, multiworld, player):
        super(HKWorld, self).__init__(multiworld, player)
        self.created_multi_locations: Dict[str, List[HKLocation]] = {
            location: list() for location in multi_locations
            if location != "Start"
        }
        self.ranges = {}
        self.created_shop_items = 0
        self.vanilla_shop_costs = deepcopy(vanilla_shop_costs)
        self.event_locations = deepcopy(event_locations)
        self.entrance_by_term = defaultdict(list)

    # def get_region_list(self) -> List[str]:
    #     return super().get_region_list()

# RandomizerCoreWorld overrides
    def create_regions(self):
        super().create_regions()
        self.add_vanilla_connections()
        self.add_all_events()
        self.add_shop_locations()

        if "King_Fragment" in self.white_palace_exclusions():
            self.multiworld.get_location("King_Fragment", self.player).progress_type = LocationProgressType.EXCLUDED

        location_to_option = {key["location"]: option for option, keys in pool_options.items() for key in keys}
        location_to_option["Elevator_Pass"] = "RandomizeElevatorPass"
        for location, costs in vanilla_location_costs.items():
            if self.options.AddUnshuffledLocations or getattr(self.options, location_to_option[location]):
                self.multiworld.get_location(location, self.player).costs = costs

    def create_items(self):
        pool_count = super().create_items()

        item_difference = \
            pool_count - len(self.multiworld.get_unfilled_locations(self.player))
        if item_difference > 0:
            self.add_extra_shop_locations(item_difference)

        self.handle_starting_inventory()
        self.apply_costsanity()
        self.sort_shops_by_cost()

# extra handling
    def add_vanilla_connections(self):
        from .data.trando_data import transitions

        transition_name_to_region = {
            transition: region["name"]
            for region in self.rc_regions
            for transition in region["transitions"]
            }
        vanilla_connections = [
            (transition_name_to_region[name], transition_name_to_region[t["vanilla_target"]], name)
            for name, t in transitions.items() if t["sides"] != "OneWayOut"
            ]

        for connection in vanilla_connections:
            region1 = self.multiworld.get_region(connection[0], self.player)
            region2 = self.multiworld.get_region(connection[1], self.player)
            region1.connect(region2, connection[2])

    def add_all_events(self):
        # lookup table of locations that need to be created with their item like events but need ids like non-events
        if self.options.AddUnshuffledLocations:
            unshuffled_location_lookup = {
                pair["locations"] if pair["locations"] not in self.created_multi_locations else f"{pair['locations']}_{pair['items']}": option
                for option, pairs in pool_options.items()
                for pair in pairs
                # TODO double check logic
                }
        else:
            unshuffled_location_lookup = {}

        # meant to add events used in logic and to add any non-randomized item/locations as events
        # also makes the unshuffled ap items if add_unshuffled is true
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
                # TODO handle this better / get better extracted itemdata

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

    def add_shop_location(self, shop, index):
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

        loc = self.location_class(self.player, location_name, code, region)
        if rule:
            self.set_rule(loc, self.create_rule(rule))
        if costs:
            loc.costs = costs
            loc.sort_costs()
        self.created_multi_locations[shop].append(loc)
        loc.basename = shop  # for costsanity pool checking
        region.locations.append(loc)

    def add_shop_locations(self):
        # TODO logicless event items that get culled don't take up shop space
        for shop, locations in self.created_multi_locations.items():
            for index in range(len(locations), getattr(self.options, shop_to_option[shop]).value):
                # start index may be important if we pre-create unshuffled items in shops
                self.add_shop_location(shop, index)
        self.add_extra_shop_locations(self.options.ExtraShopSlots.value)

    def add_extra_shop_locations(self, count):
        # Add additional shop items, as needed.
        if count > 0:
            shops = list(shop for shop, locations in self.created_multi_locations.items() if len(locations) < 16)
            if not self.options.EggShopSlots.value:  # No eggshop, so don't place items there
                shops.remove('Egg_Shop')

            if shops:
                for _ in range(count):
                    shop = self.random.choice(shops)
                    index = len(self.created_multi_locations[shop])
                    loc = self.add_shop_location(shop, index)
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
        # TODO consider caching on these as they should be deterministic, but they need options so only deterministic per world
        def parse_item_logic(reqs: list) -> Tuple[bool, Counter[str]]:  # Mapping[str, int]:
            # handle both keys of item name and keys of itemname>count
            ret: Counter[str] = Counter()
            for full_req in reqs:
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

        assert rule != []
        hk_rule = []
        for clause in rule:
            item_requirements = clause["item_requirements"]
            state_requirements = []
            skip_clause = False

            for req in clause["state_modifiers"]:
                # print(req)
                if req == "NOFLOWER=FALSE":
                    # TODO there's a handler but flowerprovider is not working yet
                    continue
                handler = resource_state_handler.get_handler(req)
                if handler.can_exclude(self.options):
                    skip_clause = True
                else:
                    state_requirements.append(handler)

            # checking for a False condidtion before and after item parsing for short circuiting
            if skip_clause:
                continue
            skip_clause, items = parse_item_logic(item_requirements)
            if skip_clause:
                continue
            for item in items:
                assert item == "FALSE" or item in affecting_items_by_term or item in affected_terms_by_item or item in event_locations, f"{item} not found in advancements"
            hk_rule.append(HKClause(
                hk_item_requirements=dict(items),
                hk_region_requirements=clause["region_requirements"],
                hk_state_requirements=state_requirements,
                ))

        return hk_rule

    def set_rule(self, spot, rule):
        # set hk_rule instead of access_rule because our Location class defines a custom access_rule
        if isinstance(spot, HKEntrance):
            if SIMPLE_STATE_LOGIC:
                for i, clause in reversed(list(enumerate(rule))):
                    if clause.hk_state_requirements:
                        # skip all entrances with state requirements so we know they're always repeatable
                        del rule[i]
            relevant_terms = {term for clause in rule for term in clause.hk_item_requirements.keys()}
            relevant_terms.update({term for clause in rule for s_var in clause.hk_state_requirements for term in s_var.GetTerms()})
            for term in relevant_terms:
                # could keep this a static method by doing spot.parent_region.multiworld.worlds[spot.player] but ugh
                self.entrance_by_term[term].append(spot.name)
        else:
            if SIMPLE_STATE_LOGIC:
                for clause in rule:
                    if clause.hk_state_requirements:
                        # assume for now that there will only be additional items for now, we can change this api later
                        for handler in clause.hk_state_requirements:
                            handler.add_simple_item_reqs(clause.hk_item_requirements)

        spot.set_hk_rule(rule)

    def get_connections(self) -> "List[Tuple[str, str, Optional[Any]]]":
        from .data.trando_data import starts
        connection_map = super().get_connections()

        key = self.options.StartLocation.current_key
        start_region = transition_to_region_map[starts[key]["granted_transition"]]
        connection_map.append(("Menu", start_region, starts[key]["logic"]))

        return connection_map

    def get_location_map(self) -> "List[Tuple[str, str, Optional[Any]]]":
        # Vanilla placements of the following items have no impact on logic, thus we can avoid creating these items and
        # locations entirely when the option to randomize them is disabled.
        logicless_options = {
            "RandomizeVesselFragments", "RandomizeGeoChests", "RandomizeJunkPitChests", "RandomizeRelics",
            "RandomizeMaps", "RandomizeJournalEntries", "RandomizeGeoRocks", "RandomizeBossGeo",
            "RandomizeLoreTablets", "RandomizeSoulTotems", "RandomizeLifebloodCocoons",
        }

        # make our location_list off of location per option
        # and add any necessary location for logic to event_locations to be create later
        exclusions = self.white_palace_exclusions()
        if "King_Fragment" in exclusions:
            exclusions.remove("King_Fragment")

        self.event_locations += [
            pair["location"] if pair["location"] not in self.created_multi_locations else f"{pair['location']}_{pair['item']}"
            for option, pairs in pool_options.items()
            for pair in pairs
            # TODO confirm logic
            if (not getattr(self.options, option) and (option not in logicless_options or self.options.AddUnshuffledLocations))
            or pair["location"] in exclusions
            ]

        location_list = [
            pair["location"]
            for option, pairs in pool_options.items()
            for pair in pairs
            if pair["location"] not in self.event_locations and getattr(self.options, option)
            and pair["location"] not in self.created_multi_locations
            ]

        # options not handled in pool_options
        if self.options.RandomizeElevatorPass:
            location_list.append("Elevator_Pass")
        # logic if random elevators is off just checks region access instead
        else:
            self.event_locations.append("Elevator_Pass")

        if self.options.SplitCrystalHeart:
            if "Crystal_Heart" in location_list:
                location_list.append("Split_Crystal_Heart")
            else:
                self.event_locations.append("Split_Crystal_Heart")

        directions = ("Left", "Right")
        if self.options.SplitMantisClaw:
            location_name = "Mantis_Claw"
            if "Mantis_Claw" in location_list:
                location_list.remove(location_name)
                location_list += [f"{prefix}_{location_name}" for prefix in directions]
            else:
                self.event_locations.remove(location_name)
                self.event_locations += [f"{prefix}_{location_name}" for prefix in directions]

        if self.options.SplitMothwingCloak:
            if "Mothwing_Cloak" in location_list:
                location_list.append("Split_Mothwing_Cloak")
            else:
                self.event_locations.append("Split_Mothwing_Cloak")

        if self.options.RandomizeFocus:
            location_list.append("Focus")

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
        if "King_Fragment" in exclusions:
            exclusions.remove("King_Fragment")
        junk.update(exclusions)

        # build out item_table (including counts) by option, excluding items in junk
        item_table = [
            pair["item"]
            for option, pairs in pool_options.items()
            for pair in pairs
            if getattr(self.options, option) and pair["item"] not in junk
        ]

        # options not handled in pool_options
        directions = ("Left", "Right")
        if self.options.SplitMothwingCloak and self.options.RandomizeSkills:
            item_name = "Mothwing_Cloak"
            item_table.remove(item_name)
            item_table += [f"{prefix}_{item_name}" for prefix in directions]

            item_table.remove("Shade_Cloak")
            item_table.append("Left_Mothwing_Cloak" if self.split_cloak_direction else "Right_Mothwing_Cloak")

        if self.options.SplitCrystalHeart and self.options.RandomizeSkills:
            item_name = "Crystal_Heart"
            item_table.remove(item_name)
            item_table += [f"{prefix}_{item_name}" for prefix in directions]

        if self.options.SplitMantisClaw and self.options.RandomizeSkills:
            item_name = "Mantis_Claw"
            item_table.remove(item_name)
            item_table += [f"{prefix}_{item_name}" for prefix in directions]

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

        from .data.item_data import non_progression_items, affecting_items_by_term

        if name in non_progression_items:
            classification = ItemClassification.filler
            assert name not in progression_effect_lookup
        elif name in progression_effect_lookup:
            classification = ItemClassification.progression
        if name in affecting_items_by_term["DREAMER"] or \
                name in affecting_items_by_term["GRUBS"] or \
                name in affecting_items_by_term["ESSENCE"] or \
                name in affecting_items_by_term["RANCIDEGGS"]:
            classification |= ItemClassification.skip_balancing
        if name in affecting_items_by_term["PALEORE"] or name in affecting_items_by_term["VESSELFRAGMENTS"]:
            classification |= ItemClassification.useful
        if (name not in progression_charms and name in affecting_items_by_term["CHARMS"]):
            classification |= ItemClassification.skip_balancing
        if name == "Mimic_Grub":
            classification |= ItemClassification.trap

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

        self.charm_names_and_costs[self.player] = {name: (charm_costs[index] if name != "Void_Heart" else 0)
                                                   for name, index in charm_name_to_id.items()}

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

    def white_palace_exclusions(self) -> Set[str]:
        exclusions = set()
        wp = self.options.WhitePalace
        if wp <= WhitePalace.option_nopathofpain:
            exclusions.update({
                name for name, loc in locations_metadata.items()
                if loc["titled_area"] == "Path of Pain"
                })
        if wp <= WhitePalace.option_kingfragment:
            exclusions.update({
                name for name, loc in locations_metadata.items()
                if loc["map_area"] == "White Palace"
                # will add in last step if needed
                and name != "King_Fragment"
                })

        loc_to_item = {pair["location"]: pair["item"] for pool in pool_options.values() for pair in pool}
        exclusions.update({loc_to_item[loc] for loc in exclusions if loc in loc_to_item})

        if wp == WhitePalace.option_exclude:
            exclusions.add("King_Fragment")
        return exclusions

    @staticmethod
    def edit_effects(state, player: int, item_effects: Dict[str, int], add: bool):
        if add:
            for effect_name, effect_value in item_effects.items():
                state.prog_items[player][effect_name] += effect_value
        else:
            for effect_name, effect_value in item_effects.items():
                state.prog_items[player][effect_name] -= effect_value
                if state.prog_items[player][effect_name] < 1:
                    del (state.prog_items[player][effect_name])

    def handle_effect(self, item_name, lookup, state, player):
        def check_item_logic(condition, state, player) -> bool:
            assert not condition["location_requirements"]
            assert not condition["region_requirements"]
            assert not condition["state_modifiers"]
            item_requirements = condition["item_requirements"]
            result = True
            for req in item_requirements:
                if ">" in req:
                    item, value = (*req.split(">"),)
                    result = result and state.count(item, player) > int(value)
                elif "<" in req:
                    item, value = (*req.split("<"),)
                    result = result and state.count(item, player) < int(value)
                elif "=" in req:
                    item, value = (*req.split("="),)
                    assert value.isdigit(), f"requirement {req} not supported"
                    result = result and state.count(item, player) == int(value)
                else:
                    # assume entire req is term
                    result = result and state.has(req, player)
            return result

        if lookup["type"] == "conditional":
            if any(
                    check_item_logic(condition, state, player)
                    for condition in lookup["condition"]
                    ):
                ret = lookup["effect"]
            else:
                return {}
        elif lookup["type"] == "branching":
            for branch in lookup["conditionals"]:
                if any(
                        check_item_logic(condition, state, player)
                        for condition in branch["condition"]
                        ):
                    ret = branch["effect"]
                    break
            else:
                # if none true use the parent else instead
                ret = lookup["else"]

        elif lookup["type"] == "incrementTerms":
            return lookup["effects"]
        elif lookup["type"] == "threshold":
            count = state._hk_processed_item_cache[player][lookup["term"]]
            if count == lookup["threshold"]:
                return lookup["at_threshold"]
            elif count < lookup["threshold"]:
                return lookup["below_threshold"]
            else:
                return lookup["above_threshold"]

        else:
            raise f"unknown type {lookup['type']}"
            return

        if "type" in ret:
            return self.handle_effect(item_name, ret, state, player)
        else:
            raise f"unknown effect {ret}"
            return

    def collect(self, state, item: HKItem) -> bool:
        if item.advancement:
            player = item.player
            if item.name in charm_name_to_id:
                state.prog_items[player][f"CHARM{charm_name_to_id[item.name] + 1}"] += 1
            if item.name not in progression_effect_lookup:
                # handle events that don't have effects by adding them as their own terms
                state.prog_items[player][item.name] += 1
            else:
                lookup = progression_effect_lookup[item.name]
                add = True

                effects = self.handle_effect(item.name, lookup, state, player)
                self.edit_effects(state, player, effects, add)
                if lookup["type"] in ("conditional", "branching",):
                    state._hk_processed_item_cache[player][item.name] += 1
                elif lookup["type"] == "threshold":
                    # increment term before checking threshold
                    state._hk_processed_item_cache[player][lookup["term"]] += 1

                for term in effects.keys():
                    state._hk_per_player_sweepable_entrances[player].update(self.entrance_by_term[term])
            if not SIMPLE_STATE_LOGIC:
                state._hk_stale[item.player] = True
        return item.advancement

    def remove(self, state, item: HKItem) -> bool:
        if item.advancement:
            player = item.player
            if item.name in charm_name_to_id:
                state.prog_items[player][f"CHARM{charm_name_to_id[item.name] + 1}"] -= 1
            if item.name not in progression_effect_lookup:
                # handle events that don't have effects by adding them as their own terms
                state.prog_items[player][item.name] -= 1
            else:
                lookup = progression_effect_lookup[item.name]
                add = False

                if lookup["type"] in ("conditional", "branching",):
                    state._hk_processed_item_cache[player][item.name] -= 1
                    reset_terms = affected_terms_by_item[item.name]
                    for term in reset_terms:
                        state.prog_items[player][term] = 0
                    recalc_items = {item for term in reset_terms for item in affecting_items_by_term[term]}
                    owned_relevant_items = [
                        item
                        for item, count in state._hk_processed_item_cache[player].items()
                        for count in range(count)
                        if item in recalc_items
                        ]
                    for recalc_item in owned_relevant_items:
                        effects = self.handle_effect(item.name, progression_effect_lookup[recalc_item], state, player)
                        # filter effects to just the ones we reset then add them to state
                        self.edit_effects(
                            state,
                            player,
                            {key: effects[key] for key in effects if key in reset_terms},
                            True
                            )
                else:
                    if lookup["type"] == "threshold":
                        # increment term before checking threshold
                        state._hk_processed_item_cache[player][lookup["term"]] -= 1
                    self.edit_effects(state, player, self.handle_effect(item.name, lookup, state, player), add)

            state._hk_entrance_clause_cache[item.player] = {}
            state._hk_per_player_sweepable_entrances[item.player] = {
                entrance.name for entrance in self.multiworld.get_region("Menu", self.player).exits
                }

            if not SIMPLE_STATE_LOGIC:
                state._hk_stale[item.player] = True
        return item.advancement

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
            if not randomized_locations:
                return
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
