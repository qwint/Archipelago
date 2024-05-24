from typing import Dict, List, NamedTuple
from enum import IntEnum
from .names import item_names as iname, location_names as lname


# makes it more convenient to put together imo
class AWType(IntEnum):
    location = 1
    region = 2


class AWData(NamedTuple):
    type: int  # location or region
    rules: List[List[str]] = []  # how to access it
    # the rules are formatted such that [[wand], [disc, remote]] means you need wand OR you need disc + remote


# region names
fast_travel_fake = "Fast Travel Mid-Warp"  # for the purpose of not putting all the entrances at the starting region
starting_area = "Squirrel Main"
s_disc_area = "Squirrel S. Disc Area"
starting_after_ghost = "Squirrel After Ghost"
fast_travel = "Fast Travel Room"
fast_travel_fish_teleport = "Fast Travel Fish Teleport Spot"
bird_area = "Bird Area"  # the central portion of the map
bird_capybara_waterfall = "Bird Capybara Waterfall"  # up and right of the ladder
bird_below_mouse_statues = "Bird Below Mouse Statues"  # on the way to frog area, need yoyo
bird_planet_egg_spot = "Bird Planet Egg Spot"
candle_area = "Squirrel Candle Area"

fish_upper = "Fish Upper"  # everything prior to the bubble wand chest
fish_lower = "Fish Lower"
fish_boss_1 = "Fish Boss Arena Part 1"  # just the whale
fish_boss_2 = "Fish Boss Arena Part 2"  # whale + seahorse
fish_wand_pit = "Fish B.Wand Chest Pit"
fish_west = "Fish Warp Room"  # after the b. wand chest, rename
fish_tube_room = "Fish Pipe Maze"  # rename?

abyss = "Bone Fish Area"
uv_lantern_spot = "UV Lantern Spot"

bear_area_entry = "Bear Main Entry"
bear_capybara_and_below = "Bear Main Area"
bear_future_egg_room = "Bear Future Egg Room"
bear_chinchilla_song_room = "Bear Chinchilla Song Room"  # where the bunny is
bear_dark_maze = "Bear Dark Maze"
bear_chameleon_room_1 = "Bear Chameleon Room 1"  # first chameleon encounter with the chinchilla
bear_ladder_after_chameleon = "Bear Ladder after Chameleon 1"
bear_slink_room = "Bear Slink Room"  # the room you get slink
bear_transcendental = "Bear Transcendental Egg Room"
bear_kangaroo_waterfall = "Bear Kangaroo Waterfall and adjacent rooms"  # up left from entry point, need slink
bear_middle_phone_room = "Bear Middle Phone Room"  # after the previous region, has the fast travel, monkey room
bear_crow_rooms = "Bear Crow Rooms"  # the room with a lot of crows, the room with 8 crows, and the room with 4 crows
bear_shadow_egg_spot = "Bear Shadow Egg Chest Spot"  # since you can get here from above with top
bear_hedgehog_square = "Bear Hedgehog on the Square Room"  # the one where the hedgehog presses 4 buttons
bear_connector_passage = "Bear Connector Passage"  # connects capybara save room, upper bear
bear_match_chest_spot = "Bear Match Chest Spot"  # where the match chest is, it's weird okay
bear_upper_phone_room = "Bear Upper Phone Room"
bear_above_chameleon = "Bear Above Chameleon Boss"  # right above the chameleon boss before the flame
bear_chameleon_room_2 = "Bear Chameleon Boss Room before Flame"
bear_razzle_egg_spot = "Bear Razzle Egg Spot"
bear_truth_egg_spot = "Bear Truth Egg Spot"

dog_area = "Dog Main"
dog_chinchilla_skull = "Dog Chinchilla Skull Room"
dog_at_mock_disc = "Dog at Mock Disc Chest"
dog_upper = "Dog Area Upper"  # rename this variable and name
dog_upper_past_lake = "Dog Area Upper past Lake"
dog_upper_above_switch_lines = "Dog Area Upper above Switch Lines"  # rename, that spot where you go up the levels?
dog_upper_above_switch_lines_to_upper_east = "Dog Area Upper above Switch Lines to Upper East"  # where the button is
dog_upper_east = "Dog Area Upper East"  # to the right of the area above the switch lines
bobcat_room = "Bobcat Room"
chest_on_spikes_region = "Chest on Spikes Region"
dog_elevator = "Dog Elevator"  # east of the flame
dog_many_switches = "Dog Switches and Bat"  # west of spike room
dog_upside_down_egg_spot = "Dog Upside Down Egg Spot"
dog_bat_room = "Dog Bat Room"
dog_under_fast_travel_room = "Dog Room under Fast Travel Door Room"
dog_fast_travel_room = "Dog Room with Fast Travel Door"
dog_swordfish_lake_ledge = "Dog Left side of Swordfish Lake"
behind_kangaroo = "Vertical Passage behind Kangaroo Room"
dog_above_fast_travel = "Dog Above Fast Travel Room"  # has some of those breakout blocks
dog_mock_disc_shrine = "Dog Mock Disc Shrine"  # and the rooms to the left of it
kangaroo_room = "Kangaroo Room"
kangaroo_blocks = "Kangaroo Room Blocks"
dog_wheel = "Dog Wheel"  # doggo getting swole af
dog_elevator_upper = "Dog Elevator Upper"  # top of the elevator going up

