from BaseClasses import MultiWorld, CollectionState, Region
from typing import TYPE_CHECKING, Tuple, NamedTuple, Dict, Set, Any, List
from worlds.AutoWorld import LogicMixin
from .Charms import names as charm_names
from collections import Counter
from copy import deepcopy

if TYPE_CHECKING:
    from . import HKWorld, HKClause

default_state = ([], Counter({"DAMAGE": 0, "SPENTSOUL": 0, "NOFLOWER": 0, "SPENTNOTCHES": 0}))
FULL_SOUL = 12
BASE_NOTCHES = 3
BASE_HEALTH = 4
charm_name_to_id = {"_".join(name.split(" ")): index for index, name in enumerate(charm_names)}  # if name in ("Spell_Twister", "Fragile_Heart")}
                    # TODO >:(


class HKLogicMixin(LogicMixin):
    multiworld: MultiWorld
    _hk_per_player_resource_states: Dict[int, Dict[str, List[Tuple[List[str], Counter]]]]
    """resource state blob to map regions and their avalible resource states"""
    # state blob is [([equippedcharm1, equippedcharm2], Counter({"DAMAGE": 0, "SPENTSOUL": 0, "NOFLOWER": 0, "CHARMNOTCHESSPENT": 0}))]

    _hk_per_player_sweepable_entrances: Dict[int, Set[str]]
    """mapping for entrances that need to be statefully swept"""

    _hk_free_entrances: Dict[int, Set[str]]
    """mapping for entrances that will not alter resource state no matter how many more items we get, for optimization"""

    _hk_entrance_clause_cache: Dict[int, Dict[str, Dict[int, bool]]]
    """mapping for clauses per entrance per player to short circuit non-resource state calculations"""

    def init_mixin(self, multiworld) -> None:
        from . import HKWorld as cls
        players = multiworld.get_game_players(cls.game)
        self._hk_per_player_resource_states = {player: {"Menu": [default_state]} for player in players}  # {player: {init_state: [start_region]} for player in players}
        self._hk_per_player_sweepable_entrances = {player: set() for player in players}
        self._hk_free_entrances = {player: set() for player in players}
        self._hk_entrance_clause_cache = {player: {} for player in players}

    def copy_mixin(self, other) -> CollectionState:
        other._hk_per_player_resource_states = self._hk_per_player_resource_states
        other._hk_free_entrances = self._hk_free_entrances
        return other
        # TODO do we need to copy sweepables? should be empty any time we're mucking with resource state

    def _hk_check_healths(self, player, state_requirement, parent_state, joni=False, heart=False) -> bool:
        """Checks for player health for calculating damage boosts and shade skips"""
        total_health = BASE_HEALTH + self.count("Mask_Shard", player) + 2 if heart else 0

        if state_requirement.shadeskip > 0:
            shade_health = 1 if joni else max(floor(total_health/2), 1)
            if not shade_health >= state_requirement.shadeskip:
                return False

        if state_requirement.damage > 0:
            total_damage = parent_state["DAMAGE"] + state_requirement.damage

            if not total_health > total_damage:
                return False
        return True

    def _hk_check_state_valid(self, player, state_requirement, parent_charms, parent_state) -> Tuple[bool, List[str]]:
        """Intented to quickly check with a given set of charms can we suffice the requirements"""
        twister = "Spell_Twister" in parent_charms
        joni = "Joni's_Blessing" in parent_charms
        heart = "Fragile_Heart" in parent_charms

        # use these for later to know what we need to improve to make the state valid
        need_soul = False
        need_health = False

        # TODO cleanup
        # print(state_requirement)
        # from . import HK_state_diff
        # TEST_fake_state = HK_state_diff(shadeskip=0, damage=0, twister_required=False, total_casts=0, before=False, after=False)
        # state_requirement = TEST_fake_state

        # doing early for short circuiting
        if state_requirement.shadeskip > 0 and parent_state["SHADESPENT"] > 0:
            return False, []
        # twister_required if an individual step requires more than default cast count
        if state_requirement.twister_required and not twister:
            return False, []

        # check to see if we have the required shade/player health for the state changes
        if not self._hk_check_healths(player, state_requirement, parent_state, joni=joni, heart=heart):
            need_health = True

        # already checked if twister is required so we can assume each step is doable
        # only need to calculate full spend
        if state_requirement.total_casts > 0:
            cast_multi = 3 if twister else 4
            soul_spend = state_requirement.total_casts * cast_multi

            # every 3 vessles we get 1/3 of full soul
            bonus_soul = FULL_SOUL * (self.count("Soul_Vessle", player) / 9)
            total_soul = FULL_SOUL + bonus_soul
            if not total_soul >= soul_spend + parent_state["SPENTSOUL"]:
                need_soul = True

        # if we didn't need to improve anything this is a valid state
        if not need_soul and not need_health:
            return True, []

        # calculate how many notches we can fill with charms to fix issues
        avaliable_notches = BASE_NOTCHES + self.count("Charm_Notch", player) - parent_state["SPENTNOTCHES"]
        if not avaliable_notches:
            return False, []

        # find which charms we need to fix issues, short circuit if we already have them
        potential_charms = []
        if need_soul:
            if twister:
                # we already have it equipped, short circuit; should stop recursion depth > 1
                return False, []
            if self.has("Spell_Twister", player):
                potential_charms.append("Spell_Twister")
        if need_health:
            if heart:
                # we already have it equipped, short circuit; should stop recursion depth > 1
                return False, []
            # make sure if we only have fragile heart that we can fix it
            heart_counts = self.count_from_list(["Fragile_Heart", "Unbreakable_Heart"], player)
            if heart_counts > 1 or (heart_counts > 0 and self.has("Can_Repair_Fragile_Charms", player)):
                potential_charms.append("Fragile_Heart")

        # find the costs for the charms we need and apply them to a new state to re-call self
        # short circuting if they cannot all be equipped
        potential_costs = [
            self.multiworld.worlds[player].charm_costs[charm_name_to_id[charm]]
            for charm in potential_charms
            ]
        if not potential_charms or not avaliable_notches >= sum(potential_costs):
            return False, []
        else:
            new_state = deepcopy(parent_state)  # .copy()
            new_charms = deepcopy(parent_charms)  # .copy()
            for charm, cost in ((charm, cost) for charm, cost in zip(potential_charms, potential_costs)):
                new_state["SPENTNOTCHES"] += cost
                new_charms.append(charm)
            improved_check = self._hk_check_state_valid(
                player,
                state_requirement,
                new_charms,
                new_state,
                )

            if improved_check:
                return True, new_charms
            else:
                return False, []

    def _hk_add_charms_to_state(self, player, resource_state, charms) -> Tuple[List[str], Counter]:
        """Returns a new state blob including the listed charms and their costs"""
        new_resource_state = deepcopy(resource_state)
        new_resource_state[0] += charms
        for charm in charms:
            new_resource_state[1]["SPENTNOTCHES"] += self.multiworld.worlds[player].charm_costs[charm_name_to_id[charm]]
        return new_resource_state

    def _hk_any_state_valid_for_region(self, state_requirement, region) -> bool:
        """Minimal check that any resource state for a parent region can be used to access a Location by state requirement"""
        player = region.player
        parent_resource_state = self._hk_per_player_resource_states[player].get(region.name, [])

        for resource_state in parent_resource_state:
            accessible, _ = self._hk_check_state_valid(player, state_requirement, resource_state[0], resource_state[1])
            if accessible:
                # we can short circuit on any accessible
                return True

        # if we got this far without returning True then we ran out of options
        return False

    def _hk_apply_state_to_region(self, entrance, state_requirement) -> bool:
        """
        Full logic to find all minimum viable states to access an entrance,
        Find any possible better states,
        Apply to the target region,
        See if they improve the target region,
        if so mark all exits as sweepable
        """

        # parent_resource_state = self._hk_per_player_resource_states[region.player].get(region.name, None)

        # # if the parent region isn't in the cache just add it as an empty list
        # if parent_resource_state is None:
        #     self._hk_per_player_resource_states[region.player][region.name] = []
        #     parent_resource_state = []
        player = entrance.player
        parent_region = entrance.parent_region
        target_region = entrance.connected_region

        parent_resource_state = self._hk_per_player_resource_states[player].get(parent_region.name, [])
        target_resource_states = []

        # TODO short circuit if there is no state changes
        if not state_requirement:
            self._hk_per_player_resource_states[player][target_region.name] = [default_state]
            return True

        if len(parent_resource_state) > 0:
            # if we don't even have default state then the region is inaccessible
            return False
        for resource_state in parent_resource_state:
            accessible, new_charms = self._hk_check_state_valid(player, state_requirement, resource_state[0], resource_state[1])
            if accessible:
                if new_charms:
                    target_resource_states.append(self._hk_add_charms_to_state(player, resource_state, new_charms))
                else:
                    target_resource_states.append(resource_state)
                    # TODO check if we need to forward 'better' states with charms equipped anyways

        if len(target_resource_states) == 0:
            # if we have a target and no valid states we ran out of options
            return False
        else:
            # apply the valid states and return True
            self._hk_per_player_resource_states[player][target_region.name] += target_resource_states
            # TODO if improved mark all its exits sweepable
            return True



