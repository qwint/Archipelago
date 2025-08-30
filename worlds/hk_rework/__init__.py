import itertools
import logging
import operator
from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any, ClassVar, cast

from BaseClasses import CollectionState, ItemClassification, LocationProgressType, MultiWorld
from Options import OptionError
from worlds.AutoWorld import World

from .charms import charm_name_to_id, charm_names
from .classes import HKClause, HKEntrance, HKItem, HKLocation, HKRegion, HKSettings, HKWeb
from .constants import gamename, randomizable_starting_items, shop_cost_types
from .data.ids import item_name_to_id, location_name_to_id
from .data.item_effects import (
    affected_terms_by_item,
    affecting_items_by_term,
    non_progression_items,
    progression_effect_lookup,
)
from .data.location_data import locations as locations_metadata
from .data.location_data import multi_locations
from .data.option_data import logic_options, pool_options
from .data.region_structure import locations, regions, transition_to_region_map
from .data.trando_data import starts, transitions
from .items import item_name_groups
from .options import (
    CostSanity,
    Goal,
    GrubHuntGoal,
    HKOptions,
    WhitePalace,
    hollow_knight_options,
    shop_to_option,
)
from .rules import cost_terms
from .state_mixin import HKLogicMixin as HKLogicMixin
from .resource_state_vars import ResourceStateHandler
from .resource_state_vars.cast_spell import NearbySoul
from .template_world import RandomizerCoreWorld

logger = logging.getLogger("Hollow Knight")


shop_locations = multi_locations
event_locations = [location["name"] for location in locations if location["is_event"]
                   and location["name"] not in ("Can_Warp_To_DG_Bench", "Can_Warp_To_Bench")]
vanilla_cost_data = [pair for option in pool_options.values() for pair in option["vanilla"] if pair["costs"]]
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

hk_regions = [
    region for region in cast(list[dict[str, Any]], regions)
    if not region["name"].startswith("$") and not region["name"] == "Bench-Godhome_Roof"
]
hk_locations = cast(list[dict[str, Any]], list(locations))


