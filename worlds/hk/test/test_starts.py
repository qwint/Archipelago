from typing import ClassVar

from .bases import NoStepHK
from ..options import filtered_starts


class StartsBase:
    valid_starts: ClassVar[list[str]]
    invalid_starts: ClassVar[list[str]]

    def test_valid_starts(self):
        for start in self.valid_starts:
            with self.subTest(start=start):
                self.assertFalse(self.world.validate_start(start))

    def test_invalid_starts(self):
        for start in self.invalid_starts:
            with self.subTest(start=start):
                self.assertTrue(self.world.validate_start(start))


class TestSwimRandoStarts(StartsBase, NoStepHK):
    options = {
        "RandomizeSwim": "true",

        "EnemyPogos": "true",
    }
    valid_starts = []
    invalid_starts = ["kingdoms_edge"]


class TestSwimRandolessStarts(StartsBase, NoStepHK):
    options = {
        "RandomizeSwim": "false",

        "EnemyPogos": "true",
    }
    valid_starts = ["kingdoms_edge"]
    invalid_starts = []


class TestEnemyPogoStarts(StartsBase, NoStepHK):
    options = {
        "EnemyPogos": "true",

        "PreciseMovement": "false",
        "RandomizeSwim": "false",
        "DangerousSkips": "true",
        "ShadeSkips": "true",
    }
    valid_starts = ["mantis_village", "kingdoms_edge", "queens_gardens"]
    invalid_starts = ["west_waterways"]


class TestPreciseEnemyPogoStarts(StartsBase, NoStepHK):
    options = {
        "EnemyPogos": "true",
        "PreciseMovement": "true",

        "RandomizeSwim": "false",
        "DangerousSkips": "true",
        "ShadeSkips": "true",
    }
    valid_starts = ["mantis_village", "kingdoms_edge", "west_waterways", "queens_gardens"]
    invalid_starts = []


class TestEnemyPogolessStarts(StartsBase, NoStepHK):
    options = {
        "EnemyPogos": "false",

        "RandomizeSwim": "false",
        "DangerousSkips": "true",
        "ShadeSkips": "true",
    }
    valid_starts = []
    invalid_starts = ["mantis_village", "kingdoms_edge", "west_waterways", "queens_gardens"]


class testDarkroomStarts(StartsBase, NoStepHK):
    options = {
        "DarkRooms": "true",
    }
    valid_starts = ["hallownests_crown"]
    invalid_starts = []


class testDarkroomStarts(StartsBase, NoStepHK):
    options = {
        "DarkRooms": "false",
    }
    valid_starts = []
    invalid_starts = ["hallownests_crown"]
