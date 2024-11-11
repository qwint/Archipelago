from BaseClasses import MultiWorld, CollectionState, Region
from typing import TYPE_CHECKING, Tuple, NamedTuple, Dict, Set, Any, List, Type, Generator, Optional, ClassVar
from worlds.AutoWorld import LogicMixin
from .Charms import names as charm_names, charm_name_to_id
from collections import Counter
from copy import deepcopy
from Utils import KeyedDefaultDict

if TYPE_CHECKING:
    from . import HKWorld, HKClause

default_state = Counter({"NOFLOWER": 1})
BASE_SOUL = 12
BASE_NOTCHES = 3
BASE_HEALTH = 4


class HKLogicMixin(LogicMixin):
    multiworld: MultiWorld
    _hk_per_player_resource_states: Dict[int, Dict[str, List[Counter]]]
    """resource state blob to map regions and their avalible resource states"""
    # state blob is [Counter({"DAMAGE": 0, "SPENTSOUL": 0, "NOFLOWER": 0, "CHARMNOTCHESSPENT": 0})]

    _hk_per_player_sweepable_entrances: Dict[int, Set[str]]
    """mapping for entrances that need to be statefully swept"""

    _hk_stale: Dict[int, bool]
    """TODO: make an item stale and a resource_state_stale difference"""

    _hk_free_entrances: Dict[int, Set[str]]
    """mapping for entrances that will not alter resource state no matter how many more items we get, for optimization"""

    _hk_entrance_clause_cache: Dict[int, Dict[str, Dict[int, bool]]]
    """mapping for clauses per entrance per player to short circuit non-resource state calculations"""

    _hk_processed_item_cache: Dict[int, Counter]

    def init_mixin(self, multiworld) -> None:
        from . import HKWorld as cls
        players = multiworld.get_game_players(cls.game)
        self._hk_per_player_resource_states = {player: KeyedDefaultDict(lambda region: [default_state.copy()] if region == "Menu" else []) for player in players}  # {player: {init_state: [start_region]} for player in players}
        self._hk_per_player_sweepable_entrances = {player: set() for player in players}
        self._hk_free_entrances = {player: {"Menu"} for player in players}
        self._hk_entrance_clause_cache = {player: {} for player in players}
        self._hk_stale = {player: True for player in players}
        self._hk_processed_item_cache = {player: Counter() for player in players}
        # for player in players:
        #     self.prog_items[player]["TOTAL_SOUL"] = BASE_SOUL
        #     self.prog_items[player]["TOTAL_HEALTH"] = BASE_HEALTH
        #     self.prog_items[player]["SHADE_HEALTH"] = max(int(BASE_HEALTH/2), 1)
        #     self.prog_items[player]["TOTAL_NOTCHES"] = BASE_NOTCHES

    def copy_mixin(self, other) -> CollectionState:
        from . import HKWorld as cls
        players = self.multiworld.get_game_players(cls.game)
        other._hk_per_player_resource_states = {player: self._hk_per_player_resource_states[player].copy() for player in players}
        other._hk_free_entrances = {player: self._hk_free_entrances[player].copy() for player in players}
        other._hk_processed_item_cache = {player: self._hk_processed_item_cache[player].copy() for player in players}
        return other
        # TODO do we need to copy sweepables? should be empty any time we're mucking with resource state

    def _hk_apply_and_validate_state(self, clause: "HKClause", region, target_region=None) -> bool:
        player = region.player
        # avaliable_states = self._hk_per_player_resource_states[player].get(region.name, None)

        # if avaliable_states is None:
        #     region.can_reach(self)
        #     avaliable_states = self._hk_per_player_resource_states[player].get(region.name, [])

                           # unneeded?
        avaliable_states = self._hk_per_player_resource_states[player][region.name].copy()
        # loses the can_reach parent call, potentially re-add it?

        if not avaliable_states:
            # no valid parent states
            return False

        if target_region:
            persist = True
        else:
            persist = False

        for handler in clause.hk_state_requirements:
            avaliable_states = [s for input_state in avaliable_states for s in handler.ModifyState(input_state, self, player)]

        if len(avaliable_states):
            if not persist:
                return True
            else:
                improved = False
                # if len(self._hk_per_player_resource_states[player][target_region.name]):
                #     print(self._hk_per_player_resource_states[player][target_region.name])
                #     print(avaliable_states)
                #     breakpoint()
                for s in avaliable_states:
                    if any(s == previous or lt(previous, s) for previous in self._hk_per_player_resource_states[player][target_region.name]):
                        # if the state we're adding already exists or a better state already exists, we didn't improve
                        continue
                    self._hk_per_player_resource_states[player][target_region.name].append(s)
                    improved = True
                if improved:
                    indicies_to_pop = []
                    for index, s in enumerate(self._hk_per_player_resource_states[player][target_region.name]):
                        if any(lt(other, s) for other in self._hk_per_player_resource_states[player][target_region.name]):
                            indicies_to_pop.append(index)
                    # if not indicies_to_pop and len(self._hk_per_player_resource_states[player][target_region.name]) > 1:
                    #     print(self._hk_per_player_resource_states[player][target_region.name])
                    #     breakpoint()
                    for index in reversed(indicies_to_pop):
                        # reverse so we can blindly pop
                        self._hk_per_player_resource_states[player][target_region.name].pop(index)
                    self._hk_per_player_sweepable_entrances[player].update({exit.name for exit in target_region.exits})
                    self._hk_stale[player] = True
                assert self._hk_per_player_resource_states[player][target_region.name]
                return True
        else:
            return False

    def _hk_sweep(self, player):
        if not self._hk_stale[player]:
            return
        self._hk_stale[player] = False
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

            # for index in [index for index, status in self._hk_entrance_clause_cache[player][entrance_name].items() if status]:
            #     self._hk_apply_and_validate_state(entrance.hk_rule[index], entrance.parent_region, target_region=entrance.connected_region)