## old code
# ["Spell_Twister"] if need_soul else ["Fragile_Heart", "Lifeblood_Heart", "Lifeblood_Core"]


                # current_spent = 0 if state_requirement.before_soul else parent_state["SPENTSOUL"]
                # cast_multi = 3 if twister else 4


                # if state_requirement.vessle_unneeded \
                #         and FULL_SOUL >= current_spent + (state_requirement.soul_requirement * cast_multi):
                #     pass
                #     # short circuit
                # elif 










            # for delta in state_modifiers:
            #     elif delta.startswith("$CASTSPELL"):  # or $SHRIEKPOGO or $SLOPEBALL
            #         soul_mod = 2 if twister else 3
            #         if "[" in delta:
            #             values = "1,before,after"  # TODO
            #             split_strings = values.split(",")
            #             spent_soul = 0 if "before" in split_strings else parent_state.SPENTSOUL

            #         # check for []
            #         # split insides on ,
            #         # already have removed before/afters that are not relevant (leave x,before,after)
            #         if "before" in split_strings:
            #             temp_state.SPENTSOUL = 0
            #         for x in [x for x in split_strings if x not in ("before", "after")]:
            #             temp_state.SPENTSOUL += x * soul_mod
            #         if "after" in split_strings:
            #             temp_state.SPENTSOUL = 0
            #     elif delta.startswith("$SHADESKIP"):
            #         if parent_state.SHADESPENT:
            #             return False
            #         if "[" in delta:
            #             value = 1  # TODO
            #             health = DEFAULT_HEALTH + (4 * mask_shards)
            #             shade_health = 1 if joni else max(floor(health/2), 1)
            #             if not shade_health >= value:
            #                 return False
            #     elif delta.startswith("$TAKEDAMAGE"):
            #         health = DEFAULT_HEALTH + (4 * mask_shards)
            #         if "[" in delta:
            #             damage = 1  # TODO
            #         else:
            #             damage = 1
            #         if not health > damage:
            #             return False
            #     elif delta == "NOFLOWER=FALSE":
            #         if parent_state.NOFLOWER == True:
            #             return False
            # return True


