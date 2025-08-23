from collections import Counter
from typing import Iterable, NamedTuple

from BaseClasses import CollectionState
from test.param import classvar_matrix

from .bases import NoStepHK
from ..resource_state_vars import ResourceStateHandler
from ..resource_state_vars.health_manager import HealthManager
from ..resource_state_vars.soul_manager import SoulManager


# TODO: revisit this, potentially breaking into different files with different input classes
class inputs(NamedTuple):
    key: str | None = None
    resource: dict[str, int] = {}
    cs: dict[str, int] = {}
    prep_vars: Iterable[str] = ()

    assert_empty: bool = False
    expecteds: Iterable[Iterable[tuple[int, int, int, int]]] = ()
    expected: tuple[int, int, int, int] | None = None
    limit: int = 0
    spend: int = 0


def get_one_state(func, *args, **kwargs):
    states = [s for s in func(*args, **kwargs)]
    assert len(states) == 1, f"Expected one state but got {len(states)}"
    return states[0]


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
            rs = get_one_state(ResourceStateHandler.get_handler(prep).modify_state, rs, state, self.player)
        return rs, state, self.player

    # TODO: cached?
    def get_handler(self):
        return ResourceStateHandler.get_handler(self.key)

    def get_modified_state(self):
        rs, cs, pi = self.get_initialized_args()

        handler = self.get_handler()
        return [s for s in handler.modify_state(rs, cs, pi)]


ers = {"NOPASSEDCHARMEQUIP": 0, "NOFLOWER": 0}  # Empty Resource State
one_mask = {"MASKSHARDS": 4}
two_mask = {"MASKSHARDS": 8}

shrogo = {"Monarch_Wings": 1, "Abyss_Shriek": 2}  # include options

