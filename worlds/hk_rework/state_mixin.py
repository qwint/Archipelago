from BaseClasses import MultiWorld, CollectionState
from typing import TYPE_CHECKING, Tuple, Dict, Set, Any
from worlds.AutoWorld import LogicMixin


if TYPE_CHECKING:
    from . import HKWorld, HKClause


class HKLogicMixin(LogicMixin):
    multiworld: MultiWorld
    _hk_per_player_resource_states: Dict[int, Dict[str, Any]]
    """resource state blob to map regions and their avalible resource states"""

    _hk_per_player_sweepable_entrances: Dict[int, Set[str]]
    """mapping for entrances that need to be statefully swept"""

    _hk_free_entrances: Dict[int, Set[str]]
    """mapping for entrances that will not alter resource state no matter how many more items we get, for optimization"""

    _hk_entrance_clause_cache: Dict[int, Dict[str, Dict[int, bool]]]
    """mapping for clauses per entrance per player to short circuit non-resource state calculations"""

    def init_mixin(self, multiworld) -> None:
        from . import HKWorld as cls
        players = multiworld.get_game_players(cls.game)
        self._hk_per_player_resource_states = {player: {"Menu": True} for player in players}  # {player: {init_state: [start_region]} for player in players}
        self._hk_per_player_sweepable_entrances = {player: set() for player in players}
        self._hk_free_entrances = {player: set() for player in players}
        self._hk_entrance_clause_cache = {player: {} for player in players}

    def copy_mixin(self, other) -> CollectionState:
        other._hk_per_player_resource_states = self._hk_per_player_resource_states
        other._hk_free_entrances = self._hk_free_entrances
        return other
        # TODO do we need to copy sweepables? should be empty any time we're mucking with resource state

    def _hk_state_valid_for_region(self, state_requirement, region) -> bool:
        parent_resource_state = self._hk_per_player_resource_states[region.player].get(region.name, None)

        # if the parent region isn't in the cache just add it as False
        if parent_resource_state is None:
            self._hk_per_player_resource_states[region.player][region.name] = False
            parent_resource_state = False
        if not parent_resource_state:
            # print(parent_resource_state)
            return False
        # for state_diff in state_requirement:
            # print(f"checking region {region.name} for state requirement {state_diff}")
        return True

    def _hk_apply_diff_to_region(self, entrance, state_modifiers) -> bool:
        player = entrance.player
        parent_region = entrance.parent_region
        target_region = entrance.connected_region
        # diff = clause.hk_state_modifiers

        # assume true for now
        self._hk_per_player_resource_states[player][target_region.name] = True
        improved = True
        return improved

    # last iteration
    def _hk_resource_state_eval_method(self, entrance):  # -> Tuple[accessible, deltas]:
        player = entrance.player
        if entrance in self._hk_free_entrances[player]:
            return True, {}
        accessible, deltas, is_free = entrance.access_rule(self)
        if not accessible:
            return False, {}
        else:
            if target_region not in self._hk_per_player_resource_states[player]:
                self._hk_per_player_resource_states[player][region] = {}
                # not needed?
            if is_free:
                self._hk_free_entrances[player] += {entrance}
            target_improved = self._hk_apply_diff_to_region(self, deltas, entrance)
            if target_improved:
                exits = {exit in entrance.target_region.exits}
                self._hk_per_player_sweepable_entrances[player] += exits
        self._hk_stateful_sweep(self, player)

    # def _hk_apply_diff_to_region(self, diff, entrance) -> bool:
    #     player = entrance.player
    #     parent_region = entrance.parent_region
    #     target_region = entrance.target_region
    #     old_resource_states = self._hk_per_player_resource_states[player][parent_region]
    #     new_resource_states = old_resource_states + diff
    #     improved = any(new > old for new in new_resource_states for old in old_resource_states)
    #     self._hk_per_player_resource_states[player][parent_region] += new_resource_states
    #     simplify(self._hk_per_player_resource_states[player][parent_region])
    #     return improved

    def _hk_full_stateful_sweep(self, player) -> None:
        sweepables = {exit for region in self.region_cache[player] for exit in region.exits if exit not in self._hk_free_entrances}
        self._hk_per_player_sweepable_entrances[player] += sweepables
        self._hk_stateful_sweep(self, player)

    def _hk_stateful_sweep(self, player) -> None:
        while self._hk_per_player_sweepable_entrances[player]:
            entrance = self._hk_per_player_sweepable_entrances[player].pop()
            self._hk_resource_state_eval_method(entrance)
        # does this loop inefficiently? i feel like it would short circuit at some point but not certain


def simplify(state_blob, region) -> None:
    # write/move this
    pass

# TODO define entrance.access_rule() that returns `accessible, deltas, is_free`


# not exactly that and would need reworks, but i think healthier
def access_rule(self, state) -> bool:
    # pseudocode
    access = zip([all(req for req in clause.reqs) for clause in self.rule.clauses], self.rule.deltas)
    applied = state.apply_deltas_to_region(self.parent_region, access)
    return any(applied)

# in this AU, apply_deltas_to_region returns a list of if_applied bools
# and internally checks if it improved the region, and applies the sweepable status to relevant entrances
# then mixin would have to interrupt and apply the stateful sweep

# also would need to add per entrance per clause caching that would reset on remove/new state
# that enables shortcircuiting when item state already returned True for a given clause

# assumes clauses that will never return True are removed for optimization (but isn't required)
