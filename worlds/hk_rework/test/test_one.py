import typing

from .bases import HKTestBase


class TestGoalAny(HKTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "Goal": "any",
    }
