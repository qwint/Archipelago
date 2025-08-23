from collections import Counter
from typing import Iterable, NamedTuple

from BaseClasses import CollectionState
from test.param import classvar_matrix

from .bases import NoStepHK
from ..resource_state_vars import ResourceStateHandler
from ..resource_state_vars.health_manager import HealthManager
from ..resource_state_vars.soul_manager import SoulManager

# TODO: convert some/all of these next() calls to get one state into comprehensions to get all of them and assert len=1


class inputs(NamedTuple):
    key: str | None = None
    resource: dict[str, int] = {}
    cs: dict[str, int] = {}
    assert_empty: bool = False
    prep_vars: Iterable[str] = ()
    expecteds: Iterable[Iterable[tuple[int, int, int, int]]] = ()


class StateVarSetup:
    key: str
    """relevant state variable key"""
    resource: dict[str, int]
    """starting Resource State"""
    cs: dict[str, int]
    """starting CollectionState"""
    prep_vars: Iterable[str]
    """other state variable keys to modify state before use"""

    def get_initialized_args(self):
        state = CollectionState(self.multiworld)
        for item, i in self.cs.items():
            # assert item in self.world.item_name_to_id, f"Unknown item collected {item}"
            for _ in range(i):
                state.collect(self.world.create_item(item))
        rs = Counter(self.resource)
        for prep in self.prep_vars:
            rs = next(ResourceStateHandler.get_handler(prep).modify_state(rs, state, self.player))
        return rs, state, self.player

    # TODO: cached?
    def get_handler(self):
        return ResourceStateHandler.get_handler(self.key)

    def get_modified_state(self):
        rs, cs, pi = self.get_initialized_args()

        handler = self.get_handler()
        return [s for s in handler.modify_state(rs, cs, pi)]


ers = {"NOPASSEDCHARMEQUIP": 0, "NOFLOWER": 0}  # Empty Resource State


input_matrix = [
    inputs("FOO=0"),
    inputs("$SHADESKIP", cs={"King_Fragment": 1, "Queen_Fragment": 1}, assert_empty=True),

    inputs("$CASTSPELL[3]"),
    inputs("$CASTSPELL[3]", prep_vars=("$SHADESKIP",), assert_empty=True),
    inputs("$CASTSPELL[4]", cs={"Vessel_Fragment": 3}, assert_empty=True),
    inputs("$CASTSPELL[4]", resource={"NOPASSEDCHARMEQUIP": 0, "NOTCHES": 6}, cs={"Spell_Twister": 1}),
    inputs("$CASTSPELL[3,1]", cs={"Vessel_Fragment": 3}),

    # TODO, add tests for equip charm and hp state

    inputs("$LIFEBLOOD", resource=ers, assert_empty=True),
    *[inputs("$LIFEBLOOD", resource={**ers, "NOTCHES": 4}, cs={charm: 1})
      for charm in ("Lifeblood_Heart", "Lifeblood_Core", "Joni's_Blessing")],
    inputs("$LIFEBLOOD", resource=ers, cs={"Lifeblood_Heart": 1}, assert_empty=True, prep_vars=("$TAKEDAMAGE[2]",)),
    *[inputs("$LIFEBLOOD", resource=ers, cs={charm: 1}, prep_vars=("$TAKEDAMAGE[2]",))
      for charm in ("Lifeblood_Core", "Joni's_Blessing")],

    # inputs("$SHADESKIP", assert_empty=True),  # theoretically checking if the option is disabled but idk
    inputs("$SHADESKIP", resource={"USEDSHADE": 1}, assert_empty=True),
    inputs("$SHADESKIP", resource={"CHARM36": 3}, assert_empty=True),  # TODO: make sure this aligns with having void heart equipped
    inputs("$SHADESKIP", resource={"REQUIREDMAXSOUL": 67}, assert_empty=True),
    inputs("$SHADESKIP"),
    inputs("$SHADESKIP[2HITS]", resource={"MASKSHARDS": 4}, assert_empty=True),  # TODO make sure that this aligns with how i set up damage state var in the future
    inputs("$SHADESKIP[2HITS]", resource={"MASKSHARDS": 16}),
    inputs("$SHADESKIP[2HITS]", resource={"MASKSHARDS": 8, "NOTCHES": 6},
           cs={"Can_Repair_Fragile_Charms": 1, "Fragile_Heart": 1}),
    inputs("$SHADESKIP[2HITS]", resource={"MASKSHARDS": 8, "NOTCHES": 6},
           cs={"Unbreakable_Strength": 1, "Fragile_Heart": 1}),
    inputs("$SHADESKIP[2HITS]", resource={"MASKSHARDS": 8, "NOTCHES": 6, "BROKEHEART": 1},
           cs={"Can_Repair_Fragile_Charms": 1, "Fragile_Heart": 1}, assert_empty=True),

    # TODO, add shrogo, slopeball, soulstate, takedamage tests
]


