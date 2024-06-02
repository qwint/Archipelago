
from . import AWTestBase
from ..names import ItemNames as iname, LocationNames as lname

from test.bases import WorldTestBase


# class AWTestBase(WorldTestBase):
#     game = "ANIMAL WELL"
#     player = 1


class TestAccess(AWTestBase):
    # test that you can't get to the B. Ball chest until you have the K. Shards or the Ball
    def test_bball_access(self) -> None:
        self.collect_all_but([iname.ball, iname.k_shard])
        self.assertFalse(self.can_reach_location(lname.b_ball_chest))
        self.collect_by_name([iname.k_shard])
        self.assertTrue(self.can_reach_location(lname.b_ball_chest))


class TestBunnyAccess(AWTestBase):
    options = {
        "bunnies_as_checks": "all_bunnies"
    }

    # test that the B.B. Wand event functions properly
    def test_bubble_long(self) -> None:
        self.collect_all_but([iname.bubble, iname.bubble_long]),
        self.assertFalse(self.can_reach_location(lname.bunny_water_spike))
        self.collect_by_name([iname.bubble]),
        self.assertTrue(self.can_reach_location(lname.bunny_water_spike))