def ge(state1, state2) -> bool:
    return all(state1[key] >= state2[key] for key in state2.keys())


def lt(state1, state2) -> bool:
    if state1 == state2:
        return False
    if any(key not in state2 for key in state1.keys()):
        return False
    if any(state1[key] > state2[key] for key in state1.keys()):
        return False
    return True
    # return sum(state1[key] <= state2[key] for key in state1.keys()) == 1 and sum(state1[key] < state2[key] for key in state1.keys()) == 1
    # return not ge(state1, state2)

# negative values won't exist
# best case is falsy
# keys in right that are not in left are inherently lt
# any key in left > right is a failure
# any key in left and not in right is a failure
# don't care about full equality because of codepath


class resource_state_handler(Type):
    handlers: list["RCStateVariable"] = []

    def __new__(mcs, name, bases, dct):
        new_class = super().__new__(mcs, name, bases, dct)
        resource_state_handler.handlers.append(new_class)
        return new_class


class RCStateVariable(metaclass=resource_state_handler):
    prefix: str

    def __init__(self, term):
        assert term.startswith(self.prefix)

        # expecting "prefix" or "prefix[one,two,three]"
        if term != self.prefix:
            params = term[len(self.prefix)+1:-1].split(",")
            self.parse_term(*params)
        else:
            self.parse_term()

    def parse_term(self, *args):
        """Subclasses should use this to expect parameter counts for init"""
        pass

    @classmethod
    def TryMatch(cls, term: str) -> bool:
        """Returns True if this class can handle the passed in term"""
        return False

    @classmethod
    def GetTerms(cls):
        """"""
        return []

    def ModifyState(self, state_blob, item_state, player):  # -> Generator["state_blob"]:
        # print(self)
        # return (output_state for valid, output_state in [self._ModifyState(state_blob, item_state, player)] if valid)
        valid, output_state = self._ModifyState(state_blob, item_state, player)
        if valid:
            yield output_state

    def _ModifyState(self, state_blob, item_state, player) -> Tuple[bool, "state_blob"]:
        pass

    def can_exclude(self, options) -> bool:
        return True


class DirectCompare():
    term: str
    op: ClassVar[str]
    value: str  # may be int or bool

    def __init__(self, term):
        self.term, self.value = (*term.split(self.op),)

    @classmethod
    def TryMatch(cls, term: str):
        return cls.op in term

    def can_exclude(self, options):
        return False


class EQVariable(DirectCompare, RCStateVariable):
    term: str
    op: str = "="
    value: str  # may be int or bool

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        if self.value.isdigit():
            return state_blob[self.term] == int(self.value), state_blob
        else:
            v = self.value == "TRUE"
            assert v or self.value == "FALSE"
            return state_blob[self.term] == v, state_blob


