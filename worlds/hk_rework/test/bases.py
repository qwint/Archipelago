import typing
from argparse import Namespace

from BaseClasses import CollectionState, MultiWorld
from Options import ItemLinks
from test.bases import WorldTestBase
from worlds.AutoWorld import AutoWorldRegister, call_all

from .. import HKWorld


class HKTestBase(WorldTestBase):
    game = "Hollow Knight"
    world: HKWorld

    # def assert_access_independency(
    #         self,
    #         locations: list[str],
    #         possible_items: typing.Iterable[typing.Iterable[str]],
    #         only_check_listed: bool = False) -> None:
    #     """Asserts that the provided locations can't be reached without
    #     the listed items but can be reached with any
    #     one of the provided combinations"""
    #     all_items = [
    #         item_name for
    #         item_names in
    #         possible_items for
    #         item_name in
    #         item_names
    #         ]

    #     state = CollectionState(self.multiworld)

    #     for item_names in possible_items:
    #         items = self.get_items_by_name(item_names)
    #         for item in items:
    #             self.collect_all_but(item.name)
    #         for location in locations:
    #             self.assertTrue(state.can_reach(location, "Location", 1),
    #                             f"{location} not reachable with {item_names}")
    #         for item in items:
    #             state.remove(item)

    # def assert_access_without(
    #         self,
    #         locations: list[str],
    #         possible_items: typing.Iterable[typing.Iterable[str]]) -> None:
    #     """Asserts that the provided locations can't be reached without the
    #     listed items but can be reached with any
    #     one of the provided combinations"""
    #     all_items = [
    #         item_name for
    #         item_names in
    #         possible_items for
    #         item_name in
    #         item_names
    #         ]

    #     state = CollectionState(self.multiworld)
    #     self.collect_all_but(all_items, state)
    #     for location in locations:
    #         self.assertTrue(
    #             state.can_reach(location, "Location", 1),
    #             f"{location} is not reachable without {all_items}")


class SelectSeedHK(WorldTestBase):
    game = "Hollow Knight"
    # player: typing.ClassVar[int] = 1
    seed = 0
    world: HKWorld

    def world_setup(self, *args, **kwargs):
        super().world_setup(self.seed)


class LinkedTestHK:
    run_default_tests = False
    game = "Hollow Knight"
    world: HKWorld
    expected_grubs: int
    item_link_group: list[dict[str, typing.Any]]

    def setup_item_links(self, args):
        setattr(args, "item_links",
                {
                    1: ItemLinks.from_any(self.item_link_group),
                    2: ItemLinks.from_any([{
                        "name": "ItemLinkTest",
                        "item_pool": ["Grub"],
                        "link_replacement": False,
                        "replacement_item": "One_Geo",
                    }])
                })
        return args

    def world_setup(self) -> None:
        """
        Create a multiworld with two players that share an itemlink
        """
        self.multiworld = MultiWorld(2)
        self.multiworld.game = {1: self.game, 2: self.game}
        self.multiworld.player_name = {1: "Linker 1", 2: "Linker 2"}
        self.multiworld.set_seed()
        args = Namespace()
        options_dataclass = AutoWorldRegister.world_types[self.game].options_dataclass
        for name, option in options_dataclass.type_hints.items():
            setattr(args, name, {
                1: option.from_any(self.options.get(name, option.default)),
                2: option.from_any(self.options.get(name, option.default))
            })
        args = self.setup_item_links(args)
        self.multiworld.set_options(args)
        self.multiworld.set_item_links()
        # groups get added to state during its constructor so this has to be after item links are set
        self.multiworld.state = CollectionState(self.multiworld)
        gen_steps = ("generate_early", "create_regions", "create_items", "set_rules", "generate_basic")
        for step in gen_steps:
            call_all(self.multiworld, step)
        # link the items together and stop at prefill
        self.multiworld.link_items()
        self.multiworld._all_state = None
        call_all(self.multiworld, "pre_fill")

        self.world = self.multiworld.worlds[self.player]

    def test_grub_count(self) -> None:
        assert self.world.grub_count == self.expected_grubs, \
               f"Expected {self.expected_grubs} but found {self.world.grub_count}"
