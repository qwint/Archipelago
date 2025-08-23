from typing import Iterable, NamedTuple

from test.param import classvar_matrix

from .bases import NoStepHK, StateVarSetup


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


class TestBasicEquips(StateVarSetup, NoStepHK):
    key = "$EQUIPPEDCHARM[Gathering_Swarm]"
    resource = {"NOTCHES": 1}
    cs = {"Gathering_Swarm": 1}
    prep_vars = []

    def test_basic_equip(self):
        # TODO update if i end up on a different return signature than tuple[bool, stateblob] for try_equip
        rs, cs, pi = self.get_initialized_args()
        handler = self.get_handler()

        self.assertFalse(handler.try_equip(rs, cs, pi)[0])  
        self.assertFalse(handler.is_equipped(rs, cs, pi))
        self.assertEqual(rs["USEDNOTCHES"], 0)
        self.assertEqual(rs["MAXNOTCHCOST"], 0)

        resource["NOPASSEDCHARMEQUIP"] = 0
        res_bool, res_state = handler.try_equip(rs, cs, pi)
        self.assertTrue(res_bool)
        # test original state
        self.assertFalse(handler.is_equipped(rs, cs, pi))
        self.assertEqual(rs["USEDNOTCHES"], 0)
        self.assertEqual(rs["MAXNOTCHCOST"], 0)
        # test output state
        self.assertTrue(handler.is_equipped(res_state, cs, pi))
        self.assertEqual(res_state["USEDNOTCHES"], 1)
        self.assertEqual(res_state["MAXNOTCHCOST"], 1)

        other = rs.copy()  # for later

        handler.set_unequippable(rs, cs, pi)
        res_bool, res_state = handler.try_equip(rs, cs, pi)
        self.assertFalse(res_bool)
        self.assertEqual(res_state["USEDNOTCHES"], 0)
        self.assertEqual(res_state["MAXNOTCHCOST"], 0)

        other_bool, res_other = handler.try_equip(other, cs, pi)
        self.assertTrue(other_bool)
        self.assertEqual(res_other["USEDNOTCHES"], 1)
        self.assertEqual(res_other["MAXNOTCHCOST"], 1)

        other_bool, res_other = handler.try_equip(other, cs, pi)
        self.assertTrue(other_bool)
        self.assertEqual(res_other["USEDNOTCHES"], 1)
        self.assertEqual(res_other["MAXNOTCHCOST"], 1)


# equip_notch_matrix = [
#     inputs(expected=(33, 0, 33, 0)),
#     inputs(cs={"Vessel_Fragment": 3}, expected=(0, 33, 33, 0)),
#     inputs(expected=None, spend=67),  # TODO: update to LimitSoul function or similar
# ]


# @classvar_matrix(matrix_vars=equip_notch_matrix)
# class TestEquipNotch(StateVarSetup, NoStepHK):
#     matrix_vars: inputs
#     notches: int
#     notch_costs: list[int]
#     equip_results: list[bool]
#     ended_overcharmed: bool

#     def setUp(self):
#         super().setUp()
#         self.resource = self.matrix_vars.resource
#         self.cs = self.matrix_vars.cs
#         self.prep_vars = self.matrix_vars.prep_vars

#         self.expected = self.matrix_vars.expected
#         self.spend = self.matrix_vars.spend

    # def test_round_spend(self):
    #     rs, cs, pi = self.get_initialized_args()
    #     manager = self.get_handler()

    #     if spend:
    #         rs = self.get_one_state(manager.spend_soul, rs, cs, pi, spend)
    #         rs = self.get_one_state(manager.restore_all_soul, rs, cs, pi, True)

    #     rs = self.get_one_state(manager.limit_soul, rs, cs, pi, 33, True)
    #     if expected is None:
    #         assert not manager.limit_soul(rs, cs, pi, 0, False)
    #     else:
    #         rs = self.get_one_state(manager.limit_soul, rs, cs, pi, 0, False)
    #         self.assertEqual((
    #                     s["SPENTSOUL"],
    #                     s["SPENTRESERVESOUL"],
    #                     s["REQUIREDMAXSOUL"],
    #                     s["SOULLIMITER"],
    #                 ), self.expected)
