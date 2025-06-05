import typing

from .bases import HKTestBase


class TestGoalAny(HKTestBase):
    """just for testing purposes, if you see this in the PR remind me to remove it lmao"""
    options: typing.ClassVar[dict[str, str]] = {
        "Goal": "any",
    }
