from typing import Iterable, NamedTuple

from test.param import classvar_matrix

from .bases import NoStepHK, StateVarSetup

# TODO: add skipped when tests for state vars with required option values


class inputs(NamedTuple):
    key: str | None = None
    resource: dict[str, int] = {}
    cs: dict[str, int] = {}
    prep_vars: Iterable[str] = ()
    assert_empty: bool = False
    notches: int | None = None


ers = {"NOPASSEDCHARMEQUIP": 0, "NOFLOWER": 0}  # Empty Resource State
one_mask = {"MASKSHARDS": 4}
two_mask = {"MASKSHARDS": 8}

shrogo = {"Monarch_Wings": 1, "Abyss_Shriek": 2}  # include options
slobo = {"Vengeful_Spirit": 1}  # include options

input_matrix = [
    inputs("FOO=0"),
    inputs("$SHADESKIP", cs={"King_Fragment": 1, "Queen_Fragment": 1}, assert_empty=True),

    inputs("$CASTSPELL[3]"),
    inputs("$CASTSPELL[3]", prep_vars=("$SHADESKIP",), assert_empty=True),
    inputs("$CASTSPELL[4]", cs={"Vessel_Fragment": 3}, assert_empty=True),
    inputs("$CASTSPELL[4]", resource={"NOPASSEDCHARMEQUIP": 0}, cs={"Spell_Twister": 1}, notches=6),
    inputs("$CASTSPELL[3,1]", cs={"Vessel_Fragment": 3}),

    inputs("$LIFEBLOOD", resource=ers, assert_empty=True),
    *[inputs("$LIFEBLOOD", resource=ers, cs={charm: 1}, notches=4)
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
    inputs("$SHADESKIP[2HITS]", resource=two_mask, notches=6,
           cs={"Can_Repair_Fragile_Charms": 1, "Fragile_Heart": 1}),
    inputs("$SHADESKIP[2HITS]", resource=two_mask, notches=6,
           cs={"Unbreakable_Strength": 1, "Fragile_Heart": 1}),
    inputs("$SHADESKIP[2HITS]", resource={**two_mask, "BROKEHEART": 1}, notches=6,
           cs={"Can_Repair_Fragile_Charms": 1, "Fragile_Heart": 1}, assert_empty=True),

    inputs("$SHRIEKPOGO", assert_empty=True),  # with and without option on
    inputs("$SHRIEKPOGO", assert_empty=True, cs={"Monarch_Wings": 1}),
    inputs("$SHRIEKPOGO", assert_empty=True, cs={"Abyss_Shriek": 2}),

    inputs("$SHRIEKPOGO[3]",   cs=shrogo),
    inputs("$SHRIEKPOGO[4]",   cs=shrogo, assert_empty=True),  # Difficult skips
    inputs("$SHRIEKPOGO[4]",   cs={**shrogo, "Spell_Twister": 1}, resource={**ers, "DIFFICULTSKIPS": 1}, notches=6),  # Difficult skips
    inputs("$SHRIEKPOGO[4]",   cs={**shrogo, "Spell_Twister": 1}, resource=ers, notches=6, assert_empty=True),  # Difficult skips off
    inputs("$SHRIEKPOGO[4]",   cs={**shrogo, "Vessel_Fragment": 3}, assert_empty=True),  # Difficult skips
    inputs("$SHRIEKPOGO[3,1]", cs={**shrogo, "Vessel_Fragment": 3}),  # Difficult skips
    inputs("$SHRIEKPOGO[4]",   cs={**shrogo, "Vessel_Fragment": 3, "Mothwing_Cloak": 1}),  # Difficult skips

    inputs("$SLOPEBALL", assert_empty=True),  # with and without option on
    inputs("$SLOPEBALL", assert_empty=True, cs=slobo, resource={"SPENTSOUL": 99}),
    inputs("$SLOPEBALL", cs=slobo),

    inputs("$TAKEDAMAGE", assert_empty=True,  resource=one_mask),
    inputs("$TAKEDAMAGE", assert_empty=False, resource=two_mask),
    inputs("$TAKEDAMAGE", assert_empty=True,  resource=two_mask, prep_vars=("$TAKEDAMAGE",)),
    inputs("$TAKEDAMAGE", assert_empty=False, resource=two_mask, prep_vars=("$TAKEDAMAGE",), cs={"FOCUS": 1}),
    inputs("$TAKEDAMAGE", assert_empty=False, resource=one_mask, prep_vars=("$TAKEDAMAGE",), notches=6,
           cs={"Lifeblood_Heart": 1}),
    inputs("$TAKEDAMAGE", assert_empty=True,  resource=one_mask, prep_vars=("$TAKEDAMAGE",), notches=1,
           cs={"Lifeblood_Heart": 1}),
    inputs("$TAKEDAMAGE", assert_empty=False, resource=two_mask, prep_vars=("$TAKEDAMAGE[2]",), notches=6,
           cs={"Lifeblood_Heart": 1}),
    inputs("$TAKEDAMAGE[2]", assert_empty=True, resource=two_mask, prep_vars=("$TAKEDAMAGE",), notches=6,
           cs={"Lifeblood_Heart": 1}),
    inputs("$TAKEDAMAGE", assert_empty=False, resource={"MASKSHARDS": 12}, prep_vars=("$TAKEDAMAGE",), notches=1,
           cs={"Lifeblood_Heart": 1}),
    inputs("$TAKEDAMAGE", assert_empty=False, resource=one_mask, prep_vars=("$TAKEDAMAGE",), notches=6,
           cs={"Lifeblood_Heart": 1}),  # duplicate?
    inputs("$TAKEDAMAGE", assert_empty=True,  resource=one_mask, prep_vars=("$TAKEDAMAGE",), notches=1,
           cs={"Lifeblood_Heart": 1}),  # another?
    inputs("$TAKEDAMAGE", assert_empty=False, resource=two_mask, prep_vars=("$TAKEDAMAGE",), notches=6,
           cs={"Hiveblood": 1}),
    inputs("$TAKEDAMAGE", assert_empty=False, resource={"MASKSHARDS": 12}, notches=6,
           prep_vars=("$TAKEDAMAGE", "$TAKEDAMAGE", "$TAKEDAMAGE",), cs={"Deep_Focus": 1, "FOCUS": 1}),
    inputs("$TAKEDAMAGE", assert_empty=True,  resource={"MASKSHARDS": 12}, notches=6,
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
        self.notch_override = self.matrix_vars.notches

        self.assert_empty = self.matrix_vars.assert_empty

    def test_output(self):
        outputs = self.get_modified_state()
        if self.assert_empty:
            self.assertFalse(outputs, "Expected to not be in logic but was")
        else:
            self.assertTrue(outputs, "Expected to be in logic but was not")
