from collections import Counter
from typing import TYPE_CHECKING

from BaseClasses import CollectionState, MultiWorld, Region
from Utils import KeyedDefaultDict
from worlds.AutoWorld import LogicMixin

from .constants import BASE_HEALTH, BASE_NOTCHES, BASE_SOUL, NearbySoul  # noqa: F401
from .resource_state_vars import rs, rs_set_value, rs_leq

if TYPE_CHECKING:
    from . import HKClause


# default_state = KeyedDefaultDict(lambda key: True if key == "NOFLOWER" else False)
class DefaultStateFactory:
    def __call__(self, defaults=None) -> rs:
        if defaults is None:
            defaults = {}
        ret = 0
        ret = rs_set_value(ret, "NOFLOWER", 1)
        ret = rs_set_value(ret, "NOPASSEDCHARMEQUIP", 1)
        for key, value in defaults.items():
            ret = rs_set_value(ret, key, value)
        return ret


default_state = DefaultStateFactory()


class HKLogicMixin(LogicMixin):
    multiworld: MultiWorld
    _hk_per_player_resource_states: dict[int, dict[str, list[int]]]
    """resource state blob to map regions and their available resource states"""
    # state blob is [Counter({"DAMAGE": 0, "SPENTSOUL": 0, "NOFLOWER": 0, "CHARMNOTCHESSPENT": 0})]

    _hk_per_player_sweepable_entrances: dict[int, set[str]]
    """mapping for entrances that need to be statefully swept"""

    _hk_stale: dict[int, bool]
    """TODO: make an item stale and a resource_state_stale difference"""

    _hk_free_entrances: dict[int, set[str]]
    """mapping for entrances that will not alter resource state no matter how many more items we get"""

    _hk_entrance_clause_cache: dict[int, dict[str, dict[int, bool]]]
    """mapping for clauses per entrance per player to short circuit non-resource state calculations"""

    _hk_checked_state_modifiers: dict[int, dict[str, set[str]]]
    """mapping for state modifiers per entrance per player to not try state modifiers which have already been tried"""

    _hk_processed_item_cache: dict[int, Counter]

    _hk_charm_costs: dict[int, dict[str, int]]
    """mapping for charm costs per player"""

    _hk_soul_modes: dict[int, NearbySoul]
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
        self._hk_checked_state_modifiers = {player: {} for player in players}
        self._hk_stale = dict.fromkeys(players, True)
        self._hk_sweeping = dict.fromkeys(players, False)
        self._hk_processed_item_cache = {player: Counter() for player in players}
        self._hk_charm_costs = HKWorld.charm_names_and_costs
        self._hk_soul_modes = HKWorld.soul_modes
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
            player: KeyedDefaultDict(lambda region: [default_state()] if region == "Menu" else [])
            for player in players
        }
        for player in players:
            for entrance in self._hk_per_player_resource_states[player]:
                other._hk_per_player_resource_states[player][entrance] = self._hk_per_player_resource_states[player][entrance].copy()
        other._hk_entrance_clause_cache = {
            player: {
                entrance: self._hk_entrance_clause_cache[player][entrance].copy()
                for entrance in self._hk_entrance_clause_cache[player]
            }
            for player in players
        }
        other._hk_checked_state_modifiers = {
            player: {
                entrance: self._hk_checked_state_modifiers[player][entrance].copy()
                for entrance in self._hk_checked_state_modifiers[player]
            }
            for player in players
        }
        other._hk_free_entrances = {player: self._hk_free_entrances[player].copy() for player in players}
        other._hk_processed_item_cache = {player: self._hk_processed_item_cache[player].copy() for player in players}
        other._hk_per_player_sweepable_entrances = {
            player: entrances.copy() for player, entrances in self._hk_per_player_sweepable_entrances.items()
        }
        return other
        # TODO do we need to copy sweepables? should be empty any time we're mucking with resource state
        # yes we do, there's nothing stopping a state from being copied while stale

    def _hk_apply_and_validate_state(self, clause: "HKClause", region: Region, target_region=None) -> bool:
        player = region.player
        # available_states = self._hk_per_player_resource_states[player].get(region.name, None)

        # if available_states is None:
        #     region.can_reach(self)
        #     available_states = self._hk_per_player_resource_states[player].get(region.name, [])

        # unneeded?
        available_states = [s for s in self._hk_per_player_resource_states[player][region.name]]
        # loses the can_reach parent call, potentially re-add it?

        if not available_states:
            # no valid parent states
            return False

        for handler in clause.hk_state_requirements:
            available_states = [
                s
                for input_state in available_states
                for s in handler.modify_state(input_state, self)
            ]

        if not available_states:
            return False
        if not target_region:
            # don't persist
            return True
        target_states = self._hk_per_player_resource_states[player][target_region.name]
        if target_states == [0]:
            return True
        if len(available_states) > 1:
            available_states.sort()
            ind = 1
            while ind < len(available_states):
                for prev in range(ind):
                    if rs_leq(available_states[prev],available_states[ind]):
                        available_states.pop(ind)
                        break
                else:
                    ind += 1
        if available_states:
            if available_states == target_states:
                return True
            # mergesort-like merging
            target_index = 0
            available_index = 0
            new_useful_state = False
            while available_index < len(available_states) or target_index < len(target_states):
                if available_index == len(available_states):
                    side_to_check = 0
                elif target_index == len(target_states):
                    side_to_check = 1
                elif target_states[target_index] == available_states[available_index]:
                    # since it's in target_states it's not always worse than any state there
                    # and since it's in available_states it's not always worse than any state there
                    # so we're always free to let it stay
                    available_index += 1
                    target_index += 1
                    continue
                elif target_states[target_index] < available_states[available_index]:
                    side_to_check = 0
                else:
                    side_to_check = 1
                if side_to_check == 0:
                    for prev in range(target_index):
                        if rs_leq(target_states[prev], target_states[target_index]):
                            target_states.pop(target_index)
                            break
                    else:
                        target_index += 1
                elif side_to_check == 1:
                    for prev in range(target_index):
                        if rs_leq(target_states[prev], available_states[available_index]):
                            break
                    else:
                        new_useful_state = True
                        target_states.insert(target_index, available_states[available_index])
                        target_index += 1
                    available_index += 1
            if new_useful_state:
                self.reachable_regions[player].add(target_region)
                for exit in target_region.exits:
                    self._hk_per_player_sweepable_entrances[player].add(exit.name)
                    self._hk_checked_state_modifiers[player][exit.name] = set()
                for exit in self.multiworld.indirect_connections.get(target_region, set()):
                    self._hk_per_player_sweepable_entrances[player].add(exit.name)
                    self._hk_checked_state_modifiers[player][exit.name] = set()
            # self._hk_stale[player] = True
        assert target_states
        return True

    def _hk_sweep(self, player: int):
        if self._hk_sweeping[player]:
            return
        self._hk_sweeping[player] = True
        world = self.multiworld.worlds[player]
        start = world.get_region(world.origin_region_name)
        if start not in self.reachable_regions[player]:
            self.reachable_regions[player].add(start)
            for start_exit in start.exits:
                self._hk_per_player_sweepable_entrances[player].add(start_exit.name)
        # assume not stale and only evaluate true clauses
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


# Requirements for state comparison:
# negative values won't exist
# best case is falsy
# keys in right that are not in left are inherently lt
# any key in left > right is a failure
# any key in left and not in right is a failure
# don't care about full equality because of codepath
