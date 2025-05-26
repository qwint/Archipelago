import typing

from Options import ItemLinks
from test.bases import WorldTestBase

from .bases import LinkedTestHK


class TestGrubcountLimited(LinkedTestHK, WorldTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "RandomizeGrubs": True,
        "GrubHuntGoal": 20,
        "Goal": "any",
    }
    item_link_group: typing.ClassVar[list[dict[str, typing.Any]]] = [{
        "name": "ItemLinkTest",
        "item_pool": ["Grub"],
        "link_replacement": True,
        "replacement_item": "Grub",
    }]
    expected_grubs = 20


class TestGrubcountDefault(LinkedTestHK, WorldTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "RandomizeGrubs": True,
        "Goal": "any",
    }
    item_link_group: typing.ClassVar[list[dict[str, typing.Any]]] = [{
        "name": "ItemLinkTest",
        "item_pool": ["Grub"],
        "link_replacement": True,
        "replacement_item": "Grub",
    }]
    expected_grubs = 46


class TestGrubcountAllUnlinked(LinkedTestHK, WorldTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "RandomizeGrubs": True,
        "GrubHuntGoal": "all",
        "Goal": "any",
    }
    item_link_group: typing.ClassVar[list[dict[str, typing.Any]]] = []
    expected_grubs = 46


class TestGrubcountAllLinked(LinkedTestHK, WorldTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "RandomizeGrubs": True,
        "GrubHuntGoal": "all",
        "Goal": "any",
    }
    item_link_group: typing.ClassVar[list[dict[str, typing.Any]]] = [{
        "name": "ItemLinkTest",
        "item_pool": ["Grub"],
        "link_replacement": True,
        "replacement_item": "Grub",
    }]
    expected_grubs = 46 + 23


class TestReplacementOnly(LinkedTestHK, WorldTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "RandomizeGrubs": True,
        "GrubHuntGoal": "all",
        "Goal": "any",
    }
    expected_grubs = 46 + 18  # the count of grubs + skills removed from item links

    def setup_item_links(self, args):
        setattr(args, "item_links",
                {
                    1: ItemLinks.from_any([{
                        "name": "ItemLinkTest",
                        "item_pool": ["Skills"],
                        "link_replacement": True,
                        "replacement_item": "Grub",
                    }]),
                    2: ItemLinks.from_any([{
                        "name": "ItemLinkTest",
                        "item_pool": ["Skills"],
                        "link_replacement": True,
                        "replacement_item": "Grub",
                    }])
                })
        return args


class TestReplacementOnlyUnlinked(LinkedTestHK, WorldTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "RandomizeGrubs": True,
        "GrubHuntGoal": "all",
        "Goal": "any",
    }
    expected_grubs = 46 + 9  # Player1s replacement Grubs

    def setup_item_links(self, args):
        setattr(args, "item_links",
                {
                    1: ItemLinks.from_any([{
                        "name": "ItemLinkTest",
                        "item_pool": ["Skills"],
                        "link_replacement": False,
                        "replacement_item": "Grub",
                    }]),
                    2: ItemLinks.from_any([{
                        "name": "ItemLinkTest",
                        "item_pool": ["Skills"],
                        "link_replacement": False,
                        "replacement_item": "Grub",
                    }])
                })
        return args


class TestIgnoreOthers(LinkedTestHK, WorldTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "RandomizeGrubs": True,
        "GrubHuntGoal": "all",
        "Goal": "any",
    }
    # player2 has more than 46 grubs but they are unlinked so player1s grubs are vanilla
    expected_grubs = 46

    def setup_item_links(self, args):
        setattr(args, "item_links",
                {
                    1: ItemLinks.from_any([{
                        "name": "ItemLinkTest",
                        "item_pool": ["Skills"],
                        "link_replacement": False,
                        "replacement_item": "One_Geo",
                    }]),
                    2: ItemLinks.from_any([{
                        "name": "ItemLinkTest",
                        "item_pool": ["Skills"],
                        "link_replacement": False,
                        "replacement_item": "Grub",
                    }])
                })
        return args


class TestReplacementOnlyLinked(LinkedTestHK, WorldTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "RandomizeGrubs": True,
        "GrubHuntGoal": "all",
        "Goal": "any",
    }
    expected_grubs = 46 + 9  # Player2s linkreplacement grubs

    def setup_item_links(self, args):
        setattr(args, "item_links",
                {
                    1: ItemLinks.from_any([{
                        "name": "ItemLinkTest",
                        "item_pool": ["Skills"],
                        "link_replacement": True,
                        "replacement_item": "One_Geo",
                    }]),
                    2: ItemLinks.from_any([{
                        "name": "ItemLinkTest",
                        "item_pool": ["Skills"],
                        "link_replacement": True,
                        "replacement_item": "Grub",
                    }])
                })
        return args
