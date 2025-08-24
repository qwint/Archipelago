from typing import Iterable, NamedTuple

from test.param import classvar_matrix

from .bases import NoStepHK, StateVarSetup


class inputs(NamedTuple):
    key: str | None = None
    resource: dict[str, int] = {}
    cs: dict[str, int] = {}
    prep_vars: Iterable[str] = ()

    expecteds: Iterable[Iterable[tuple[int, int, int, int]]] = ()
    expected: tuple[int, int, int, int] | None = None
    limit: int = 0
    spend: int = 0


soul_spend_matrix = [
    inputs(resource={"NOPASSEDCHARMEQUIP": 0, "NOFLOWER": 0},
           expecteds=[[(33, 0, 33, 0)], [(66, 0, 66, 0)], [(99, 0, 99, 0)], []]),
    inputs(resource={"NOPASSEDCHARMEQUIP": 0, "NOFLOWER": 0}, cs={"Vessel_Fragment": 3},
           expecteds=[[(0, 33, 33, 0)], [(33, 33, 33, 0)], [(66, 33, 66, 0)], [(99, 33, 99, 0)], []]),
    inputs(resource={"NOPASSEDCHARMEQUIP": 0, "NOFLOWER": 0, "SOULLIMITER": 33},
           expecteds=[[(33, 0, 33, 33)], [(66, 0, 66, 33)], []], limit=33),
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
        rs, cs = self.get_initialized_args()
        manager = self.get_handler()

        if limit:
            rs = manager.limit_soul(rs, cs, limit, True)

        for i, expected in enumerate(self.expecteds):
            outputs = [s for s in manager.modify_state(rs, cs)]
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
        rs, cs = self.get_initialized_args()
        manager = self.get_handler()

        if limit:
            rs = manager.limit_soul(rs, cs, limit)

        rs = self.get_one_state(manager.spend_soul, rs, cs, 66)
        rs = self.get_one_state(manager.restore_all_soul, rs, cs, True)
        self.assertEqual((
                    s["SPENTSOUL"],
                    s["SPENTRESERVESOUL"],
                    s["REQUIREDMAXSOUL"],
                    s["SOULLIMITER"],
                ), self.expected)

        rs = self.get_one_state(manager.spend_all_soul, rs, cs)
        rs = self.get_one_state(manager.restore_all_soul, rs, cs, True)
        self.assertEqual((
                    s["SPENTSOUL"],
                    s["SPENTRESERVESOUL"],
                    s["REQUIREDMAXSOUL"],
                    s["SOULLIMITER"],
                ), (
                self.expected[0],
                self.expected[1],
                manager.get_soul_info(rs, cs).max_soul,
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
        rs, cs = self.get_initialized_args()
        manager = self.get_handler()

        if spend:
            rs = self.get_one_state(manager.spend_soul, rs, cs, spend)
            rs = self.get_one_state(manager.restore_all_soul, rs, cs, True)

        rs = self.get_one_state(manager.limit_soul, rs, cs, 33, True)
        if expected is None:
            assert not manager.limit_soul(rs, cs, 0, False)
        else:
            rs = self.get_one_state(manager.limit_soul, rs, cs, 0, False)
            self.assertEqual((
                        s["SPENTSOUL"],
                        s["SPENTRESERVESOUL"],
                        s["REQUIREDMAXSOUL"],
                        s["SOULLIMITER"],
                    ), self.expected)