class GTVariable(DirectCompare, RCStateVariable):
    term: str
    op: str = ">"
    value: str

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        assert self.value.isdigit()
        return state_blob[self.term] > int(self.value), state_blob


class GTVariable(DirectCompare, RCStateVariable):
    term: str
    op: str = "<"
    value: str

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        assert self.value.isdigit()
        return state_blob[self.term] < int(self.value), state_blob


class RCResetter():
    reset_properties: List[str]

    def parse_term(self):
        pass

    def _ModifyState(self, state_blob, item_state, player):
        for reset in self.reset_properties:
            del state_blob[reset]
        return True, state_blob

    @classmethod
    def TryMatch(cls, term: str):
        return term.startswith(cls.prefix)

    def can_exclude(self, options):
        return False


class BenchResetVariable(RCResetter, RCStateVariable):
    prefix = "$BENCHRESET"
    reset_properties = ["BenchResetCondition", "SPENTSHADE", "SPENTNOTCHES", "DAMAGE"]

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))


class CastSpellVariable(RCStateVariable):
    prefix = "$CASTSPELL"
    casts: List[int]
    before: Optional[str]
    after: Optional[str]

    def parse_term(self, *args):
        self.casts = []
        self.before = None
        self.after = None
        for arg in args:
            if arg.isdigit():
                self.casts.append(int(arg))
            elif arg.startswith("before"):
                self.before = arg[7:]
            elif arg.startswith("after"):
                self.after = arg[6:]
            # elif arg == "noDG":
                # is this even real?
            elif arg in ("NOLEFTSTALL", "NORIGHTSTALL", "NOSTALL",):
                pass
            else:
                raise Exception(f"unknown {self.prefix} term, args: {args}")
        if len(self.casts) == 0:
            self.casts.append(1)

    @classmethod
    def TryMatch(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        # TODO actually flesh this out
        max_soul = 99
        soul_burn = sum(self.casts) * 33
        if self.before:
            state_blob["SPENTSOUL"] = 0

        if max_soul < soul_burn + state_blob["SPENTSOUL"]:
            return False, state_blob
        else:
            state_blob["SPENTSOUL"] += soul_burn
            if self.after:
                state_blob["SPENTSOUL"] = 0
            return True, state_blob

    def can_exclude(self, options):
        return False


class EquipCharmVariable(RCStateVariable):
    prefix = "$EQUIPPEDCHARM"
    excluded_charm_ids: Tuple[int] = (23, 24, 25, 36,)  # fragiles and Kingsoul
    charm_id: int
    charm_name: str

    @staticmethod
    def charm_id_and_name(charm) -> Tuple[int, str]:
        if not charm.isdigit():
            return charm_name_to_id[charm] + 1, charm
        else:
            return charm, charm_names[charm - 1]  # TODO

    def parse_term(self, charm):
        self.charm_id, self.charm_name = self.charm_id_and_name(charm)

    @classmethod
    def TryMatch(cls, term: str):
        if term.startswith(cls.prefix):
            charm_id, _ = cls.charm_id_and_name(term[len(cls.prefix)+1:-1])
            # covered by other handlers
            if charm_id not in cls.excluded_charm_ids:
                return True
        # else
        return False

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def has_item(self, item_state, player):
        return bool(item_state._hk_processed_item_cache[player][self.charm_name])

    def _ModifyState(self, state_blob, item_state, player):
        # TODO figure this out
        charm_key = f"CHARM{self.charm_id}"
        if charm_key in state_blob:
            return True, state_blob
        if f"no{charm_key}" in state_blob:
            return False, state_blob
        if not self.has_item(item_state, player):
            return False, state_blob
        else:
            # TODO
            state_blob[charm_key] = 1
            return True, state_blob

    def can_exclude(self, options):
        return False


class FragileCharmVariable(EquipCharmVariable):
    # prefix = "$EQUIPPEDCHARM"
    fragile_lookup = {
        23: ["Fragile_Heart", "Unbreakable_Heart"],
        24: ["Fragile_Greed", "Unbreakable_Greed"],
        25: ["Fragile_Strength", "Unbreakable_Strength"],
    }

    # def parse_term(self):
    #     pass

    @classmethod
    def TryMatch(cls, term: str):
        if term.startswith(cls.prefix):
            charm_id, _ = cls.charm_id_and_name(term[len(cls.prefix)+1:-1])
            if charm_id in cls.fragile_lookup:
                return True
        # else
        return False

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        # TODO flush out with charm notch checking etc.
        if self.has_item(item_state, player):
            return True, state_blob
        else:
            return False, state_blob


class WhiteFragmentEquipVariable(EquipCharmVariable):
    # prefix = "$EQUIPPEDCHARM"
    void: bool

    def parse_term(self, charm):
        self.charm_id, self.charm_name = self.charm_id_and_name(charm)
        self.void = charm == "Void_Heart"
        assert not self.void == (charm == "Kingsoul")

    @classmethod
    def TryMatch(cls, term: str):
        if term.startswith(cls.prefix):
            charm_id, _ = cls.charm_id_and_name(term[len(cls.prefix)+1:-1])
            if charm_id == 36:
                return True
        # else
        return False

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def has_item(self, item_state, player):
        if self.void:
            count = 3
        else:
            count = 2
        return item_state._hk_processed_item_cache[player]["WHITEFRAGMENT"] >= count

    # def _ModifyState(self, state_blob, item_state, player):
    #     # TODO figure this out
    #     # TODO actually
    #     print(self.void)
    #     return super()._ModifyState(state_blob, item_state, player)


class FlowerProviderVariable(RCResetter, RCStateVariable):
    prefix = "$FLOWERGET"
    reset_properties = ["NOFLOWER"]

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))


