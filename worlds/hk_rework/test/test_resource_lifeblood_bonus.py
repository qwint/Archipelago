from typing import Iterable, NamedTuple

from test.param import classvar_matrix

from .bases import NoStepHK, StateVarSetup


class inputs(NamedTuple):
    key: str | None = None
    resource: dict[str, int] = {}
    cs: dict[str, int] = {}
    prep_vars: Iterable[str] = ()
    assert_empty: bool = False
    notches: int | None = None
    damage: int = 0


lifeblood_damage_matrix = [
    inputs("$LIFEBLOOD", resource={"NOPASSEDCHARMEQUIP": 0, "NOFLOWER": 0},
           cs={"Lifeblood_Heart": 1}, assert_empty=True, damage=2, notches=4),
    *[inputs("$LIFEBLOOD", resource={"NOPASSEDCHARMEQUIP": 0, "NOFLOWER": 0}, cs={charm: 1}, damage=2, notches=4)
      for charm in ("Lifeblood_Core", "Joni's_Blessing")],
]


@classvar_matrix(matrix_vars=lifeblood_damage_matrix)
class TestLifeblood(StateVarSetup, NoStepHK):
    matrix_vars: inputs
    assert_empty: bool
    damage: int

    def setUp(self):
        super().setUp()
        self.key = self.matrix_vars.key
        self.resource = self.matrix_vars.resource
        self.cs = self.matrix_vars.cs
        self.prep_vars = self.matrix_vars.prep_vars
        self.notch_override = self.matrix_vars.notches

        self.assert_empty = self.matrix_vars.assert_empty
        self.damage = self.matrix_vars.damage

    def test_output(self):
        rs, cs = self.get_initialized_args()
        handler = self.get_handler()
        damage_handler = self.get_handler("$TAKEDAMAGE")
        outputs = [rs]
        for _ in range(self.damage):
            outputs = [s for os in outputs for s in damage_handler.modify_state(os, cs)]

        outputs = [s for os in outputs for s in handler.modify_state(os, cs)]
        if self.assert_empty:
            self.assertFalse(outputs, "Expected to not be in logic but was")
        else:
            self.assertTrue(outputs, "Expected to be in logic but was not")