frog_near_wombat = "Frog Area near Groundhog"  # first part of the frog area after you drop down the hole
frog_under_ostrich_statue = "Frog Area under Ostrich Statue"  # just the dark room basically
frog_pre_ostrich_attack = "Frog before Ostrich Attack"  # left of dark room, right of ostrich, above dynamite
frog_ostrich_attack = "Frog Ostrich Attack"  # and also the little area above it
frog_worm_shaft_top = "Frog Worm Shaft Top"  # where the fire egg is
frog_worm_shaft_bottom = "Frog Worm Shaft Bottom"  # save point after ostrich chase
frog_bird_after_yoyo_1 = "Frog Bird Area after Yoyo 1"  # the first two bird rooms after you get yoyo
frog_bird_after_yoyo_2 = "Frog Bird Area after Yoyo 2"  # the area after the previous one (rewrite comment)
frog_dark_room = "Wave Room"  # the dark room with the frog, and also the wave room
frog_ruby_egg_ledge = "Ruby Egg Ledge"  # the ledge with the ruby egg in the frog dark room
frog_east_of_fast_travel = "Frog East of Fast Travel"  # one screen to the right of the fast travel spot
frog_elevator_and_ostrich_wheel = "Frog Elevator and Ostrich Wheel Section"  # interdependent, so one big region
frog_travel_egg_spot = "Frog Travel Egg Spot"

hippo_entry = "Hippo Entry"  # the beginning of the end
hippo_manticore_room = "Hippo Manticore Room"  # the 4 rooms you evade the manticore in for the first ending
hippo_skull_room = "Hippo Skull Room"  # B. B. Wand and the skull pile
hippo_fireworks = "Hippo Fireworks Room"  # the first ending

home = "Home"
barcode_bunny = "Barcode Bunny"  # barcode bunny is gotten in two places
top_of_the_well = "Top of the Well"  # where the warp song takes you, right of the house
chocolate_egg_spot = "Chocolate Egg Spot"
match_center_well_spot = "Center Well Match Spot"  # in the shaft, across from chocolate egg