input_matrix = [
    inputs("FOO=0"),
    inputs("$SHADESKIP", cs={"King_Fragment": 1, "Queen_Fragment": 1}, assert_empty=True),

    inputs("$CASTSPELL[3]"),
    inputs("$CASTSPELL[3]", prep_vars=("$SHADESKIP",), assert_empty=True),
    inputs("$CASTSPELL[4]", cs={"Vessel_Fragment": 3}, assert_empty=True),
    inputs("$CASTSPELL[4]", resource={"NOPASSEDCHARMEQUIP": 0, "NOTCHES": 6}, cs={"Spell_Twister": 1}),
    inputs("$CASTSPELL[3,1]", cs={"Vessel_Fragment": 3}),

    # TODO, add tests for equip charm

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
    inputs("$SHADESKIP[2HITS]", resource=one_mask, assert_empty=True),  # TODO make sure that this aligns with how i set up damage state var in the future
    inputs("$SHADESKIP[2HITS]", resource={"MASKSHARDS": 16}),
    inputs("$SHADESKIP[2HITS]", resource={**two_mask, "NOTCHES": 6},
           cs={"Can_Repair_Fragile_Charms": 1, "Fragile_Heart": 1}),
    inputs("$SHADESKIP[2HITS]", resource={**two_mask, "NOTCHES": 6},
           cs={"Unbreakable_Strength": 1, "Fragile_Heart": 1}),
    inputs("$SHADESKIP[2HITS]", resource={**two_mask, "NOTCHES": 6, "BROKEHEART": 1},
           cs={"Can_Repair_Fragile_Charms": 1, "Fragile_Heart": 1}, assert_empty=True),

    inputs("$SHRIEKPOGO", assert_empty=True),
    inputs("$SHRIEKPOGO", assert_empty=True, cs={"Monarch_Wings": 1}),
    inputs("$SHRIEKPOGO", assert_empty=True, cs={"Abyss_Shriek": 2}),

    inputs("$SHRIEKPOGO[3]",   cs=shrogo),
    inputs("$SHRIEKPOGO[4]",   cs=shrogo, assert_empty=True),  # Difficult skips
    inputs("$SHRIEKPOGO[4]",   cs={**shrogo, "Spell_Twister": 1}, resource={**ers, "NOTCHES": 6, "DIFFICULTSKIPS": 1}),  # Difficult skips
    inputs("$SHRIEKPOGO[4]",   cs={**shrogo, "Spell_Twister": 1}, resource={**ers, "NOTCHES": 6}, assert_empty=True),  # Difficult skips off
    inputs("$SHRIEKPOGO[4]",   cs={**shrogo, "Vessel_Fragment": 3}, assert_empty=True),  # Difficult skips
    inputs("$SHRIEKPOGO[3,1]", cs={**shrogo, "Vessel_Fragment": 3}),  # Difficult skips
    inputs("$SHRIEKPOGO[4]",   cs={**shrogo, "Vessel_Fragment": 3, "Mothwing_Cloak": 1}),  # Difficult skips

    # TODO, add shrogo, slopeball,
    inputs("$TAKEDAMAGE", assert_empty=True,  resource=one_mask),
    inputs("$TAKEDAMAGE", assert_empty=False, resource=two_mask),
    inputs("$TAKEDAMAGE", assert_empty=True,  resource=two_mask, prep_vars=("$TAKEDAMAGE",)),
    inputs("$TAKEDAMAGE", assert_empty=False, resource=two_mask, prep_vars=("$TAKEDAMAGE",), cs={"FOCUS": 1}),
    inputs("$TAKEDAMAGE", assert_empty=False, resource={**one_mask, "NOTCHES": 6}, prep_vars=("$TAKEDAMAGE",),
           cs={"Lifeblood_Heart": 1}),
    inputs("$TAKEDAMAGE", assert_empty=True,  resource={**one_mask, "NOTCHES": 1}, prep_vars=("$TAKEDAMAGE",),
           cs={"Lifeblood_Heart": 1}),
    inputs("$TAKEDAMAGE", assert_empty=False, resource={**two_mask, "NOTCHES": 6}, prep_vars=("$TAKEDAMAGE[2]",),
           cs={"Lifeblood_Heart": 1}),
    inputs("$TAKEDAMAGE[2]", assert_empty=True, resource={**two_mask, "NOTCHES": 6}, prep_vars=("$TAKEDAMAGE",),
           cs={"Lifeblood_Heart": 1}),
    inputs("$TAKEDAMAGE", assert_empty=False, resource={"MASKSHARDS": 12, "NOTCHES": 1}, prep_vars=("$TAKEDAMAGE",),
           cs={"Lifeblood_Heart": 1}),
    inputs("$TAKEDAMAGE", assert_empty=False, resource={**one_mask, "NOTCHES": 6}, prep_vars=("$TAKEDAMAGE",),
           cs={"Lifeblood_Heart": 1}),  # duplicate?
    inputs("$TAKEDAMAGE", assert_empty=True,  resource={**one_mask, "NOTCHES": 1}, prep_vars=("$TAKEDAMAGE",),
           cs={"Lifeblood_Heart": 1}),  # another?
    inputs("$TAKEDAMAGE", assert_empty=False, resource={**two_mask, "NOTCHES": 6}, prep_vars=("$TAKEDAMAGE",),
           cs={"Hiveblood": 1}),
    inputs("$TAKEDAMAGE", assert_empty=False, resource={"MASKSHARDS": 12, "NOTCHES": 6},
           prep_vars=("$TAKEDAMAGE", "$TAKEDAMAGE", "$TAKEDAMAGE",), cs={"Deep_Focus": 1, "FOCUS": 1}),
    inputs("$TAKEDAMAGE", assert_empty=True,  resource={"MASKSHARDS": 12, "NOTCHES": 6},
           prep_vars=("$TAKEDAMAGE", "$TAKEDAMAGE", "$TAKEDAMAGE", "$TAKEDAMAGE",), cs={"Deep_Focus": 1, "FOCUS": 1}),

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


soul_spend_matrix = [
    inputs(resource=ers, expecteds=[[(33, 0, 33, 0)], [(66, 0, 66, 0)], [(99, 0, 99, 0)], []]),
    inputs(resource=ers, cs={"Vessel_Fragment": 3},
           expecteds=[[(0, 33, 33, 0)], [(33, 33, 33, 0)], [(66, 33, 66, 0)], [(99, 33, 99, 0)], []]),
    inputs(resource={**ers, "SOULLIMITER": 33}, expecteds=[[(33, 0, 33, 33)], [(66, 0, 66, 33)], []], limit=33),
]


@classvar_matrix(matrix_vars=soul_spend_matrix)
class TestSoulSpend(StateVarSetup, NoStepHK):
    key = "$SSM"
    matrix_vars: inputs
    expecteds: Iterable[list[tuple[int, int, int, int]]]
    limit: int = 0

    def setUp(self):
        super().setUp()
        self.resource = self.matrix_vars.resource
        self.cs = self.matrix_vars.cs
        self.prep_vars = self.matrix_vars.prep_vars

        self.expecteds = self.matrix_vars.expecteds
        self.limit = self.matrix_vars.limit

    def test_spend_soul(self):
        rs, cs, pi = self.get_initialized_args()
        manager = self.get_handler()

        if limit:
            rs = manager.limit_soul(rs, cs, pi, limit, True)

        for i, expected in enumerate(self.expecteds):
            outputs = [s for s in manager.modify_state(rs, cs, pi)]
            self.assertEqual([(
                    s["SPENTSOUL"],
                    s["SPENTRESERVESOUL"],
                    s["REQUIREDMAXSOUL"],
                    s["SOULLIMITER"],
                ) for s in outputs], expected, f"Failed on expected index {i}")
            rs = outputs[0] if outputs else []


soul_restore_matrix = [
    inputs(expected=(0, 0, 66, 0)),
    inputs(expected=(0, 0, 66, 0)),
    inputs(expected=(0, 0, 66, 33), limit=33),  # TODO: update to LimitSoul function or similar
]


@classvar_matrix(matrix_vars=soul_restore_matrix)
class TestRestoreSpend(StateVarSetup, NoStepHK):
    key = "$SSM"
    matrix_vars: inputs
    expected: tuple[int, int, int, int]
    limit: int = 0

    def setUp(self):
        super().setUp()
        self.resource = self.matrix_vars.resource
        self.cs = self.matrix_vars.cs
        self.prep_vars = self.matrix_vars.prep_vars

        assert self.matrix_vars.expected is not None
        self.expected = self.matrix_vars.expected
        self.limit = self.matrix_vars.limit

    def test_restore_soul(self):
        rs, cs, pi = self.get_initialized_args()
        manager = self.get_handler()

        if limit:
            rs = manager.limit_soul(rs, cs, pi, limit)

        rs = get_one_state(manager.spend_soul, rs, cs, pi, 66)
        rs = get_one_state(manager.restore_all_soul, rs, cs, pi, True)
        self.assertEqual((
                    s["SPENTSOUL"],
                    s["SPENTRESERVESOUL"],
                    s["REQUIREDMAXSOUL"],
                    s["SOULLIMITER"],
                ), self.expected)

        rs = get_one_state(manager.spend_all_soul, rs, cs, pi)
        rs = get_one_state(manager.restore_all_soul, rs, cs, pi, True)
        self.assertEqual((
                    s["SPENTSOUL"],
                    s["SPENTRESERVESOUL"],
                    s["REQUIREDMAXSOUL"],
                    s["SOULLIMITER"],
                ), (
                self.expected[0],
                self.expected[1],
                manager.get_soul_info(rs, cs, pi).max_soul,
                self.expected[3],
                ))


soul_round_matrix = [
    inputs(expected=(33, 0, 33, 0)),
    inputs(cs={"Vessel_Fragment": 3}, expected=(0, 33, 33, 0)),
    inputs(expected=None, spend=67),  # TODO: update to LimitSoul function or similar
]


@classvar_matrix(matrix_vars=soul_round_matrix)
class TestRoundSpend(StateVarSetup, NoStepHK):
    key = "$SSM"
    matrix_vars: inputs
    expected: tuple[int, int, int, int] | None
    spend: int = 0

    def setUp(self):
        super().setUp()
        self.resource = self.matrix_vars.resource
        self.cs = self.matrix_vars.cs
        self.prep_vars = self.matrix_vars.prep_vars

        self.expected = self.matrix_vars.expected
        self.spend = self.matrix_vars.spend

    def test_round_spend(self):
        rs, cs, pi = self.get_initialized_args()
        manager = self.get_handler()

        if spend:
            rs = get_one_state(manager.spend_soul, rs, cs, pi, spend)
            rs = get_one_state(manager.restore_all_soul, rs, cs, pi, True)

        rs = get_one_state(manager.limit_soul, rs, cs, pi, 33, True)
        if expected is None:
            assert not manager.limit_soul(rs, cs, pi, 0, False)
        else:
            rs = get_one_state(manager.limit_soul, rs, cs, pi, 0, False)
            self.assertEqual((
                        s["SPENTSOUL"],
                        s["SPENTRESERVESOUL"],
                        s["REQUIREDMAXSOUL"],
                        s["SOULLIMITER"],
                    ), self.expected)


class TestHPManager(StateVarSetup, NoStepHK):
    key = "$HPSM"
    resource = {}
    cs = {}
    prep_vars = []

    def assert_spent_health(self, lazy: int, white: int, blue: int):
        healths = rs["LAZYSPENTHP"], rs["SPENTHP"], rs["SPENTBLUEHP"]
        self.assertEqual(healths, (lazy, white, blue), (
            f"Expected LAZYSPENTHP={'max' if lazy == HealthManager.max_damage else lazy}, "
            f"SPENTHP={white}, SPENTBLUEHP={blue}, but were {healths} instead."
        ))  # TODO make sure this isn't over-reporting info

    def test_strict_early(self):
        rs, cs, pi = self.get_initialized_args()
        manager = self.get_handler()

        rs = get_one_state(manager.determine_hp, rs, cs, pi)
        self.assert_spent_health(manager.max_damage, 0, 0)

        # TODO confirm what this assumption is right
        states = [s for s in manager.take_damage(rs, cs, pi, 1)]
        healths = sorted([(s["LAZYSPENTHP"], s["SPENTHP"], s["SPENTBLUEHP"])
                         for s in states])
        expected_healths = sorted([
            (manager.max_damage, 1, 0),
            (manager.max_damage, 2, 0)
        ])
        self.assertEqual(healths, expected_healths)

    def test_lazy_to_strict(self):
        rs, cs, pi = self.get_initialized_args()
        manager = self.get_handler()

        for i in range(1, 3):
            rs = get_one_state(manager.take_damage, rs, cs, pi, 1)
            self.assert_spent_health(i, 0, 0)
            assert not manager.is_hp_determined(rs), "HP was set to determined after lazy damage"
        for i in range(3, 5):
            rs = get_one_state(manager.take_damage, rs, cs, pi, 1)
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
