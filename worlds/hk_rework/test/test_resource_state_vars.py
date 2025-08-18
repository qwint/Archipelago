from collections import Counter
from typing import Iterable, NamedTuple

from BaseClasses import CollectionState
from test.param import classvar_matrix

from .bases import NoStepHK
from ..resource_state_vars import ResourceStateHandler


class inputs(NamedTuple):
    key: str
    resource: dict[str, int] = {}
    cs: dict[str, int] = {}
    assert_empty: bool = False
    prep_vars: Iterable[str] = ()
    expecteds: Iterable[Iterable[tuple[int, int, int, int]]] = ()


class StateVarSetup:
    matrix_vars: inputs
    key: str
    resource: dict[str, int]
    cs: dict[str, int]
    assert_empty: bool
    prep_vars: Iterable[str]

    def setUp(self):
        super().setUp()
        self.key = self.matrix_vars.key
        self.resource = self.matrix_vars.resource
        self.cs = self.matrix_vars.cs
        self.assert_empty = self.matrix_vars.assert_empty
        self.prep_vars = self.matrix_vars.prep_vars

    def get_modify_args(self) -> tuple[Counter, CollectionState, int]:
        state = CollectionState(self.multiworld)
        for item, i in self.cs.items():
            # assert item in self.world.item_name_to_id, f"Unknown item collected {item}"
            for _ in range(i):
                state.collect(self.world.create_item(item))
        return Counter(self.resource), state, self.player

    def get_modified_state(self):
        args = self.get_modify_args()
        if self.prep_vars:
            for prep in self.prep_vars:
                rs = next(ResourceStateHandler.get_handler(prep).modify_state(rs, cs, pi))
            args = rs, cs, pi

        handler = ResourceStateHandler.get_handler(self.key)
        return [s for s in handler.modify_state(*args)]


ers = {"NOPASSEDCHARMEQUIP": 0, "NOFLOWER": 0}  # Empty Resource State


input_matrix = [
    inputs("FOO=0"),
    # inputs("$SHADESKIP", cs={"King_Fragment": 1, "Queen_Fragment": 1}, assert_empty=True),

    # inputs("$CASTSPELL[3]"),
    # inputs("$CASTSPELL[3]", prep_vars=("$SHADESKIP",), assert_empty=True),
    # inputs("$CASTSPELL[4]", cs={"Vessel_Fragment": 3}, assert_empty=True),
    # inputs("$CASTSPELL[4]", resource={"NOPASSEDCHARMEQUIP": 0, "NOTCHES": 6}, cs={"Spell_Twister": 1}),
    # inputs("$CASTSPELL[3,1]", cs={"Vessel_Fragment": 3}),

    # # TODO, add tests for equip charm and hp state

    # inputs("$LIFEBLOOD", resource=ers, assert_empty=True),
    # *[inputs("$LIFEBLOOD", resource={**ers, "NOTCHES": 4}, cs={charm: 1}) for charm in ("Lifeblood_Heart", "Lifeblood_Core", "Joni's_Blessing")],
    # inputs("$LIFEBLOOD", resource=ers, cs={"Lifeblood_Heart": 1}, assert_empty=True, prep_vars=("$TAKEDAMAGE[2]",)),
    # *[inputs("$LIFEBLOOD", resource=ers, cs={charm: 1}, prep_vars=("$TAKEDAMAGE[2]",)) for charm in ("Lifeblood_Core", "Joni's_Blessing")],

    # # inputs("$SHADESKIP", assert_empty=True),  # theoretically checking if the option is disabled but idk
    # inputs("$SHADESKIP", resource={"USEDSHADE": 1}, assert_empty=True),
    # inputs("$SHADESKIP", resource={"CHARM36": 1}, assert_empty=True),
    # inputs("$SHADESKIP", resource={"REQUIREDMAXSOUL": 67}, assert_empty=True),
    # inputs("$SHADESKIP"),
    # inputs("$SHADESKIP[2HITS]", resource={"MASKSHARDS": 4}, assert_empty=True),  # TODO make sure that this aligns with how i set up damage state var in the future
    # inputs("$SHADESKIP[2HITS]", resource={"MASKSHARDS": 16}),
    # inputs("$SHADESKIP[2HITS]", resource={"MASKSHARDS": 8, "NOTCHES": 6}, cs={"Can_Repair_Fragile_Charms": 1, "Fragile_Heart": 1}),
    # inputs("$SHADESKIP[2HITS]", resource={"MASKSHARDS": 8, "NOTCHES": 6}, cs={"Unbreakable_Strength": 1, "Fragile_Heart": 1}),
    # inputs("$SHADESKIP[2HITS]", resource={"MASKSHARDS": 8, "NOTCHES": 6, "BROKEHEART": 1}, cs={"Can_Repair_Fragile_Charms": 1, "Fragile_Heart": 1}, assert_empty=True),

    # TODO, add shrogo, slopeball, soulstate, takedamage tests
]


@classvar_matrix(matrix_vars=input_matrix)
class TestStateVars(StateVarSetup, NoStepHK):
    def test_output(self):
        outputs = self.get_modified_state()
        if self.assert_empty:
            self.assertFalse(outputs, "Expected to not be in logic but was")
        else:
            self.assertTrue(outputs, "Expected to be in logic but was not")


soul_matrix = [
    inputs("$SPENDSOUL[33]", resource=ers, expecteds=[[(33, 0, 33, 0)], [(66, 0, 66, 0)], [(99, 0, 99, 0)], []]),
    inputs("$SPENDSOUL[33]", resource=ers, cs={"Vessel_Fragment": 3}, expecteds=[[(0, 33, 33, 0)], [(33, 33, 33, 0)], [(66, 33, 66, 0)], [(99, 33, 99, 0)], []]),
    inputs("$SPENDSOUL[33]", resource={**ers, "SOULLIMITER": 33}, expecteds=[[(33, 0, 33, 33)], [(66, 0, 66, 33)], []]),  # TODO: update to LimitSoul function or similar
]


@classvar_matrix(matrix_vars=soul_matrix)
class TestSoulManagement(StateVarSetup, NoStepHK):
    expecteds: Iterable[list[tuple[int, int, int, int]]]

    def setUp(self):
        super().setUp()
        self.expecteds = self.matrix_vars.expecteds

    def test_spend_soul(self):
        rs, cs, pi = self.get_modify_args()
        if self.prep_vars:
            for prep in self.prep_vars:
                rs = next(ResourceStateHandler.get_handler(prep).modify_state(rs, cs, pi))
        handler = ResourceStateHandler.get_handler(self.key)

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
