from BaseClasses import MultiWorld, CollectionState, Region
from typing import TYPE_CHECKING, Tuple, NamedTuple, Dict, Set, Any, List
from worlds.AutoWorld import LogicMixin
from .Charms import names as charm_names
from collections import Counter
from copy import deepcopy

if TYPE_CHECKING:
    from . import HKWorld, HKClause

default_state = ([], Counter({"DAMAGE": 0, "SPENTSHADE": 0, "SPENTSOUL": 0, "NOFLOWER": 0, "SPENTNOTCHES": 0}))
BASE_SOUL = 12
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
        for player in players:
            self.prog_items[player]["TOTAL_SOUL"] = BASE_SOUL
            self.prog_items[player]["TOTAL_HEALTH"] = BASE_HEALTH
            self.prog_items[player]["SHADE_HEALTH"] = max(int(BASE_HEALTH/2), 1)

    def copy_mixin(self, other) -> CollectionState:
        other._hk_per_player_resource_states = self._hk_per_player_resource_states
        other._hk_free_entrances = self._hk_free_entrances
        return other
        # TODO do we need to copy sweepables? should be empty any time we're mucking with resource state

    def _hk_apply_and_validate_state(self, clause: "HKClause", region, target_region=None) -> bool:
        player = region.player
        requires_shadeskip = clause.hk_state_requirements.shadeskip
        requies_twister = clause.hk_state_requirements.twister_required
        avaliable_states = self._hk_per_player_resource_states[player].get(region.name, None)

        any_true = False
        if target_region:
            target_states = self._hk_per_player_resource_states[player].get(target_region.name, [])
            self._hk_per_player_resource_states[player][target_region.name] = target_states
            persist = True
        else:
            persist = False

        if avaliable_states is None:
            region.can_reach(self)
            avaliable_states = self._hk_per_player_resource_states[player].get(region.name, [])
        if requires_shadeskip:
            avaliable_states = [state for state in avaliable_states if not state[1]["SPENTSHADE"]]
        if False and requies_twister:
            # TODO do black magic here
            self.has("Spell_Twister", player)

        if not avaliable_states:
            # no valid parent states
            return False

        for state_tuple in avaliable_states:
            state = state_tuple[1]
            # TODO see if we can remove the charm list
            for reset_key in clause.hk_before_resets:
                state[reset_key] = 0
            for key, value in clause.hk_state_modifiers.items():
                state[key] += value

            if not self.prog_items[player]["TOTAL_HEALTH"] > state["DAMAGE"]:
                continue
            if not self.prog_items[player]["SHADE_HEALTH"] >= state["SPENTSHADE"]:
                continue
            if not self.prog_items[player]["TOTAL_SOUL"] >= state["SPENTCASTS"] * (3 if "Spell_Twister" in state_tuple[0] else 4):
                continue
            # TODO charm+notch calcs

            for reset_key in clause.hk_after_resets:
                state[reset_key] = 0

            if persist:
                any_true = True
                self._hk_per_player_resource_states[player][target_region.name].append(([], state))
            else:
                # we only need one success
                return True

        if any_true and persist:
            simplify(self, target_region)
            # after a simplify if there are more or any different states then there are new states that should be swept
            if self._hk_per_player_resource_states[player][target_region.name] != target_states:
                self._hk_per_player_sweepable_entrances[player].update({exit.name for exit in target_region.exits})
                self.sweep_for_resource_state(player)
            return True
        else:
            return False

    def sweep_for_resource_state(self, player):
        # TODO assume not stale and only evaluate true clauses
        # (region can_reach dependencies will be covered by indirect connections)
        while self._hk_per_player_sweepable_entrances[player]:
            # random pop but i don't really care
            entrance = self._hk_per_player_sweepable_entrances[player].pop()
            self.can_reach_entrance(entrance, player)


def simplify(state, region):
    def ge(state1, state2) -> bool:
        return all(state1[key] >= state2[key] for key in state2.keys())

    previous_states = state._hk_per_player_resource_states[region.player][region.name]
    if len(previous_states) == 1:
        return
    output_states = []  # previous_states.copy()
    for charms, counter in previous_states:
        if len(output_states) == 0:
            output_states.append((charms, counter))
            continue

        if any(not ge(counter, c) for _, c in output_states):
            output_states.append((charms, counter))

    state._hk_per_player_resource_states[region.player][region.name] = output_states