class HotSpringResetVariable(RCResetter, RCStateVariable):
    prefix = "$HOTSPRINGRESET"
    reset_properties = ["HotSpringResetCondition", "SPENTSOUL", "DAMAGE"]

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))


class RegainSoulVariable(RCStateVariable):
    prefix = "$REGAINSOUL"
    amount: int

    def parse_term(self, amount):
        self.amount = int(amount)

    @classmethod
    def TryMatch(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        # TODO figure this out
        previous = state_blob["SPENTSOUL"]
        if previous <= self.amount:
            state_blob["SPENTSOUL"] = 0
        else:
            state_blob["SPENTSOUL"] -= self.amount
        return True, state_blob["SPENTSOUL"]

    def can_exclude(self, options):
        return False


class SaveQuitResetVariable(RCResetter, RCStateVariable):
    prefix = "$SAVEQUITRESET"
    reset_properties = ["SaveQuitConditionalReset", "DAMAGE"]

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))


class ShadeStateVariable(RCStateVariable):
    prefix = "$SHADESKIP"
    health: int

    def parse_term(self, *args):
        if len(args) == 1:
            hits = args[0]
            self.health = hits[:-4]
        elif len(args) == 0:
            self.health = 1
        else:
            raise Exception(f"unknown {self.prefix} term, args: {args}")

    @classmethod
    def TryMatch(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        # TODO figure this out
        # TODO update
        if state_blob["SpentShade"]:
            return False, state_blob
        else:
            state_blob["SpentShade"] = True
            return True, state_blob

    def can_exclude(self, options):
        return not bool(options.ShadeSkips)


class ShriekPogoVariable(CastSpellVariable):
    prefix = "$SHRIEKPOGO"

    @classmethod
    def TryMatch(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        # TODO figure this out
        if not item_state.has_all_counts({"SCREAM": 2, "WINGS": 1}, player):
            return False, state_blob
        else:
            return super()._ModifyState(state_blob, item_state, player)

    def can_exclude(self, options):
        return True
        # TODO add the option lol
        on = bool(options.ShriekPogoSkips)
        difficult = sum(self.casts) > 3
        difficult_on = bool(options.DifficultSkips)
        return (not on) or (difficult and not difficult_on)


class SlopeballVariable(CastSpellVariable):
    prefix = "$SLOPEBALL"

    @classmethod
    def TryMatch(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        # TODO figure this out
        if not item_state.has("FIREBALL", player):
            return False, state_blob
        else:
            return super()._ModifyState(state_blob, item_state, player)

    def can_exclude(self, options):
        return True
        # TODO add the option lol
        return bool(options.SlopeBallSkips)


class SpendSoulVariable(RCStateVariable):
    prefix = "$SPENDSOUL"
    amount: int

    def parse_term(self, amount):
        self.amount = amount

    @classmethod
    def TryMatch(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        # TODO actually flesh this out
        max_soul = 99
        soul_burn = self.amount

        if max_soul < soul_burn + state_blob["SPENTSOUL"]:
            return False, state_blob
        else:
            state_blob["SPENTSOUL"] += soul_burn
            return True, state_blob

    def can_exclude(self, options):
        return False


class StagStateVariable(RCStateVariable):
    prefix = "$STAGSTATEMODIFIER"

    def parse_term(self):
        pass

    @classmethod
    def TryMatch(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        state_blob["NOFLOWER"] = 1
        return True, state_blob

    def can_exclude(self, options):
        return False


class StartRespawnResetVariable(RCResetter, RCStateVariable):
    prefix = "$BENCHRESET"
    reset_properties = ["StartRespawnResetCondition", "DAMAGE"]

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    # def _ModifyState(self, state_blob, item_state, player):
    #     # TODO figure this out
    #     pass


# i don't know what this is for; says it's for handling subhandlers but not sure when
# class StateModifierWrapper(RCStateVariable):
#     prefix = "$BENCHRESET"

#     def parse_term(self):
#         pass

#     @classmethod
#     def TryMatch(cls, term: str):
#         return term.startswith(cls.prefix)

#     # @classmethod
#     # def GetTerms(cls):
#     #     return (term for term in ("VessleFragments",))

#     def _ModifyState(self, state_blob, item_state, player):
#         # TODO figure this out
#         pass

#     def can_exclude(self, options):
#         return False


class TakeDamageVariable(RCStateVariable):
    prefix = "$TAKEDAMAGE"
    damage: int

    def parse_term(self, damage=1):
        self.damage = int(damage)
        pass

    @classmethod
    def TryMatch(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def _ModifyState(self, state_blob, item_state, player):
        # TODO figure this out
        if self.damage + state_blob["DAMAGE"] >= BASE_HEALTH:
            return False, state_blob
        else:
            state_blob["DAMAGE"] += self.damage
            return True, state_blob

    def can_exclude(self, options):
        # can not actually be excluded because the damage skip option is checked in logic seperately
        return False


class WarpToBenchResetVariable(RCStateVariable):
    prefix = "$WARPTOBENCH"
    sq_reset: SaveQuitResetVariable
    bench_reset: BenchResetVariable

    def parse_term(self):
        self.sq_reset = SaveQuitResetVariable(SaveQuitResetVariable.prefix)
        self.bench_reset = BenchResetVariable(BenchResetVariable.prefix)

    @classmethod
    def TryMatch(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def ModifyState(self, state_blob, item_state, player):
        # under the knowledge that these do not proliferate state
        sq_state = next(self.sq_reset.ModifyState(state_blob, item_state, player))
        yield next(self.bench_reset.ModifyState(sq_state, item_state, player))
        # return (output_state for valid, output_state in self._ModifyState(state_blob) if valid)

    def _ModifyState(self, state_blob, item_state, player):
        # TODO figure this out
        valid, state_blob = self.sq_reset._ModifyState(state_blob, item_state, player)
        if valid:
            return BenchResetVariable._ModifyState(state_blob, item_state, player)
        else:
            return False, state_blob

    def can_exclude(self, options):
        return False


class WarpToStartResetVariable(RCStateVariable):
    prefix = "$WARPTOSTART"
    sq_reset: SaveQuitResetVariable
    start_reset: StartRespawnResetVariable

    def parse_term(self):
        self.sq_reset = SaveQuitResetVariable(SaveQuitResetVariable.prefix)
        self.start_reset = StartRespawnResetVariable(StartRespawnResetVariable.prefix)

    @classmethod
    def TryMatch(cls, term: str):
        return term.startswith(cls.prefix)

    # @classmethod
    # def GetTerms(cls):
    #     return (term for term in ("VessleFragments",))

    def ModifyState(self, state_blob, item_state, player):
        # under the knowledge that these do not proliferate state
        sq_state = next(self.sq_reset.ModifyState(state_blob, item_state, player))
        yield next(self.start_reset.ModifyState(sq_state, item_state, player))
        # return (output_state for valid, output_state in self._ModifyState(state_blob) if valid)

    def _ModifyState(self, state_blob, item_state, player):
        # TODO figure this out
        valid, state_blob = self.sq_reset._ModifyState(state_blob, item_state, player)
        if valid:
            return BenchResetVariable._ModifyState(state_blob, item_state, player)
        else:
            return False, state_blob

    def can_exclude(self, options):
        return False
