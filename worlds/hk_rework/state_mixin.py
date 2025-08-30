from collections import Counter
from typing import TYPE_CHECKING

from BaseClasses import CollectionState, MultiWorld, Region
from Utils import KeyedDefaultDict
from worlds.AutoWorld import LogicMixin

from .constants import BASE_HEALTH, BASE_NOTCHES, BASE_SOUL  # noqa: F401

if TYPE_CHECKING:
    from . import HKClause
    from .resource_state_vars.cast_spell import NearbySoul


# default_state = KeyedDefaultDict(lambda key: True if key == "NOFLOWER" else False)
class DefaultStateFactory:
    def __call__(self, defaults=None) -> Counter:
        if defaults is None:
            defaults = {}
        ret = Counter({"NOFLOWER": 1, "NOPASSEDCHARMEQUIP": 1})
        for key, value in defaults.items():
            ret[key] = value
        return ret


default_state = DefaultStateFactory()


class HKLogicMixin(LogicMixin):
    multiworld: MultiWorld
    _hk_per_player_resource_states: dict[int, dict[str, list[Counter]]]
    """resource state blob to map regions and their avalible resource states"""
    # state blob is [Counter({"DAMAGE": 0, "SPENTSOUL": 0, "NOFLOWER": 0, "CHARMNOTCHESSPENT": 0})]

    _hk_per_player_sweepable_entrances: dict[int, set[str]]
    """mapping for entrances that need to be statefully swept"""

    _hk_stale: dict[int, bool]
    """TODO: make an item stale and a resource_state_stale difference"""

    _hk_free_entrances: dict[int, set[str]]
    """mapping for entrances that will not alter resource state no matter how many more items we get"""

    _hk_entrance_clause_cache: dict[int, dict[str, dict[int, bool]]]
    """mapping for clauses per entrance per player to short circuit non-resource state calculations"""

    _hk_processed_item_cache: dict[int, Counter]

    hk_charm_costs: dict[int, dict[str, int]]
    """mapping for charm costs per player"""

    _hk_soul_modes: "dict[int, NearbySoul]"
    """mapping of soul mode per player"""

    def init_mixin(self, multiworld: MultiWorld) -> None:
        from . import HKWorld
        players = multiworld.get_game_players(HKWorld.game)
        if not players:
            return
        self._hk_per_player_resource_states = {
            player: KeyedDefaultDict(lambda region: [default_state()] if region == "Menu" else [])
            for player in players
            }  # {player: {init_state: [start_region]} for player in players}
        self._hk_per_player_sweepable_entrances = {player: set() for player in players}
        self._hk_free_entrances = {player: {"Menu"} for player in players}
        self._hk_entrance_clause_cache = {player: {} for player in players}
        self._hk_stale = dict.fromkeys(players, True)
        self._hk_sweeping = dict.fromkeys(players, False)
        self._hk_processed_item_cache = {player: Counter() for player in players}
        self.hk_charm_costs = HKWorld.charm_names_and_costs
        from .resource_state_vars.cast_spell import NearbySoul
        self._hk_soul_modes = {player: NearbySoul.ITEMSOUL for player in players}  # this will be a dict on the world like charm costs at sometime
        for player in players:
            self.prog_items[player]["MASKSHARDS"] = BASE_HEALTH*4
            self.prog_items[player]["NOTCHES"] = BASE_NOTCHES
        # for player in players:
        #     self.prog_items[player]["TOTAL_SOUL"] = BASE_SOUL
        #     self.prog_items[player]["TOTAL_HEALTH"] = BASE_HEALTH
        #     self.prog_items[player]["SHADE_HEALTH"] = max(int(BASE_HEALTH/2), 1)
        #     self.prog_items[player]["TOTAL_NOTCHES"] = BASE_NOTCHES

    def copy_mixin(self, other) -> CollectionState:
        from . import HKWorld
        players = self.multiworld.get_game_players(HKWorld.game)
        if not players:
            return other
        other._hk_per_player_resource_states = {
            player: self._hk_per_player_resource_states[player].copy()
            for player in players
        }
        other._hk_free_entrances = {player: self._hk_free_entrances[player].copy() for player in players}
        other._hk_processed_item_cache = {player: self._hk_processed_item_cache[player].copy() for player in players}
        # intentionally setting by reference since it doesn't change after being set
        other.hk_charm_costs = {player: self.hk_charm_costs[player] for player in players}
        return other
        # TODO do we need to copy sweepables? should be empty any time we're mucking with resource state

    def _hk_apply_and_validate_state(self, clause: "HKClause", region: Region, target_region=None) -> bool:
        player = region.player
        # avaliable_states = self._hk_per_player_resource_states[player].get(region.name, None)

        # if avaliable_states is None:
        #     region.can_reach(self)
        #     avaliable_states = self._hk_per_player_resource_states[player].get(region.name, [])

        # unneeded?
        avaliable_states = [s.copy() for s in self._hk_per_player_resource_states[player][region.name]]
        # loses the can_reach parent call, potentially re-add it?

        if not avaliable_states:
            # no valid parent states
            return False

        for handler in clause.hk_state_requirements:
            avaliable_states = [
                s
                for input_state in avaliable_states
                for s in handler.modify_state(input_state, self)
            ]

        if not avaliable_states:
            return False
        if not target_region:
            # don't persist
            return True
        target_states = self._hk_per_player_resource_states[player][target_region.name]
        for index, s in reversed(list(enumerate(avaliable_states))):
            for previous in target_states:
                if eq(s, previous) or lt(previous, s):
                    # if the state we're adding already exists
                    # or a better state already exists, we didn't improve
                    avaliable_states.pop(index)
                    break
        if avaliable_states:
            # for exit in target_region.exits:
            #     if exit.hk_rule is None:
            #         self._hk_per_player_sweepable_entrances[player].add(exit.name)
            #         continue
            #     relevant_terms = sorted({
            #         term
            #         for clause in exit.hk_rule
            #         for handler in clause.hk_state_requirements
            #         for term in handler.terms
            #     })
            #     for term in relevant_terms:
            #         prev = max(0, 0, *[s[term] for s in target_states])
            #         new = max(0, 0, *[s[term] for s in avaliable_states])
            #         if prev > new:
            #             self._hk_per_player_sweepable_entrances[player].add(exit.name)
            #             break

            target_states += avaliable_states

            for index, s in reversed(list(enumerate(target_states))):
                for other in [t_s for t_s in target_states if t_s is not s]:
                    # TODO make sure this doesn't ever break
                    if lt(other, s):
                        target_states.pop(index)
                        break

            self._hk_per_player_sweepable_entrances[player].update({exit.name for exit in target_region.exits})
            # self._hk_stale[player] = True
        assert target_states
        return True

    def _hk_sweep(self, player: int):
        if self._hk_sweeping[player]:
            return
        self._hk_sweeping[player] = True
        # assume not stale and only evaluate true clauses
        # (region can_reach dependencies will be covered by indirect connections)
        while self._hk_per_player_sweepable_entrances[player]:
            # print(self._hk_per_player_sweepable_entrances[player])
            # random pop but i don't really care
            entrance_name = self._hk_per_player_sweepable_entrances[player].pop()
            entrance = self.multiworld.get_entrance(entrance_name, player)
            if entrance.parent_region in self.reachable_regions[player]:
                # let normal sweep find new regions
                entrance.can_reach(self)
            # if entrance_name not in self._hk_entrance_clause_cache[player]:
            #     entrance.can_reach(self)
            #     # then we haven't done a single can_reach on it, let normal sweep handle that
            #     continue
            # cur_entrance_cache = self._hk_entrance_clause_cache[player][entrance_name]
            # for index in [index for index, status in cur_entrance_cache.items() if status]:
            #     self._hk_apply_and_validate_state(
            #         entrance.hk_rule[index],
            #         entrance.parent_region,
            #         target_region=entrance.connected_region
            #     )
        self._hk_stale[player] = False
        self._hk_sweeping[player] = False