@classvar_matrix(matrix_vars=input_matrix)
class TestStateVars(StateVarSetup, NoStepHK):
    matrix_vars: inputs
    assert_empty: bool

    def setUp(self):
        super().setUp()
        self.key = self.matrix_vars.key
        self.resource = self.matrix_vars.resource
        self.cs = self.matrix_vars.cs
        self.prep_vars = self.matrix_vars.prep_vars

        self.assert_empty = self.matrix_vars.assert_empty

    def test_output(self):
        outputs = self.get_modified_state()
        if self.assert_empty:
            self.assertFalse(outputs, "Expected to not be in logic but was")
        else:
            self.assertTrue(outputs, "Expected to be in logic but was not")


soul_matrix = [
    inputs(resource=ers, expecteds=[[(33, 0, 33, 0)], [(66, 0, 66, 0)], [(99, 0, 99, 0)], []]),
    inputs(resource=ers, cs={"Vessel_Fragment": 3}, expecteds=[[(0, 33, 33, 0)], [(33, 33, 33, 0)], [(66, 33, 66, 0)], [(99, 33, 99, 0)], []]),
    inputs(resource={**ers, "SOULLIMITER": 33}, expecteds=[[(33, 0, 33, 33)], [(66, 0, 66, 33)], []]),  # TODO: update to LimitSoul function or similar
]


@classvar_matrix(matrix_vars=soul_matrix)
class TestSoulManagement(StateVarSetup, NoStepHK):
    key = "$SSM"
    matrix_vars: inputs
    expecteds: Iterable[list[tuple[int, int, int, int]]]

    def setUp(self):
        super().setUp()
        self.resource = self.matrix_vars.resource
        self.cs = self.matrix_vars.cs
        self.prep_vars = self.matrix_vars.prep_vars

        self.expecteds = self.matrix_vars.expecteds

    def test_spend_soul(self):
        rs, cs, pi = self.get_initialized_args()
        handler = self.get_handler()

        for i, expected in enumerate(self.expecteds):
            outputs = [s for s in handler.modify_state(rs, cs, pi)]
            self.assertEqual([(
                    s["SPENTSOUL"],
                    s["SPENTRESERVESOUL"],
                    s["REQUIREDMAXSOUL"],
                    s["SOULLIMITER"],
                ) for s in outputs], expected, f"Failed on expected index {i}")
            rs = outputs[0] if outputs else []

# TODO: the rest of the soul management tests


class TestHPManager(StateVarSetup, NoStepHK):
    key = "$HPSM"
    resource = {}
    cs = {}
    prep_vars = []

    def assert_spent_health(self, lazy: int, white: int, blue: int):
        healths = rs["LAZYSPENTHP"], rs["SPENTHP"], rs["SPENTBLUEHP"]
        assert healths == (lazy, white, blue), (
            f"Expected LAZYSPENTHP={'max' if lazy == HealthManager.max_damage else lazy}, "
            f"SPENTHP={white}, SPENTBLUEHP={blue}, but were {healths} instead."
        )

    def test_strict_early(self):
        rs, cs, pi = self.get_initialized_args()
        manager = self.get_handler()

        rs = next(manager.determine_hp(rs, cs, pi))
        self.assert_spent_health(manager.max_damage, 0, 0)
        rs = next(manager.take_damage(rs, cs, pi, 1))  # TODO confirm what this assumption is right
        self.assert_spent_health(manager.max_damage, 1, 0)

    def test_lazy_to_strict(self):
        rs, cs, pi = self.get_initialized_args()
        manager = self.get_handler()

        for i in range(1, 3):
            rs = next(manager.take_damage(rs, cs, pi, 1))
            self.assert_spent_health(i, 0, 0)
            assert not manager.is_hp_determined(rs), "HP was set to determined after lazy damage"
        for i in range(3, 5):
            rs = next(manager.take_damage(rs, cs, pi, 1))
            self.assert_spent_health(manager.max_damage, i, 0)
            assert manager.is_hp_determined(rs), "HP was not set to determined after taking too much lazy damage"
        rs = [s for s in manager.take_damage(rs, cs, pi, 1)]
        assert not rs, "States were returned after taking enough damage to kill"


class TestJoniHP(StateVarSetup, NoStepHK):
    key = "$HPSM"
    resource = {**ers, "NOTCHES": 4, "CANNOTOVERCHARM": 1}
    cs = {"Joni's_Blessing": 1}
    prep_vars = ["$EQUIPPEDCHARM[Joni's_Blessing]"]

    def test_joni_info(self):
        rs, cs, pi = self.get_initialized_args()
        manager = self.get_handler()

        rs = manager.determine_hp(rs, cs, pi)
        hp = manager.get_hp_info(rs, cs, pi)
        assert hp.max_white_hp == 7, f"Expected Max White HP to be 7 but was {hp.max_white_hp}"
        assert hp.current_white_hp == 7, f"Expected Current White HP to be 7 but was {hp.current_white_hp}"
        assert hp.current_blue_hp == 7, f"Expected Current Blue HP to be 7 but was {hp.current_blue_hp}"