class HKWorld(RandomizerCoreWorld, World):
    """Beneath the fading town of Dirtmouth sleeps a vast, ancient kingdom. Many are drawn beneath the surface,
    searching for riches, or glory, or answers to old secrets.

    As the enigmatic Knight, you’ll traverse the depths, unravel its mysteries and conquer its evils.
    """  # from https://www.hollowknight.com  # noqa: RUF002

    game = gamename
    web = HKWeb()
    location_name_to_id = location_name_to_id
    item_name_to_id = item_name_to_id
    options_dataclass = HKOptions
    options: HKOptions
    settings: ClassVar[HKSettings]
    item_name_groups = item_name_groups

    rc_regions: list[dict[str, Any]] = hk_regions
    rc_locations: list[dict[str, Any]] = hk_locations
    item_class = HKItem
    location_class = HKLocation
    region_class = HKRegion

    rule_lookup: ClassVar[dict[str, str]] = {location["name"]: location["logic"] for location in hk_locations}
    region_lookup: ClassVar[dict[str, str]] = {location: r["name"] for r in hk_regions for location in r["locations"]}
    entrance_by_term: dict[str, list[str]]

    cached_filler_items: ClassVar[dict[int, list[str]]] = {}  # per player cache
    grub_count: int
    grub_player_count: dict[int, int]
    event_locations: list[str]
    ranges: dict[str, tuple[int, int]]
    charm_costs: list[int]
    charm_names_and_costs: ClassVar[dict[int, dict[str, int]]] = {}  # per player cache
    soul_modes: ClassVar[dict[int, NearbySoul]] = {}  # per player cache

    def __init__(self, multiworld, player):
        super().__init__(multiworld, player)
        self.created_multi_locations: dict[str, list[HKLocation]] = {
            location: [] for location in multi_locations
            if location != "Start"
        }
        self.ranges = {}
        self.created_shop_items = 0
        self.vanilla_shop_costs = deepcopy(vanilla_shop_costs)
        self.event_locations = deepcopy(event_locations)
        self.entrance_by_term = defaultdict(list)

    def white_palace_exclusions(self) -> set[str]:
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

        # TODO update or remove this
        # loc_to_item = {pair["location"]: pair["item"] for pool in pool_options.values() for pair in pool}
        # exclusions.update({loc_to_item[loc] for loc in exclusions if loc in loc_to_item})

        if wp == WhitePalace.option_exclude:
            exclusions.add("King_Fragment")
            # these aren't item groups anymore
            # exclusions.update(item_name_groups["PalaceJournal"])
            # exclusions.update(item_name_groups["PalaceLore"])
            # exclusions.update(item_name_groups["PalaceTotem"])
        return exclusions

    @staticmethod
    def edit_effects(state, player: int, item_effects: dict[str, int], add: bool):
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
                ret = lookup["at_threshold"]
            elif count < lookup["threshold"]:
                ret = lookup["below_threshold"]
            else:
                ret = lookup["above_threshold"]
            return {lookup["term"]: 1, **ret}

        else:
            raise Exception(f"unknown type {lookup['type']}")

        if "type" in ret:
            return self.handle_effect(item_name, ret, state, player)
        else:  # noqa: RET505
            raise Exception(f"unknown effect {ret}")

    def collect(self, state, item: HKItem) -> bool:
        if item.advancement:
            player = item.player
            if item.name == "Grub":
                # to make sure grub counting is consistent across Groups etc.
                state.prog_items[player][item.name] += 1

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
            state._hk_stale[item.player] = True
        return item.advancement

    def remove(self, state, item: HKItem) -> bool:
        if item.advancement:
            player = item.player
            if item.name == "Grub":
                # to make sure grub counting is consistent across Groups etc.
                state.prog_items[player][item.name] -= 1

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
                entrance.name for entrance in self.get_region("Menu").exits
                }

            state._hk_stale[item.player] = True
        return item.advancement

    # generate_early
    def generate_early(self):
        options = self.options
        weights = {
            data.term: getattr(options, f"CostSanity{data.option}Weight").value
            for data in cost_terms.values()
        }
        if options.CostSanity:
            player_name = self.player_name
            if all(weight == 0 for weight in weights.values()):
                raise OptionError(f"CostSanity was on for {player_name} but no currencies are enabled")
            if all(weight == 0 for name, weight in weights.items() if name != "GEO"):
                raise OptionError(
                    f"CostSanityHybridChance was on for {player_name}"
                    "but no non-geo currencies are enabled for non-geo shops"
                )
            # hybrid_chance = options.CostSanityHybridChance.value
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
        self.soul_modes[self.player] = NearbySoul.ITEMSOUL  # make dynamic with ER support

        self.split_cloak_direction = self.random.randint(0, 1)

        start_location_key = self.options.StartLocation.current_key
        start_validation = self.validate_start(start_location_key)
        if start_validation:
            raise OptionError(f"Start Location {start_location_key} was invalid with other Options. "
                              f"Requirements not met are:\n{start_validation}")
            # TODO consider warning and resetting to KP
        self.start_location_region = transition_to_region_map[starts[start_location_key]["granted_transition"]]
        # actually connect it later once we have regions created

        # defaulting so completion condition isn't incorrect before pre_fill
        self.grub_count = (
            46 if options.GrubHuntGoal == GrubHuntGoal.special_range_names["all"]
            else options.GrubHuntGoal.value
            )
        self.grub_player_count = {self.player: self.grub_count}

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

    def validate_start(self, start_location_key: str) -> list[list[str]]:
        test_state = CollectionState(self.multiworld)
        valid_items = ["ITEMRANDO", "2MASKS"]  # TODO: properly handle these assumptions (non-er and non-cursed masks)
        if self.options.EnemyPogos:
            valid_items.append("ENEMYPOGOS")
        if test_state.has_group("Vertical", self.player):
            valid_items.append("VERTICAL")
        if self.options.RandomizeSwim:
            valid_items.append("SWIM")
        if self.options.DarkRooms:
            valid_items.append("DARKROOMS")
        if self.options.ShadeSkips:
            valid_items.append("SHADESKIPS")
        if self.options.DangerousSkips:
            valid_items.append("DANGEROUSSKIPS")
        start_location_logic = starts[start_location_key]["logic"]

        if not start_location_logic:  # empty logic means always good
            return []
        for clause in start_location_logic:  # TODO: assuming only item_requirements are relevant
            if all(i in valid_items for i in clause["item_requirements"]):
                return []
        return [clause["item_requirements"] for clause in start_location_logic]

    # create_regions
    def create_regions(self):
        super().create_regions()  # Call RandomizerCoreWorld create_regions
        self.add_vanilla_connections()
        self.add_all_events()
        self.add_shop_locations()

        if "King_Fragment" in self.white_palace_exclusions():
            self.get_location("King_Fragment").progress_type = LocationProgressType.EXCLUDED

        location_to_option = {
            location: option for option, data in pool_options.items() for location in data["randomized"]["locations"]
        }
        location_to_option["Elevator_Pass"] = "RandomizeElevatorPass"
        for location, costs in vanilla_location_costs.items():
            if self.options.AddUnshuffledLocations or getattr(self.options, location_to_option[location]):
                self.get_location(location).costs = costs
        self.get_region("Menu").connect(self.get_region(self.start_location_region))

    def get_location_map(self) -> list[tuple[str, str, Any | None]]:
        # # Vanilla placements of the following items have no impact on logic, thus we can avoid creating these items
        # # and locations entirely when the option to randomize them is disabled.
        # logicless_options = {
        #     "RandomizeVesselFragments", "RandomizeGeoChests", "RandomizeJunkPitChests", "RandomizeRelics",
        #     "RandomizeMaps", "RandomizeJournalEntries", "RandomizeGeoRocks", "RandomizeBossGeo",
        #     "RandomizeLoreTablets", "RandomizeSoulTotems", "RandomizeLifebloodCocoons",
        # }

        # make our location_list off of location per option
        # and add any necessary location for logic to event_locations to be create later
        exclusions = self.white_palace_exclusions()
        if "King_Fragment" in exclusions:
            exclusions.remove("King_Fragment")

        location_list = [
            location
            for option, data in pool_options.items()
            for location in data["randomized"]["locations"]
            if location not in self.event_locations and getattr(self.options, option)
            and location not in self.created_multi_locations
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
        location_map = [
            (region["name"], location, self.rule_lookup[location])
            for region in self.rc_regions
            for location in region["locations"]
            if location in location_list
        ]

        # TODO bandaid fix to make sure these don't ever get added to the pool
        assert not [obj for obj in location_map if obj[1] in ("Can_Warp_To_DG_Bench", "Can_Warp_To_Bench")]
        return [obj for obj in location_map if obj[1] not in ("Can_Warp_To_DG_Bench", "Can_Warp_To_Bench")]

    def create_rule(self, rule: Any) -> list[HKClause]:
        # TODO consider caching on these as they should be deterministic,
        # TODO Cont. but they need options so only deterministic per world
        def parse_item_logic(reqs: list) -> tuple[bool, Counter[str]]:  # Mapping[str, int]:
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
                handler = ResourceStateHandler.get_handler(req, self.player)
                if handler.can_exclude(self.options):
                    skip_clause = True
                else:
                    state_requirements.append(handler)

            # checking for a False condition before and after item parsing for short circuiting
            if skip_clause:
                continue
            skip_clause, items = parse_item_logic(item_requirements)
            if skip_clause:
                continue
            for item in items:
                assert (
                    item == "FALSE"
                    or item in affecting_items_by_term
                    or item in affected_terms_by_item
                    or item in self.event_locations
                ), f"{item} not found in advancements"
            hk_rule.append(HKClause(
                hk_item_requirements=dict(items),
                hk_region_requirements=clause["region_requirements"],
                hk_state_requirements=state_requirements,
                ))

        return hk_rule

    def set_rule(self, spot, rule):
        # set hk_rule instead of access_rule because our Location class defines a custom access_rule
        if isinstance(spot, HKEntrance):
            relevant_terms = {term for clause in rule for term in clause.hk_item_requirements.keys()}
            relevant_terms.update(
                {term for clause in rule for s_var in clause.hk_state_requirements for term in s_var.terms}
            )
            for term in relevant_terms:
                # could keep this a static method by doing spot.parent_region.multiworld.worlds[spot.player] but ugh
                self.entrance_by_term[term].append(spot.name)

        spot.set_hk_rule(rule)

    def set_victory(self) -> None:
        multiworld = self.multiworld
        player = self.player
        goal = self.options.Goal
        if goal == Goal.option_hollowknight:
            multiworld.completion_condition[player] = lambda state: state.has("Defeated_Any_Hollow_Knight", player)
        elif goal == Goal.option_siblings:
            multiworld.completion_condition[player] = lambda state: (state.has("Defeated_Any_Hollow_Knight", player)
                                                                     and state.has("WHITEFRAGMENT", player, 3))
        elif goal == Goal.option_radiance:
            multiworld.completion_condition[player] = lambda state: state.has("Defeated_Any_Radiance", player)
        elif goal == Goal.option_godhome:
            multiworld.completion_condition[player] = lambda state: state.has("Defeated_Pantheon_5", player)
        elif goal == Goal.option_godhome_flower:
            multiworld.completion_condition[player] = self.can_godhome_flower
        elif goal == Goal.option_grub_hunt:
            multiworld.completion_condition[player] = lambda state: self.can_grub_goal(state)
        else:
            # Any goal
            multiworld.completion_condition[player] = (
                lambda state: state.has("Defeated_Any_Hollow_Knight", player) and state.has("WHITEFRAGMENT", player, 3)
                and state.has("Defeated_Any_Radiance", player)
                and self.can_godhome_flower(state)
                and self.can_grub_goal(state)
            )

    def can_godhome_flower(self, state: CollectionState):
        if not state.has_all_counts({"Godtuner": 1, "Defeated_Pantheon_5": 1}, self.player):
            return False

        if not state.can_reach_region("GG_Waterways", self.player):
            # cannot deliver flower
            return False
        for state_blob in state._hk_per_player_resource_states[self.player]["GG_Waterways"]:
            if not state_blob["NOFLOWER"]:
                # if any valid state gets us to godseeker with the flower unbroken
                return True
        return False

    def can_grub_goal(self, state: CollectionState) -> bool:
        return all(state.has("Grub", owner, count) for owner, count in self.grub_player_count.items())

    def add_vanilla_connections(self):
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
            region1 = self.get_region(connection[0])
            region2 = self.get_region(connection[1])
            region1.connect(region2, connection[2])

    def add_all_events(self):
        location_to_region = {loc: reg["name"] for reg in regions for loc in reg["locations"]}

        def create_location(item: str, location: str, costs: list[dict]):
            if location in shop_locations:
                loc = self.add_shop_location(location)
            else:
                region = self.get_region(location_to_region[location])
                if not self.options.AddUnshuffledLocations or location in self.event_locations:
                    loc_id = None
                else:
                    loc_id = self.location_name_to_id[location]
                loc = self.location_class(self.player, location, loc_id, region)
                region.locations.append(loc)

                rule = self.rule_lookup.get(location)
                if rule:
                    self.set_rule(loc, self.create_rule(rule))
            assert item
            if item:
                if not self.options.AddUnshuffledLocations or item in self.event_locations:
                    item_id = None
                    loc.address = None
                else:
                    item_id = self.item_name_to_id[item]
                loc.place_locked_item(
                    self.item_class(item, ItemClassification.progression, item_id, self.player)
                )
                loc.show_in_spoiler = False
            return loc

        for option, option_data in pool_options.items():
            if not getattr(self.options, option):
                for pair in option_data["vanilla"]:
                    if pair["location"] == "Start":
                        continue
                    create_location(pair["item"], pair["location"], pair["costs"])
        for event in self.event_locations:
            create_location(event, event, [])

    def add_shop_location(self, shop, index=None):
        if index is None:
            index = len(self.created_multi_locations[shop])
        lookup_shop = shop if "(Requires_Charms)" not in shop else "Salubra"
        # fix because Salubra_(Requires_Charms) isn't actually in the source data

        costs = None
        if shop in shop_cost_types:
            costs = {
                term: self.random.randint(*self.ranges[term])
                for term in shop_cost_types[shop]
            }

        rule = self.rule_lookup[lookup_shop]
        region = self.get_region(self.region_lookup[lookup_shop])
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
        return loc

    def add_shop_locations(self):
        # TODO logicless event items that get culled don't take up shop space
        for shop, shop_locations in self.created_multi_locations.items():
            for index in range(len(shop_locations), getattr(self.options, shop_to_option[shop]).value):
                # start index may be important if we pre-create unshuffled items in shops
                self.add_shop_location(shop, index)
        self.add_extra_shop_locations(self.options.ExtraShopSlots.value)

    def add_extra_shop_locations(self, count):
        # Add additional shop items, as needed.
        if not count > 0:
            return
        shops = [shop for shop, locations in self.created_multi_locations.items() if len(locations) < 16]
        if not self.options.EggShopSlots.value:  # No eggshop, so don't place items there
            shops.remove("Egg_Shop")

        if not shops:
            return
        for _ in range(count):
            shop = self.random.choice(shops)
            index = len(self.created_multi_locations[shop])
            self.add_shop_location(shop, index)
            if len(self.created_multi_locations[shop]) >= 16:
                shops.remove(shop)
                if not shops:
                    break

    # create_items
    def create_items(self):
        pool_count = super().create_items()  # Call RandomizerCoreWorld create_items

        item_difference = pool_count - len(self.multiworld.get_unfilled_locations(self.player))
        if item_difference > 0:
            self.add_extra_shop_locations(item_difference)

        self.handle_starting_inventory()
        self.apply_costsanity()
        self.sort_shops_by_cost()

    def get_item_list(self) -> list[str]:
        junk: set[str] = {"Downslash"}
        if self.options.RemoveSpellUpgrades:
            junk.update(("Abyss_Shriek", "Shade_Soul", "Descending_Dark"))
        exclusions = self.white_palace_exclusions()
        if "King_Fragment" in exclusions:
            exclusions.remove("King_Fragment")
        junk.update(exclusions)

        # build out item_table (including counts) by option, excluding items in junk
        item_table = [
            item
            for option, data in pool_options.items()
            for item in data["randomized"]["items"]
            if getattr(self.options, option) and item not in junk
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

        # Grimmchild 2 added in the pool options but should be handled as 1 in vanilla event placement
        if "Grimmchild2" in item_table and (self.options.RandomizeGrimmkinFlames or not self.options.RandomizeCharms):
            item_table.remove("Grimmchild2")
            item_table.append("Grimmchild1")

        if self.options.RandomizeElevatorPass:
            item_table.append("Elevator_Pass")

        return item_table

    @staticmethod
    def get_item_classification(name: str) -> ItemClassification:
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

        if name in non_progression_items:
            classification = ItemClassification.filler
            assert name not in progression_effect_lookup
        elif name in progression_effect_lookup:
            classification = ItemClassification.progression
        else:
            logger.warning(f"unknown item {name} setting to progression")
            classification = ItemClassification.progression
        if name in affecting_items_by_term["DREAMER"] or \
                name in affecting_items_by_term["GRUBS"] or \
                name in affecting_items_by_term["ESSENCE"] or \
                name in affecting_items_by_term["RANCIDEGGS"]:
            classification |= ItemClassification.skip_balancing
        if name in ("Pale_Ore", "Arcane_Egg", "King's_Idol", "Hallownest_Seal", "Wanderer's_Journal"):
            classification |= ItemClassification.useful
        if (name not in progression_charms and name in affecting_items_by_term["CHARMS"]):
            classification |= ItemClassification.skip_balancing
        if name == "Mimic_Grub" or name == "Quill":
            classification |= ItemClassification.trap

        return classification

    def get_filler_items(self) -> list[str]:
        if self.player not in self.cached_filler_items:
            fillers = ["One_Geo", "Soul_Refill"]
            exclusions = self.white_palace_exclusions()
            for group in (
                    "RandomizeGeoRocks", "RandomizeSoulTotems", "RandomizeLoreTablets", "RandomizeJunkPitChests",
                    "RandomizeRancidEggs"
            ):
                if getattr(self.options, group):
                    fillers.extend(item for item in pool_options[group]["randomized"]["items"] if item not in
                                   exclusions)
            self.cached_filler_items[self.player] = fillers
        return self.cached_filler_items[self.player]

    def get_filler_item_name(self) -> str:
        return self.random.choice(self.get_filler_items())

    def handle_starting_inventory(self):
        def precollect(item, code):
            self.push_precollected(self.item_class(item, ItemClassification.progression, code, self.player))
        precollect("Downslash", self.item_name_to_id["Downslash"])
        for option, items in randomizable_starting_items.items():
            if not getattr(self.options, option):
                for item in items:
                    precollect(item, self.item_name_to_id[item])

    def apply_costsanity(self):
        setting = self.options.CostSanity.value
        if not setting:
            return  # noop

        def _compute_weights(weights: dict, desc: str) -> dict[str, int]:
            if all(x == 0 for x in weights.values()):
                logger.warning(
                    f"All {desc} weights were zero for {self.player_name}."
                    f" Setting them to one instead."
                )
                weights = dict.fromkeys(weights, 1)

            return {k: v for k, v in weights.items() if v}

        random = self.random
        hybrid_chance = self.options.CostSanityHybridChance.value
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
                    f"Only one cost type is available for CostSanity in {self.player_name}'s world."
                    f" CostSanityHybridChance will not trigger in geo shop locations."
                )
            if len(weights_geoless) == 1:
                logger.warning(
                    f"Only one cost type is available for CostSanity in {self.player_name}'s world."
                    f" CostSanityHybridChance will not trigger in geoless locations."
                )

        for region in self.get_regions():
            for location in region.locations:
                if location.vanilla:
                    continue
                if not location.costs:
                    continue
                if location.name == "Vessel_Fragment-Basin":
                    continue
                if setting == CostSanity.option_notshops and location.basename in self.created_multi_locations:
                    continue
                if setting == CostSanity.option_shopsonly and location.basename not in self.created_multi_locations:
                    continue
                if location.basename in {"Grubfather", "Seer", "Egg_Shop"}:
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

    def sort_shops_by_cost(self):
        for shop, shop_locations in self.created_multi_locations.items():
            randomized_locations = [loc for loc in shop_locations if not loc.vanilla]
            if not randomized_locations:
                return
            prices = sorted(
                (loc.costs for loc in randomized_locations),
                key=lambda costs: (len(costs), *costs.values(),)
            )
            for loc, costs in zip(randomized_locations, prices):
                loc.costs = costs

    # pre_fill
    @classmethod
    def stage_pre_fill(cls, multiworld: MultiWorld):
        worlds = [world for world in multiworld.get_game_worlds(cls.game) if world.options.Goal in ["any", "grub_hunt"]]
        if worlds:
            grubs = [item for item in multiworld.get_items() if item.name == "Grub"]
        all_grub_players = [
            world.player
            for world in worlds
            if world.options.GrubHuntGoal == GrubHuntGoal.special_range_names["all"]
            ]

        if all_grub_players:
            group_lookup = defaultdict(set)
            for group_id, group in multiworld.groups.items():
                for player in group["players"]:
                    group_lookup[group_id].add(player)

            grub_count_per_player = Counter()
            per_player_grubs_per_player = defaultdict(Counter)

            for grub in grubs:
                player = grub.player
                if player in group_lookup:
                    for real_player in group_lookup[player]:
                        per_player_grubs_per_player[real_player][player] += 1
                else:
                    per_player_grubs_per_player[player][player] += 1

                if grub.location and grub.location.player in group_lookup.keys():
                    # will count the item linked grub instead
                    pass
                elif player in group_lookup:
                    for real_player in group_lookup[player]:
                        grub_count_per_player[real_player] += 1
                else:
                    # for non-linked grubs
                    grub_count_per_player[player] += 1

            for player, count in grub_count_per_player.items():
                multiworld.worlds[player].grub_count = count

            for player, grub_player_count in per_player_grubs_per_player.items():
                if player in all_grub_players:
                    multiworld.worlds[player].grub_player_count = grub_player_count

        for world in worlds:
            if world.player not in all_grub_players:
                world.grub_count = world.options.GrubHuntGoal.value
                player = world.player
                world.grub_player_count = {player: world.grub_count}

    # fill_slot_data
    def fill_slot_data(self):
        slot_data = {}

        options = slot_data["options"] = {}
        for option_name in hollow_knight_options:
            option = getattr(self.options, option_name)
            try:
                # exclude more complex types - we only care about int, bool, enum for player options; the client
                # can get them back to the necessary type.
                optionvalue = int(option.value)
                options[option_name] = optionvalue
            except TypeError:
                pass

        slot_data["options"]["StartLocationName"] = starts[self.options.StartLocation.current_key]["logic_name"]

        # 32 bit int
        slot_data["seed"] = self.random.randint(-2147483647, 2147483646)

        # HKAP 0.1.0 and later cost data.
        location_costs = {}
        for region in self.get_regions():
            for location in region.locations:
                if location.costs:
                    location_costs[location.name] = location.costs
        slot_data["location_costs"] = location_costs
        # TODO apply geo caps here and spoiler

        slot_data["notch_costs"] = self.charm_costs

        slot_data["grub_count"] = self.grub_count

        slot_data["is_race"] = self.settings.disable_spoilers or self.multiworld.is_race

        return slot_data

    # write_spoiler
    @classmethod
    def stage_write_spoiler(cls, multiworld: MultiWorld, spoiler_handle):
        hk_worlds = multiworld.get_game_worlds(cls.game)
        spoiler_handle.write("\n\nCharm Notches:")
        for hk_world in hk_worlds:
            player = hk_world.player
            name = multiworld.get_player_name(player)
            spoiler_handle.write(f"\n{name}\n")
            for charm_number, cost in enumerate(hk_world.charm_costs):
                spoiler_handle.write(f"\n{charm_names[charm_number]}: {cost}")

        spoiler_handle.write("\n\nShop Prices:")
        for hk_world in hk_worlds:
            player = hk_world.player
            name = hk_world.player_name
            spoiler_handle.write(f"\n{name}\n")

            if hk_world.options.CostSanity.value:
                for loc in sorted(
                    (
                        loc for loc in itertools.chain(*(region.locations for region in hk_world.get_regions()))
                        if loc.costs
                    ), key=operator.attrgetter("name")
                ):
                    spoiler_handle.write(f"\n{loc}: {loc.item} costing {loc.cost_text()}")
            else:
                for shop_name, locations in hk_world.created_multi_locations.items():
                    for loc in locations:
                        spoiler_handle.write(f"\n{loc}: {loc.item} costing {loc.cost_text()}")
