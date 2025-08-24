from .bases import NoStepHK, StateVarSetup

from ..resource_state_vars.health_manager import HealthManager


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
        rs, cs = self.get_initialized_args()
        manager = self.get_handler()

        rs = self.get_one_state(manager.determine_hp, rs, cs)
        self.assert_spent_health(manager.max_damage, 0, 0)

        # TODO confirm what this assumption is right
        states = [s for s in manager.take_damage(rs, cs, 1)]
        healths = sorted([(s["LAZYSPENTHP"], s["SPENTHP"], s["SPENTBLUEHP"])
                         for s in states])
        expected_healths = sorted([
            (manager.max_damage, 1, 0),
            (manager.max_damage, 2, 0)
        ])
        self.assertEqual(healths, expected_healths)

    def test_lazy_to_strict(self):
        rs, cs = self.get_initialized_args()
        manager = self.get_handler()

        for i in range(1, 3):
            rs = self.get_one_state(manager.take_damage, rs, cs, 1)
            self.assert_spent_health(i, 0, 0)
            assert not manager.is_hp_determined(rs), "HP was set to determined after lazy damage"
        for i in range(3, 5):
            rs = self.get_one_state(manager.take_damage, rs, cs, 1)
            self.assert_spent_health(manager.max_damage, i, 0)
            assert manager.is_hp_determined(rs), "HP was not set to determined after taking too much lazy damage"
        rs = [s for s in manager.take_damage(rs, cs, 1)]
        assert not rs, "States were returned after taking enough damage to kill"


class TestJoniHP(StateVarSetup, NoStepHK):
    key = "$HPSM"
    resource = {"NOPASSEDCHARMEQUIP": 0, "NOFLOWER": 0, "NOTCHES": 4, "CANNOTOVERCHARM": 1}
    cs = {"Joni's_Blessing": 1}
    prep_vars = ["$EQUIPPEDCHARM[Joni's_Blessing]"]

    def test_joni_info(self):
        rs, cs = self.get_initialized_args()
        manager = self.get_handler()

        rs = manager.determine_hp(rs, cs)
        hp = manager.get_hp_info(rs, cs)
        assert hp.max_white_hp == 7, f"Expected Max White HP to be 7 but was {hp.max_white_hp}"
        assert hp.current_white_hp == 7, f"Expected Current White HP to be 7 but was {hp.current_white_hp}"
        assert hp.current_blue_hp == 7, f"Expected Current Blue HP to be 7 but was {hp.current_blue_hp}"