def ge(state1: dict, state2: dict) -> bool:
    return state1.keys() >= state2.keys() and all(v2 <= state1[key] for key, v2 in state2.items())


# from mysteryem
def em_lt(state1: dict, state2: dict) -> bool:
    """Counter-like strict subset comparison"""
    if not state1.keys() <= state2.keys():
        # state1 is not a subset of state2, so state1 has some keys not present in state2
        return False
    if len(state2) > len(state1):
        # state2 has some extra keys, so even if every key in state1 has the same value as in state2, state1 is
        # still a strict subset of state2.
        for key, v1 in state1.items():
            if v1 > state2[key]:
                return False
        return True
    else:  # noqa: RET505
        # state2 has the same keys as state1, so at least one key in state1 must have a lower value than in state2
        less_than = False
        for key, v1 in state1.items():
            v2 = state2[key]
            if v1 > v2:
                # state1 has a larger value than state2 for this key, so state1 is not a subset of state2
                return False
            # todo: How to best optimise this?
            if v1 < v2:
                # state1's value is less than state2's, so state1 could be a strict subset of state2
                less_than = True
        return less_than


def eq(x: dict, y: dict) -> bool:
    keys = x.keys() | y.keys()
    for key in keys:
        if not x[key] == y[key]:
            return False
    return True


def lt(state1: dict, state2: dict) -> bool:
    # TODO rename to le and/or revert this
    for key, v1 in state1.items():
        if not v1 <= state2.get(key, 0):
            return False
    return True

#     if state1 == state2:
#         breakpoint()
#     if state1.keys() - state2.keys():
#         # if any keys exist in state1 that aren't present in state2, state1 cannot be less than
#         return False
#     # if state1["SPENTSOUL"] > state2["SPENTSOUL"]:
#     #     # see if shortcircuting common keys adds speedups
#     #     return False
#     if any(v1 > state2[key] for key, v1 in state1.items()):
#         return False
#     return True
#     return (
#         sum(state1[key] <= state2[key] for key in state1.keys()) == 1
#         and sum(state1[key] < state2[key] for key in state1.keys()) == 1
#     )
#     return not ge(state1, state2)

# negative values won't exist
# best case is falsy
# keys in right that are not in left are inherently lt
# any key in left > right is a failure
# any key in left and not in right is a failure
# don't care about full equality because of codepath