# instructions for contributors:
# the outer string is the name of the origin region
# the inner string is the name of the destination region or location
# use AWData to specify if it's a region or location, and then put the rules in the second parameter if any
# add item names used within rules to the names.py file if any are missing
# reason: we will probably change the names of things, so this'll make it easier
# if you want to add something like an event to a rule, do so, that's fine
# this is to set them apart from the rest for now, just making it easier as we write it initially
traversal_requirements: Dict[str, Dict[str, AWData]] = {
    bird_area: {
        fish_upper:
            AWData(AWType.region),
        bear_area_entry:
            AWData(AWType.region),
        dog_area:
            AWData(AWType.region),
        dog_upper:
            AWData(AWType.region),
        bird_capybara_waterfall:  # kinda tight with the disc, but you can just make it to the egg chest
            AWData(AWType.region, [[iname.disc], [iname.bubble_short]]),
        bird_below_mouse_statues:  # enter from the room where you can get the planet egg
            AWData(AWType.region, [[iname.can_break_spikes_below]]),
        frog_near_wombat:  # to the right of the bunny mural, drop down
            AWData(AWType.region),
        hippo_entry:
            AWData(AWType.region, [[iname.blue_flame, iname.green_flame, iname.pink_flame, iname.violet_flame]]),
        bear_truth_egg_spot:
            AWData(AWType.region, [[iname.disc_hop_hard]]),
        lname.stamp_chest:
            AWData(AWType.location),
        lname.flute_chest:
            AWData(AWType.location, [["8 Eggs"]]),
        lname.pencil_chest:
            AWData(AWType.location, [["16 Eggs", iname.bubble], ["16 Eggs", iname.disc]]),
        lname.top_chest:
            AWData(AWType.location, [["32 Eggs", iname.bubble], ["32 Eggs", iname.disc]]),
        lname.egg_65:
            AWData(AWType.location, [["64 Eggs", iname.bubble], ["64 Eggs", iname.disc]]),
        lname.key_office:  # does this actually require 64 eggs?
            AWData(AWType.location, [["64 Eggs", iname.bubble, iname.flute], ["64 Eggs", iname.disc, iname.flute]]),
        lname.bunny_duck:  # edit rule if we shuffle songs
            AWData(AWType.location, [[iname.flute]]),
        lname.bunny_mural:
            AWData(AWType.location, [[iname.remote]]),
        lname.egg_virtual:  # sneaky passage in the top left of the screen with the penguin hedges
            AWData(AWType.location),
        lname.match_above_egg_room:
            AWData(AWType.location, [[iname.disc], [iname.remote], [iname.bubble_long]]),
        lname.egg_holiday:  # in the wall to the right of the egg room entrance
            AWData(AWType.location, [[iname.bubble], [iname.disc_hop]]),
        lname.egg_rain:
            AWData(AWType.location, [[iname.top]]),
    },
    bird_capybara_waterfall: {
        lname.egg_sweet:
            AWData(AWType.location),
    },
    bird_below_mouse_statues: {
        lname.match_under_mouse_statue:
            AWData(AWType.location),
        lname.egg_planet:
            AWData(AWType.location),
        frog_travel_egg_spot:
            AWData(AWType.region, [[iname.top]]),
    },

    starting_area: {
        starting_after_ghost:  # it would feel weird to call this the central area imo
            AWData(AWType.region, [[iname.firecrackers]]),  # not sure if randoing firecrackers yet
        candle_area:
            AWData(AWType.region, [[iname.light_all_candles, iname.bubble]]),  # turn this into an event later
        s_disc_area:
            AWData(AWType.region, [[iname.s_medal, iname.bubble], [iname.s_medal, iname.disc_hop]]),
        lname.egg_clover:  # in room where you see the status of the candles
            AWData(AWType.location),
        lname.match_start_ceiling:
            AWData(AWType.location),
        lname.bunny_face:
            AWData(AWType.location, [[iname.flute]]),
        fast_travel_fake:
            AWData(AWType.region, [[iname.flute]]),
    },
    starting_after_ghost: {
        bird_area:
            AWData(AWType.region),
        lname.candle_first:
            AWData(AWType.location, [[iname.match]]),  # idk if we're even doing these
        lname.egg_gorgeous:  # up and right of the candle
            AWData(AWType.location),
        lname.map_chest:
            AWData(AWType.location),
    },
    s_disc_area: {
        lname.remote_chest:
            AWData(AWType.location),
        lname.egg_iridescent:
            AWData(AWType.location, [[iname.remote]]),
        lname.egg_ice:
            AWData(AWType.location, [[iname.remote]]),
        lname.egg_neon:
            AWData(AWType.location, [[iname.remote, iname.ball]]),
    },
    candle_area: {
        lname.medal_e:
            AWData(AWType.location),
    },

    fish_upper: {
        lname.match_fish_mural:  # right at the start, just some platforming
            AWData(AWType.location),
        lname.bunny_fish:
            AWData(AWType.location, [[iname.flute]]),
        # upper right of fish mural room leads to Virtual Egg, which you can get itemless
        # upper right of first bubble room leads to a door that requires a button hit on both sides
        lname.egg_mystic:  # avoid the fireball thrower, hit some buttons
            AWData(AWType.location),
        lname.egg_great:  # east end of the crane room
            AWData(AWType.location, [[iname.bubble], [iname.disc_hop]]), 
        lname.egg_normal:  # hidden wall in lower left of first bubble room
            AWData(AWType.location),
        lname.egg_dazzle:  # little obstacle course, feels like the bubble jump tutorial?
            AWData(AWType.location, [[iname.bubble_short]]),
        fish_tube_room:  # enter at the save room fish pipe, the rooms with all the fish pipes
            AWData(AWType.region, [[iname.bubble]]),
        lname.egg_sunset:  # break the spikes in the room to the right of the fish warp
            AWData(AWType.location, [[iname.can_break_spikes_below], [iname.disc_hop]]),
        
    },
    fish_wand_pit: {
        # fish_upper:  # commented out because not logically relevant
        #     AWData(AWType.region, [[iname.bubble_long], [iname.disc_hop]]),
        fish_west:
            AWData(AWType.region, [[iname.bubble], [iname.disc]]),  # Bubble OR disc to go vertically out of the pit
        lname.b_wand_chest:
            AWData(AWType.location),
    },
    fish_west: {
        lname.egg_ancient:  # one room up and left of save point, vines in top right
            AWData(AWType.location, [[iname.bubble], [iname.disc_hop_hard]]),
        fish_lower:  # bubble to go down, disc or remote to activate switches, breakspike to pass icicles in first penguin room
            AWData(AWType.region, [[iname.bubble, iname.remote, iname.can_break_spikes], [iname.bubble, iname.disc]]),
        lname.activate_fish_fast_travel:
            AWData(AWType.location, [[iname.flute]]),
        fast_travel:
            AWData(AWType.region, [[iname.activated_fish_fast_travel]]),
        lname.egg_galaxy:
            AWData(AWType.location, [[iname.remote, iname.disc]]),
    },        
    fish_tube_room: {  # no location access rules because you need bubble wand to get here anyway
        lname.egg_friendship:  # the green pipe in the fish tube room
            AWData(AWType.location),  # tight timing with no midair bubble jumps
        lname.egg_magic:  # open the gate in the fish tube room
            AWData(AWType.location),
    },
    fish_lower: {
        fish_west:
            AWData(AWType.region, [[iname.bubble]]),  # fish pipe left of the save point
        fish_boss_1:  # disc is required to solve both the windbox puzzle and to cross the whale room
            AWData(AWType.region, [[iname.disc]]),
        bobcat_room:
            AWData(AWType.region, [[iname.top]]), 
        lname.candle_fish:
            AWData(AWType.location, [[iname.disc], [iname.bubble]]),
        lname.egg_goodnight:
            AWData(AWType.location, [[iname.can_defeat_ghost], [iname.event_candle_penguin_lit]]),
    },
    fish_boss_1: {  # the disc required to clear this room's puzzle is in the entrance reqs, so not duplicated here
        chest_on_spikes_region:  # the one you're supposed to get to after getting the wheel
            AWData(AWType.location, [[iname.bubble_short]]),
        fish_boss_2:
            AWData(AWType.region),
        lname.egg_brick:  # disc hard required for one switch, and you can use disc to get in
            AWData(AWType.location, [[iname.disc, iname.wheel]]),
    },
    chest_on_spikes_region: {
        lname.egg_scarlet:
            AWData(AWType.location, [[iname.wheel]]),
        # no connection to fish_boss_1 since you'd need to open the door in fish_boss_1
        fish_boss_2:
            AWData(AWType.region),  # you can just jump down the shaft
    },
    fish_boss_2: {
        lname.flame_blue:
            AWData(AWType.location, [[iname.can_open_flame]]),
        bird_area:
            AWData(AWType.region),
        abyss:  # little hole above the fish pipe
            AWData(AWType.region, [[iname.top, iname.e_medal, iname.disc], [iname.top, iname.e_medal, iname.bubble]]),
    },
    abyss: {
        uv_lantern_spot:
            AWData(AWType.region, [[iname.flute, iname.disc], [iname.flute, iname.bubble_short]]),
    },

    bear_area_entry: {
        lname.key_bear_lower:
            AWData(AWType.location),
        bear_capybara_and_below:
            AWData(AWType.region, [[iname.key], [iname.bubble_short]]),
        bear_transcendental:  # might be controversial? it's across a screen transition but only 4 bubbles
            AWData(AWType.region, [[iname.bubble_short], [iname.disc_hop_hard]]),
        bear_kangaroo_waterfall:
            AWData(AWType.region, [[iname.slink], [iname.top, iname.yoyo]]),  # todo: check if top + yoyo can be used
        bear_razzle_egg_spot:
            AWData(AWType.region, [[iname.defeated_chameleon, iname.bubble_short],
                                     [iname.defeated_chameleon, iname.disc_hop_hard]])
    },
    bear_capybara_and_below: {
        bear_future_egg_room:
            AWData(AWType.region),
        lname.key_bear_upper:
            AWData(AWType.location),
        lname.egg_zen:
            AWData(AWType.location, [[iname.slink, iname.bubble], [iname.slink, iname.disc]]),
        bear_dark_maze:  # need one key to open the gate
            AWData(AWType.region, [[iname.key]]),
        lname.egg_universal:
            AWData(AWType.location, [[iname.slink, iname.bubble, iname.yoyo],
                                     [iname.slink, iname.bubble, iname.firecrackers],
                                     [iname.slink, iname.disc]]),  # disc hits the chinchilla across
        lname.egg_value:
            AWData(AWType.location, [[iname.bubble_long, iname.disc_hop_hard]]),
    },
    bear_future_egg_room: {
        lname.egg_future:  # chinchilla on the moving platforms puzzle room
            AWData(AWType.location),
    },
    bear_chinchilla_song_room: {
        lname.bunny_chinchilla_vine:
            AWData(AWType.location),
        bear_future_egg_room:
            AWData(AWType.region),
    },
    bear_dark_maze: {
        bear_chameleon_room_1:
            AWData(AWType.region),
        lname.candle_bear:
            AWData(AWType.location, [[iname.bubble], [iname.disc]]),
        lname.egg_lf:
            AWData(AWType.location, [[iname.firecrackers]]),
    },
    bear_chameleon_room_1: {
        bear_dark_maze:
            AWData(AWType.region, [[iname.bubble], [iname.disc]]),
        bear_ladder_after_chameleon:
            AWData(AWType.region),
        lname.medal_s:
            AWData(AWType.location, [[iname.defeated_chameleon]]),
    },
    bear_ladder_after_chameleon: {
        bear_slink_room:  # jump up through the floor at the top of the ladder
            AWData(AWType.region),
    },
    bear_slink_room: {
        lname.slink_chest:
            AWData(AWType.location),
        bear_transcendental:  # descend, jump into left wall, or disc hop from the platforms underneath. TODO: too tight to not be disc_hop_hard? It's close.
            AWData(AWType.region, [[iname.slink, iname.bubble], [iname.top, iname.bubble],
                                   [iname.slink, iname.disc_hop], [iname.top, iname.disc_hop],
                                   [iname.ball, iname.disc_hop], [iname.ball, iname.disc_hop]]),
        # bear_area_entry:  # unnecessary because it's a sphere 1 area
        #     AWData(AWType.region),
    },
    bear_transcendental: {
        lname.egg_transcendental:
            AWData(AWType.location),
    },
    bear_kangaroo_waterfall: {
        bear_ladder_after_chameleon:
            AWData(AWType.region),  # just press a button
        bear_middle_phone_room:
            AWData(AWType.region, [[iname.slink]]),
        lname.egg_post_modern:
            AWData(AWType.location, [[iname.top, iname.switch_for_post_modern_egg]]),
        bear_truth_egg_spot:  # throw disc to the right after jumping down the waterfall
            AWData(AWType.region, [[iname.disc]]),
    },
    bear_truth_egg_spot: {
        lname.egg_truth:
            AWData(AWType.location),
    },
    bear_middle_phone_room: {
        lname.activate_bear_fast_travel:
            AWData(AWType.location, [[iname.flute]]),
        fast_travel:
            AWData(AWType.region, [[iname.activated_bear_fast_travel]]),
        lname.egg_chaos:  # in the room with the monkey that throws rocks at you
            AWData(AWType.location),
        bear_crow_rooms:
            AWData(AWType.region, [[iname.slink], [iname.ball_tricky]]),
        bear_match_chest_spot:
            AWData(AWType.region, [[iname.ball_tricky, iname.disc, iname.weird_skips]]),  # oh hell yeah this is a cool one
    },
    bear_crow_rooms: {
        bear_shadow_egg_spot:  # get across the room with the lifters and the miasma
            AWData(AWType.region, [[iname.slink], [iname.lantern], [iname.tanking_damage]]),
        lname.bunny_crow:  # it jumps down after a moment
            AWData(AWType.location, [[iname.flute]]),
        bear_hedgehog_square:  # slink needed for puzzle to get to the button
            AWData(AWType.region, [[iname.slink], [iname.ball_tricky]]),
    },
    bear_shadow_egg_spot: {
        lname.egg_shadow:
            AWData(AWType.location),
        bear_crow_rooms:
            AWData(AWType.region),
    },
    bear_hedgehog_square: {
        lname.bunny_ghost_dog:  # todo: find a route that doesn't require the flute
            AWData(AWType.location, [[iname.m_disc, iname.flute, iname.activated_bear_fast_travel]]),
        bear_connector_passage:
            AWData(AWType.region, [[iname.slink]]),
    },
    bear_connector_passage: {
        bear_capybara_and_below:
            AWData(AWType.region),
        bear_middle_phone_room:
            AWData(AWType.region),
        bear_match_chest_spot:  # you open some doors starting at the connector and ending at the door to here. Or, bubble over the wall through the miasma. Will we call this bubble_short?
            AWData(AWType.region, [[iname.slink], [iname.bubble, iname.tanking_damage],
                                   [iname.disc, iname.tanking_damage, iname.weird_skips]]),
    },
    bear_match_chest_spot: {
        lname.match_bear:
            AWData(AWType.location),
        chocolate_egg_spot:
            AWData(AWType.region, [[iname.bubble]]),  # wall juts out, need bubble
        match_center_well_spot:
            AWData(AWType.region),  # wall is flush, just hold left
        # top_of_the_well:  # unnecessary because of the connection from match center spot
        #     AWData(AWType.region, [[iname.bubble_long]]),
        bear_upper_phone_room:  # todo: see if ball can go through wooden platforms
            AWData(AWType.region, [[iname.slink, iname.yoyo]]),
    },
    bear_upper_phone_room: {
        bear_above_chameleon:
            AWData(AWType.region, [[iname.yoyo]]),  # todo: check if you can do this with ball
    },
    bear_above_chameleon: {  # includes the screens to the right of it
        lname.egg_swan:  # wake one chinchilla, push another
            AWData(AWType.location, [[iname.flute, iname.disc], [iname.firecrackers]]),
        # chinchilla can be woken up with flute or firecrackers
        # otters can be distracted with firecrackers, yoyo, or top
        # you need 3 firecrackers minimum if you want to get through without yoyo or flute
        bear_shadow_egg_spot:
            AWData(AWType.region, [[iname.top, iname.slink, iname.yoyo, iname.flute],
                                   [iname.top, iname.slink, iname.firecrackers]]),
        bear_chameleon_room_2:
            AWData(AWType.region, [[iname.yoyo, iname.slink, iname.flute],
                                   [iname.yoyo, iname.slink, iname.firecrackers]]),
    },
    bear_chameleon_room_2: {
        bear_middle_phone_room:  # drop down, probably unimportant
            AWData(AWType.region),
        lname.flame_violet:
            AWData(AWType.location, [[iname.can_open_flame]]),
        bear_upper_phone_room:
            AWData(AWType.region),
    },
    bear_razzle_egg_spot: {
        lname.egg_razzle:
            AWData(AWType.location),
        bear_dark_maze:
            AWData(AWType.region),
    },

    dog_area: {
        lname.disc_spot:
            AWData(AWType.location),  # todo: figure out what to do for this
        lname.candle_dog_dark:
            AWData(AWType.location, [[iname.match]]),  # todo: figure out what we're doing for matches/candles
        dog_chinchilla_skull:
            AWData(AWType.region, [[iname.bubble]]),  # can get here without bubble jumps
        dog_upside_down_egg_spot:  # upper right of switch platform room above second dog
            AWData(AWType.region, [[iname.bubble_short]]),
        dog_at_mock_disc:  # you drop down to here, but can't get back up immediately
            AWData(AWType.region),
        lname.egg_orange:
            AWData(AWType.location, [[iname.top]]),
    },
    dog_upside_down_egg_spot: {
        lname.egg_upside_down:
            AWData(AWType.location),
        dog_area:
            AWData(AWType.region),
        dog_many_switches:
            AWData(AWType.region, [[iname.remote]]),
    },
    dog_at_mock_disc: {
        dog_area:  # can leave by hitting the button or jumping up to the ledge you came from
            AWData(AWType.region, [[iname.bubble], [iname.disc]]),
        lname.egg_sour:  # when escaping the dachsund, jump up and right out of the tunnel
            AWData(AWType.location),
        bird_area:  # after the sour egg chest, you escape to the central area
            AWData(AWType.region),
    },
    dog_chinchilla_skull: {
        lname.egg_red:
            AWData(AWType.location, [[iname.firecrackers], [iname.disc]])  # use a firecracker to scare them, or mash discs at them.
    },
    dog_upper: {
        dog_upper_past_lake:
            AWData(AWType.region, [[iname.disc_hop], [iname.bubble_long]]),  # maybe not long?
        dog_upper_above_switch_lines:
            AWData(AWType.region, [[iname.disc], [iname.remote], [iname.top]]),  # double check you can use remote in here
        lname.egg_evil:
            AWData(AWType.location, [[iname.flute]]),
    },
    dog_upper_past_lake: {
        lname.candle_dog_switch_box:
            AWData(AWType.location),
        dog_upper_above_switch_lines:
            AWData(AWType.region, [[iname.can_distract_dogs]]),  # need to get past the 3 dogs
        barcode_bunny:  # region since you can get this in two spots
            AWData(AWType.region, [[iname.flute, iname.song_barcode]]),
        lname.mama_cha:
            AWData(AWType.location, [[iname.flute]]),  # add song req if we're shuffling songs
        # todo: floor is lava
        dog_many_switches:
            AWData(AWType.region, [[iname.can_break_spikes]]),  # todo: verify you can do this with wheel
        dog_under_fast_travel_room:
            AWData(AWType.region, [[iname.switch_next_to_bat_room], [iname.bubble_short]]),
    },
    dog_under_fast_travel_room: {
        dog_upper_past_lake:
            AWData(AWType.region, [[iname.bubble_short]]),
        dog_fast_travel_room:
            AWData(AWType.region, [[iname.can_distract_dogs], [iname.bubble_long], [iname.wheel]]),  # wheel can allow you to crank safely. not usable at most other dogs
    },
    dog_fast_travel_room: {
        dog_under_fast_travel_room:
            AWData(AWType.region),
        lname.activate_dog_fast_travel:
            AWData(AWType.location, [[iname.flute]]),
        dog_swordfish_lake_ledge:
            AWData(AWType.region),
        dog_upper_past_lake:  # ride bubble down, jump the partial-height wall
            AWData(AWType.region, [[iname.bubble]]),
        dog_above_fast_travel:
            AWData(AWType.region, [[iname.slink], [iname.bubble_short]]),
        dog_mock_disc_shrine:
            AWData(AWType.region, [[iname.slink]]),
    },
    dog_mock_disc_shrine: {
        lname.egg_raw:
            AWData(AWType.location, [[iname.slink, iname.disc_hop_hard],
                                     [iname.slink, iname.bubble_short],
                                     [iname.slink, iname.key]]),
        lname.flame_pink:
            AWData(AWType.location, [[iname.m_disc]]),
    },
    dog_above_fast_travel: {
        lname.egg_brown:
            AWData(AWType.location, [[iname.slink]]),
        lname.egg_reference:  # funny slink and disc room
            AWData(AWType.location, [[iname.slink, iname.disc]]),
        dog_fast_travel_room:
            AWData(AWType.region),
        lname.egg_crystal:  # todo: revisit with wheel to see if we need more items
            AWData(AWType.location, [[iname.top, iname.ball, iname.slink, iname.remote, iname.wheel]]),
    },
    dog_swordfish_lake_ledge: {
        dog_fast_travel_room:
            AWData(AWType.region, [[iname.disc]]),
        lname.egg_forbidden:
            AWData(AWType.location, [[iname.disc], [iname.bubble_long]]),
        lname.bunny_disc_spike:
            AWData(AWType.location, [[iname.disc]]),  # not disc hop since you literally need to do this
        behind_kangaroo:
            AWData(AWType.region, [[iname.slink]]),
    },
    behind_kangaroo: {
        bear_middle_phone_room:
            AWData(AWType.region),  # activate dynamite
        lname.egg_plant:
            AWData(AWType.location, [[iname.disc, iname.slink]]),
        kangaroo_blocks:
            AWData(AWType.region, [[iname.ball]]),
    },
    dog_many_switches: {
        lname.candle_dog_many_switches:
            AWData(AWType.location),
        dog_upside_down_egg_spot:
            AWData(AWType.region, [[iname.remote]]),
        dog_bat_room:
            AWData(AWType.region),
    },
    dog_bat_room: {
        lname.key_dog:
            AWData(AWType.location),
        lname.switch_next_to_bat_room:
            AWData(AWType.location),
        lname.egg_service:
            AWData(AWType.location),
        kangaroo_room:
            AWData(AWType.region, [[iname.k_medal, iname.bubble], [iname.k_medal, iname.disc]]),
    },
    kangaroo_room: {
        dog_bat_room:
            AWData(AWType.region),
        lname.b_ball_chest:
            AWData(AWType.location),
        kangaroo_blocks:
            AWData(AWType.region, [[iname.ball, iname.disc], [iname.ball, iname.bubble]]),
    },
    kangaroo_blocks: {
        kangaroo_room:
            AWData(AWType.region),
        lname.egg_vanity:
            AWData(AWType.location),
        behind_kangaroo:
            AWData(AWType.region),
    },
    dog_upper_above_switch_lines: {
        lname.match_dog_switch_bounce:  # in the little switch area
            AWData(AWType.location, [[iname.disc], [iname.remote], [iname.top]]),
        lname.candle_dog_disc_switches:
            AWData(AWType.location, [[iname.match, iname.disc], [iname.match, iname.remote], [iname.match, iname.top]]),
        lname.egg_depraved:  # in the little switch area, you need to take care of the ghost
            AWData(AWType.location, [[iname.disc, iname.can_defeat_ghost], [iname.remote, iname.can_defeat_ghost]]),
        dog_upper_above_switch_lines_to_upper_east:
            AWData(AWType.region, [[iname.disc], [iname.remote]]),
    },
    dog_upper_above_switch_lines_to_upper_east: {
        dog_upper_above_switch_lines:
            AWData(AWType.region),  # hit button, walk into the hallway
        dog_upper_east:
            AWData(AWType.region),
    },
    dog_upper_east: {
        dog_upper_above_switch_lines_to_upper_east:
            AWData(AWType.region, [[iname.bubble_short]]),  # jump up to the switch
        lname.match_dog_upper_east:
            AWData(AWType.location),
        dog_upper:  # hit the dynamite switch to get back to the bird area and upper dog
            AWData(AWType.region),
        frog_dark_room:  # take the bubble pipe by the dynamite, this is the really long pipe
            AWData(AWType.region, [[iname.bubble]]),
        dog_elevator:
            AWData(AWType.region, [[iname.slink]]),
    },
    dog_elevator: {
        lname.switch_for_post_modern_egg:
            AWData(AWType.location),
        dog_wheel:
            AWData(AWType.region, [[iname.remote]]),
        dog_elevator_upper:
            AWData(AWType.region, [[iname.dog_wheel_flip]]),
    },
    dog_wheel: {
        # bird_area:
        #     AWData(AWType.region),
        lname.dog_wheel_flip:
            AWData(AWType.region, [[iname.yoyo]]),
    },
    dog_elevator_upper: {
        lname.egg_big:
            AWData(AWType.location),
        bear_match_chest_spot:
            AWData(AWType.region, [[iname.bubble]]),
    },

    frog_near_wombat: {
        lname.candle_frog:
            AWData(AWType.location, [[iname.match]]),
        lname.egg_moon:  # the one with all the mouse heads
            AWData(AWType.location, [[iname.disc, iname.lantern], [iname.bubble, iname.lantern]]),
            # bubble short or maybe just bubble? You have to shoot down at the apex of your jump, feels weird
            # I was getting this 90% of the time, not sure it's intuitive? make it logical and put it in the tricks FAQ.
        lname.egg_promise:  # under spikes in 3 bird room
            AWData(AWType.location, [[iname.lantern, iname.can_break_spikes_below]]),
        frog_under_ostrich_statue:  # after hitting the switch, no items needed
            AWData(AWType.region),
        frog_travel_egg_spot:
            AWData(AWType.region, [[iname.key]]),
        frog_pre_ostrich_attack:
            AWData(AWType.region, [[iname.top]]),
    },
    frog_travel_egg_spot: {  # the spot behind the groundhog
        lname.egg_travel:
            AWData(AWType.location),
        frog_ostrich_attack:
            AWData(AWType.region, [[iname.yoyo], [iname.ball]]),
        frog_near_wombat:
            AWData(AWType.region, [[iname.key]]),  # assuming the key can open it from the left
    },
    frog_under_ostrich_statue: {
        frog_near_wombat:  # may have to go a few screens away to hit a switch, but you don't need items
            AWData(AWType.region),
        lname.egg_bubble:  # top right of room with the mouse ghost that throws its head
            AWData(AWType.location, [[iname.bubble], [iname.disc]]),
        frog_pre_ostrich_attack:
            AWData(AWType.region),
    },
    frog_pre_ostrich_attack: {
        frog_ostrich_attack:
            AWData(AWType.region),
    },
    frog_ostrich_attack: {
        lname.key_chest_mouse_head_lever:
            AWData(AWType.location),
        lname.egg_dream:  # right after the key chest
            AWData(AWType.location),
        bird_area:  # door switch to get you out under the bunny mural
            AWData(AWType.region),
        frog_worm_shaft_top:
            AWData(AWType.region),
    },
    frog_worm_shaft_top: {
        lname.egg_fire:  # after ostrich attack room
            AWData(AWType.location, [[iname.disc], [iname.bubble_short]]),
        frog_worm_shaft_bottom:
            AWData(AWType.region),
    },
    frog_worm_shaft_bottom: {
        frog_worm_shaft_top:
            AWData(AWType.region, [[iname.bubble_long]]),  # climb the shaft above the save point
        lname.yoyo_chest:
            AWData(AWType.location),
        frog_bird_after_yoyo_1:  # can bypass the locked door with bubble jumps + lantern
            AWData(AWType.region, [[iname.yoyo], [iname.bubble_long, iname.lantern]]),  # todo: test if you can use ball
    },
    frog_bird_after_yoyo_1: {
        frog_bird_after_yoyo_2:  # pain in the ass, but you can get up with downwards bubbles
            AWData(AWType.region, [[iname.yoyo], [iname.bubble_long]]),
        frog_worm_shaft_bottom:  # if you fall along the left side from a screen up, the bird doesn't reach you in time
            AWData(AWType.region),
        lname.egg_sapphire:
            AWData(AWType.location, [[iname.lantern]]),
    },
    frog_bird_after_yoyo_2: {
        lname.activate_frog_fast_travel:
            AWData(AWType.location, [[iname.flute]]),
        lname.key_frog_guard_room_west:
            AWData(AWType.location, [[iname.yoyo], [iname.flute], [iname.ball]]),  # you can just throw the ball at their shields lmao
        lname.match_guard_room:  # hit guard then jump off its head, or jump up with mobility
            AWData(AWType.location, [[iname.yoyo], [iname.flute], [iname.disc_hop], [iname.bubble], [iname.ball]]), # todo: top, ball, wheel?
        # 2 doors in the top right of this region
        lname.key_frog_guard_room_east: 
            AWData(AWType.location, [[iname.yoyo], [iname.bubble, iname.flute], [iname.ball]]),  # might be doable with flute + disc?
        frog_dark_room:  # yoyo to open the door, lantern to fall through the bird
            AWData(AWType.region, [[iname.yoyo], [iname.lantern]]),
        frog_ruby_egg_ledge:  # fall through a bird onto it
            AWData(AWType.region, [[iname.lantern]]),
        frog_east_of_fast_travel:  # yoyo to open the door
            AWData(AWType.region, [[iname.yoyo]]),
        frog_pre_ostrich_attack:
            AWData(AWType.region, [[iname.two_keys]]),
    },
    frog_dark_room: {
        frog_bird_after_yoyo_2:  # jump up at the rust egg with lantern, or use yoyo to open the door
            AWData(AWType.region, [[iname.lantern], [iname.yoyo]]),  # todo: verify you can yoyo the door open from this side
        lname.egg_rust:  # top left of the dark room
            AWData(AWType.location),
        lname.egg_jade:  # do the puzzle
            AWData(AWType.location),
        bird_capybara_waterfall:  # take the very long pipe to the sweet egg room
            AWData(AWType.region, [[iname.bubble]]),
        frog_ruby_egg_ledge:  # two bubble jumps, a difficult disc use (but no disc hops) or dig out the frog and flute
            AWData(AWType.region, [[iname.bubble_short], [iname.disc], [iname.top, iname.flute]]),
        frog_elevator_and_ostrich_wheel:  # you need these two items to avoid locking checks
            AWData(AWType.region, [[iname.yoyo, iname.bubble]]),
    },
    frog_ruby_egg_ledge: {
        lname.egg_ruby:  # this whole region just for one egg
            AWData(AWType.location),
    },
    frog_elevator_and_ostrich_wheel: {
        lname.egg_desert:  # up the elevator, bottom right of dangerous elevator room
            AWData(AWType.location),  # you need yoyo and bubble to get to this check logically
            # if you have yoyo, you can swap the mouse direction and lock yourself out of the check without bubbles
        lname.egg_obsidian:  # bounce disc between the moving walls
            AWData(AWType.location, [[iname.disc]]),
        lname.egg_golden:
            AWData(AWType.location, [[iname.wheel]]),
        lname.flame_green:
            AWData(AWType.location),
        bobcat_room:
            AWData(AWType.region, [[iname.top]]),
        # bird_area:  # pipe after flame, you need bubble to be here so no need to put the item requirement
        #     AWData(AWType.region),
    },
    bobcat_room: {
        frog_elevator_and_ostrich_wheel:  # todo: check if you can actually use top to get in here backwards
            AWData(AWType.region, [[iname.top, iname.yoyo, iname.bubble]]),
        fish_lower:
            AWData(AWType.region, [[iname.top]]),
        lname.wheel_chest:
            AWData(AWType.location, [[iname.song_bobcat]]),
        chest_on_spikes_region:  # kinda unreasonable without the wheel imo
            AWData(AWType.region, [[iname.wheel]]),
    },

    hippo_entry: {
        lname.activate_hippo_fast_travel:
            AWData(AWType.location, [[iname.flute]]),
        lname.lantern_chest:
            AWData(AWType.location, [[iname.slink, iname.disc, iname.bubble, iname.yoyo]]),
        hippo_manticore_room:  # can technically use ball instead of yoyo but it's inconsistent
            AWData(AWType.region, [[iname.lantern, iname.disc, iname.yoyo]]),

    },
    hippo_manticore_room: {
        hippo_fireworks:
            AWData(AWType.region, [[iname.slink, iname.yoyo, iname.disc], [iname.slink, iname.yoyo, iname.bubble]]),
        hippo_skull_room:
            AWData(AWType.region, [[iname.slink, iname.yoyo, iname.disc], [iname.slink, iname.yoyo, iname.bubble]]),
    },
    hippo_skull_room: {
        lname.bb_wand_chest:
            AWData(AWType.location),  # need to die a lot
    },
    hippo_fireworks: {
        lname.victory_first:
            AWData(AWType.location),
        home:
            AWData(AWType.region, [[iname.house_key]]),
        hippo_skull_room:
            AWData(AWType.region, [[iname.bubble_short], [iname.disc_hop_hard]]),
    },
    home: {
        hippo_fireworks:
            AWData(AWType.region, [[iname.house_key]]),
        lname.bunny_tv:
            AWData(AWType.location, [[iname.flute]]),
        lname.fanny_pack_chest:
            AWData(AWType.location),
        barcode_bunny:
            AWData(AWType.region, [[iname.flute, iname.song_barcode]]),
        top_of_the_well:
            AWData(AWType.region, [[iname.lantern]]),
    },
    barcode_bunny: {
        lname.bunny_barcode:
            AWData(AWType.location),
    },

    top_of_the_well: {
        home:
            AWData(AWType.region, [[iname.lantern]]),
        lname.egg_pickled:  # hold right while falling down the well
            AWData(AWType.location),
        chocolate_egg_spot:
            AWData(AWType.region, [[iname.bubble]]),  # wall juts out, need bubble
        match_center_well_spot:
            AWData(AWType.region),  # wall is flush, just hold left
    },
    chocolate_egg_spot: {
        lname.egg_chocolate:  # across from center well match
            AWData(AWType.location),
        match_center_well_spot:
            AWData(AWType.region, [[iname.disc, iname.remote], [iname.bubble_short, iname.remote]]),
        bear_match_chest_spot:
            AWData(AWType.region, [[iname.bubble_long]]),
        top_of_the_well:
            AWData(AWType.region, [[iname.bubble_long]]),
    },
    match_center_well_spot: {
        lname.match_center_well:  # across from the chocolate egg
            AWData(AWType.location),
        chocolate_egg_spot:  # todo: verify that this needs bubble short
            AWData(AWType.region, [[iname.disc, iname.remote], [iname.bubble_short, iname.remote]]),
        bear_match_chest_spot:
            AWData(AWType.region, [[iname.bubble_long]]),
        top_of_the_well:
            AWData(AWType.region, [[iname.bubble_long]]),
    },

    fast_travel: {
        starting_area:
            AWData(AWType.region, [[iname.flute]]),
        bird_area:
            AWData(AWType.region, [[iname.flute]]),
        fish_west:
            AWData(AWType.region, [[iname.flute]]),
        frog_dark_room:
            AWData(AWType.region, [[iname.activated_frog_fast_travel]]),
        bear_middle_phone_room:
            AWData(AWType.region, [[iname.activated_bear_fast_travel]]),
        dog_fast_travel_room:
            AWData(AWType.region, [[iname.activated_dog_fast_travel]]),
        hippo_entry:
            AWData(AWType.region, [[iname.activated_hippo_fast_travel]]),
    },
    fast_travel_fish_teleport: {
        uv_lantern_spot:
            AWData(AWType.region),
        fast_travel:
            AWData(AWType.region),
    },

    fast_travel_fake: {  # for direct teleport spells
        fast_travel:
            AWData(AWType.region),  # probably never randomizing fast travel song, so no rule
        top_of_the_well:
            AWData(AWType.region, [[iname.song_home]]),
        bear_chinchilla_song_room:
            AWData(AWType.region, [[iname.song_chinchilla]]),
        fast_travel_fish_teleport:
            AWData(AWType.region, [[iname.song_fish]]),
    },
}
