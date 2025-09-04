import unittest

from ..state_mixin import lt


class TestLT(unittest.TestCase):

    def test_one(self):
        state1 = {"a": 1}
        state2 = {"a": 2}
        outcome = True

        assert outcome == lt(state1, state2)

    def test_two(self):
        state1 = {"a": 1}
        state2 = {"a": 1, "b": 1}
        outcome = True

        assert outcome == lt(state1, state2)

    def test_three(self):
        state1 = {"a": 2}
        state2 = {"a": 1, "b": 1}
        outcome = False

        assert outcome == lt(state1, state2)

    # this case is irrelevant if we move to effectively le instead
    # def test_four(self):
    #     state1 = {"a": 2}
    #     state2 = {"a": 2}
    #     outcome = False

    #     assert outcome == lt(state1, state2)
