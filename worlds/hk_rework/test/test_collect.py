import unittest
from worlds.AutoWorld import AutoWorldRegister
from test.general import setup_solo_multiworld
from .. import HKWorld


class TestBase(unittest.TestCase):
    def testCollect(self):
        game_name, world_type = "Hollow Knight", HKWorld
        multiworld = setup_solo_multiworld(world_type)
        proxy_world = multiworld.worlds[1]
        empty_state = multiworld.state.copy()

        for item_name in world_type.item_name_to_id:
            with self.subTest("Create Item", item_name=item_name, game_name=game_name):
                item = proxy_world.create_item(item_name)

            with self.subTest("Item Name", item_name=item_name, game_name=game_name):
                self.assertEqual(item.name, item_name)

            if item.advancement:
                with self.subTest("Item State Collect", item_name=item_name, game_name=game_name):
                    multiworld.state.collect(item, True)

                with self.subTest("Item State Remove", item_name=item_name, game_name=game_name):
                    multiworld.state.remove(item)

                    self.assertEqual(multiworld.state.prog_items, empty_state.prog_items,
                                     "Item Collect -> Remove should restore empty state.")
            else:
                with self.subTest("Item State Collect No Change", item_name=item_name, game_name=game_name):
                    # Non-Advancement should not modify state.
                    base_state = multiworld.state.prog_items.copy()
                    multiworld.state.collect(item)
                    self.assertEqual(base_state, multiworld.state.prog_items)

            multiworld.state.prog_items = empty_state.prog_items

    def testCollect_split_cloak(self):
        game_name, world_type = "Hollow Knight", HKWorld
        multiworld = setup_solo_multiworld(world_type)
        proxy_world = multiworld.worlds[1]
        empty_state = multiworld.state.copy()

        l_cloaks = ["Left_Mothwing_Cloak", "Right_Mothwing_Cloak", "Left_Mothwing_Cloak"]
        r_cloaks = ["Left_Mothwing_Cloak", "Right_Mothwing_Cloak", "Right_Mothwing_Cloak"]
        for cloaks in [l_cloaks, r_cloaks]:
            items = []
            for item_name in cloaks:
                with self.subTest("Create Item", item_name=item_name, game_name=game_name):
                    item = proxy_world.create_item(item_name)
                    items.append(item)

                with self.subTest("Item Name", item_name=item_name, game_name=game_name):
                    self.assertEqual(item.name, item_name)

                if item.advancement:
                    with self.subTest("Item State Collect", item_name=item_name, game_name=game_name):
                        multiworld.state.collect(item, True)
            proxy_world.random.shuffle(items)
            for item in items:
                with self.subTest("Item State Remove", item_name=item_name, game_name=game_name):
                    multiworld.state.remove(item)

            self.assertEqual(multiworld.state.prog_items, empty_state.prog_items,
                             f"Item Collect -> Remove should restore empty state.\n{multiworld.state.prog_items}\n\n{empty_state.prog_items}")

            multiworld.state.prog_items = empty_state.prog_items