def _hk_apply_diff_to_region(self, entrance, state_modifiers) -> bool:
    player = entrance.player
    parent_region = entrance.parent_region
    target_region = entrance.connected_region
    temp_state = deepcopy(self._hk_per_player_resource_states[player][parent_region.name])  # .copy()
    # diff = clause.hk_state_modifiers

    # TODO fix
    # for delta in state_modifiers:
    #     if delta == "$BENCHRESET":
    #         temp_state.DAMAGE = 0
    #         if self.has("Salubra's_Blessing", player):
    #             temp_state.SPENTSOUL = 0
    #         temp_state.SHADESPENT = 0
    #         temp_state.EQUIPPEDCHARMS = 0
    #     elif delta.startswith("$CASTSPELL"):  # or $SHRIEKPOGO or $SLOPEBALL
    #         # check for []
    #         # split insides on ,
    #         # already have removed before/afters that are not relevant (leave x,before,after)
    #         if "before" in split_strings:
    #             temp_state.SPENTSOUL = 0
    #         for x in [x for x in split_strings if x not in ("before", "after")]:
    #             temp_state.SPENTSOUL += x*3  # alter based on if twister available
    #         if "after" in split_strings:
    #             temp_state.SPENTSOUL = 0
    #     elif delta == "$FLOWERGET":
    #         # ?
    #         pass
    #     elif delta == "$HOTSPRINGRESET":
    #         temp_state.DAMAGE = 0
    #         temp_state.SPENTSOUL = 0
    #     elif delta.startswith("$SHADESKIP"):
    #         # assume is valid was already called
    #         temp_state.SHADESPENT = True
    #     elif delta == "$STAGSTATEMODIFIER":
    #         temp_state.NOFLOWER = True
    #     elif delta.startswith("$WARPTOSTART"):
    #         temp_state.SPENTSOUL = 0
    #         temp_state.DAMAGE = 0
    #         temp_state.NOFLOWER = True
    #     elif delta.startswith("$TAKEDAMAGE"):
    #         if "[" in delta:
    #             damage = 1  # TODO
    #             temp_state.DAMAGE + damage
    #         else:
    #             temp_state.DAMAGE + 1
    #     elif delta == "NOFLOWER=FALSE":
    #         # assume validity was already checked
    #         pass
    #     else:
    #         raise f"unknown state {delta}"


    # assume true for now
    self._hk_per_player_resource_states[player][target_region.name] = [default_state]
    improved = True
    return improved

    # last iteration
    # def _hk_resource_state_eval_method(self, entrance):  # -> Tuple[accessible, deltas]:
    #     player = entrance.player
    #     if entrance in self._hk_free_entrances[player]:
    #         return True, {}
    #     accessible, deltas, is_free = entrance.access_rule(self)
    #     if not accessible:
    #         return False, {}
    #     else:
    #         if target_region not in self._hk_per_player_resource_states[player]:
    #             self._hk_per_player_resource_states[player][region] = {}
    #             # not needed?
    #         if is_free:
    #             self._hk_free_entrances[player] += {entrance}
    #         target_improved = self._hk_apply_diff_to_region(self, deltas, entrance)
    #         if target_improved:
    #             exits = {exit in entrance.target_region.exits}
    #             self._hk_per_player_sweepable_entrances[player] += exits
    #     self._hk_stateful_sweep(self, player)

    # # def _hk_apply_diff_to_region(self, diff, entrance) -> bool:
    # #     player = entrance.player
    # #     parent_region = entrance.parent_region
    # #     target_region = entrance.target_region
    # #     old_resource_states = self._hk_per_player_resource_states[player][parent_region]
    # #     new_resource_states = old_resource_states + diff
    # #     improved = any(new > old for new in new_resource_states for old in old_resource_states)
    # #     self._hk_per_player_resource_states[player][parent_region] += new_resource_states
    # #     simplify(self._hk_per_player_resource_states[player][parent_region])
    # #     return improved

    # def _hk_full_stateful_sweep(self, player) -> None:
    #     sweepables = {exit for region in self.region_cache[player] for exit in region.exits if exit not in self._hk_free_entrances}
    #     self._hk_per_player_sweepable_entrances[player] += sweepables
    #     self._hk_stateful_sweep(self, player)

    # def _hk_stateful_sweep(self, player) -> None:
    #     while self._hk_per_player_sweepable_entrances[player]:
    #         entrance = self._hk_per_player_sweepable_entrances[player].pop()
    #         self._hk_resource_state_eval_method(entrance)
        # does this loop inefficiently? i feel like it would short circuit at some point but not certain


# def simplify(state_blob, region) -> None:
#     # write/move this
#     pass

# TODO define entrance.access_rule() that returns `accessible, deltas, is_free`


# not exactly that and would need reworks, but i think healthier
# def access_rule(self, state) -> bool:
#     # pseudocode
#     access = zip([all(req for req in clause.reqs) for clause in self.rule.clauses], self.rule.deltas)
#     applied = state.apply_deltas_to_region(self.parent_region, access)
#     return any(applied)

# in this AU, apply_deltas_to_region returns a list of if_applied bools
# and internally checks if it improved the region, and applies the sweepable status to relevant entrances
# then mixin would have to interrupt and apply the stateful sweep

# also would need to add per entrance per clause caching that would reset on remove/new state
# that enables shortcircuiting when item state already returned True for a given clause

# assumes clauses that will never return True are removed for optimization (but isn't required)
