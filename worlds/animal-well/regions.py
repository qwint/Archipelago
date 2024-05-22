from typing import Dict, List, NamedTuple
from enum import IntEnum
from names import item_names as iname, location_names as lname


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
bear_upper_phone_room = "Bear Upper Phone Room"  # after the previous region
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
top_of_the_well = "Top of the Well"  # where the warp song takes you, right of the house
frog_near_wombat = "Frog Area near Wombat"  # first part of the frog area after you drop down the hole
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
        bird_capybara_waterfall:
            AWData(AWType.region, [[iname.disc], [iname.bubble_short]]),
        bird_below_mouse_statues:  # enter from the room where you can get the planet egg
            AWData(AWType.region, [[iname.can_break_spikes_below]]),
        frog_near_wombat:  # to the right of the bunny mural, drop down
            AWData(AWType.region),
        lname.stamp_chest:
            AWData(AWType.location),
        lname.flute_chest:
            AWData(AWType.location, [["8 Eggs"]]),
        lname.pencil_chest:
            AWData(AWType.location, [["16 Eggs", iname.bubble], ["16 Eggs", iname.disc]]),
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
    },

    starting_area: {
        starting_after_ghost:  # it would feel weird to call this the central area imo
            AWData(AWType.region, [[iname.firecrackers]]),  # not sure if randoing firecrackers yet
        candle_area:
            AWData(AWType.region, [["Light All Candles"]]),  # turn this into an event later
        s_disc_area:
            AWData(AWType.region, [[iname.s_medal, iname.bubble], [iname.s_medal, iname.disc]]),
        lname.egg_clover:  # in room where you see the status of the candles
            AWData(AWType.location),
        lname.ceiling_match_start:
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

    fish_upper: {
        lname.fish_mural_match:  # right at the start, just some platforming
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
    fish_boss_1: {  # the disc required to clear this room's puzzle is implicated in the entrance reqs so it is not duplicated here
        chest_on_spikes_region:  # the one you're supposed to get to after getting the wheel
            AWData(AWType.location, [[iname.bubble_short]]),
        fish_boss_2:
            AWData(AWType.region),
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

    bear_area_entry: {
        lname.key_bear_lower:
            AWData(AWType.location),
        bear_capybara_and_below:
            AWData(AWType.region, [[iname.key], [iname.bubble_short]]),
        bear_transcendental:  # might be controversial? it's across a screen transition but only 4 bubbles
            AWData(AWType.region, [[iname.bubble_short]]),
        bear_kangaroo_waterfall:
            AWData(AWType.region, [[iname.slink], [iname.top, iname.yoyo]]),  # todo: check if top + yoyo can be used
    },
    bear_capybara_and_below: {
        bear_future_egg_room:
            AWData(AWType.region),
        lname.key_bear_upper:
            AWData(AWType.location),
        # todo: go back to chinchilla chest on head room with slink
        bear_dark_maze:  # need one key to open the gate
            AWData(AWType.region, [[iname.key]]),
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
    },
    bear_ladder_after_chameleon: {
        bear_slink_room:  # jump up through the floor at the top of the ladder
            AWData(AWType.region),
    },
    bear_slink_room: {
        iname.slink:
            AWData(AWType.location),
        bear_transcendental:  # descend, jump into left wall
            AWData(AWType.region, [[iname.bubble]]),
        # bear_area_entry:  # unnecessary cause it's a sphere 1 area
        #     AWData(AWType.region),
    },
    bear_transcendental: {
        lname.egg_transcendental:
            AWData(AWType.location),
    },
    bear_kangaroo_waterfall: {
        bear_ladder_after_chameleon:
            AWData(AWType.region),  # just press a button
        bear_upper_phone_room:
            AWData(AWType.region, [[iname.slink]]),
    },
    bear_upper_phone_room: {
        lname.activate_bear_fast_travel:
            AWData(AWType.location, [[iname.flute]]),
    },

    dog_area: {
        lname.disc_spot:
            AWData(AWType.location),  # todo: figure out what to do for this
        lname.candle_dog_dark:
            AWData(AWType.location, [[iname.match]]),  # todo: figure out what we're doing for matches/candles
        dog_chinchilla_skull:
            AWData(AWType.region, [[iname.bubble]]),  # can get here without bubble jumps
        lname.egg_upside_down:  # upper right of switch platform room above second dog
            AWData(AWType.location, [[iname.bubble_short]]),  # todo: there's another way here from above?
        dog_at_mock_disc:  # you drop down to here, but can't get back up immediately
            AWData(AWType.region),
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
            AWData(AWType.location, [[iname.firecrackers]])  # use a firecracker
    },
    dog_upper: {
        dog_upper_past_lake:
            AWData(AWType.region, [[iname.disc_hop], [iname.bubble_long]]),  # maybe not long?
        dog_upper_above_switch_lines:
            AWData(AWType.region, [[iname.disc], [iname.remote]]),  # double check you can use remote in here
    },
    dog_upper_past_lake: {
        lname.candle_dog_switch_box:
            AWData(AWType.location),
        dog_upper_above_switch_lines:
            AWData(AWType.region, [[iname.can_distract_dogs]]),  # need to get past the 3 dogs
        lname.bunny_barcode:
            AWData(AWType.location, [[iname.flute]]),  # add song req if we're shuffling songs
        lname.mama_cha:
            AWData(AWType.location, [[iname.flute]]),  # add song req if we're shuffling songs
        # todo: floor is lava
    },
    dog_upper_above_switch_lines: {
        lname.dog_match_switch:  # in the little switch area
            AWData(AWType.location, [[iname.disc], [iname.remote]]),
        lname.candle_dog_disc_switches:
            AWData(AWType.location, [[iname.match, iname.disc], [iname.match, iname.remote]]),
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
        lname.dog_match_upper_east:
            AWData(AWType.location),
        dog_upper:  # hit the dynamite switch to get back to the bird area and upper dog
            AWData(AWType.region),
        frog_dark_room:  # take the bubble pipe by the dynamite, this is the really long pipe
            AWData(AWType.region, [[iname.bubble]]),
        # todo: get slink, go east past the room that needs it for a puzzle
    },

    frog_near_wombat: {
        # todo: locked door to the left of the wombat
        # todo: spikes at floor of the room with the 3 birds
        lname.candle_frog:
            AWData(AWType.location, [[iname.match]]),
        lname.egg_moon:  # the one with all the mouse heads
            AWData(AWType.location, [[iname.disc, iname.lantern], [iname.bubble_short, iname.lantern]]),
            # bubble short or maybe just bubble? You have to shoot down at the apex of your jump, feels weird
        frog_under_ostrich_statue:  # after hitting the switch, no items needed
            AWData(AWType.region),
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
    },
    frog_bird_after_yoyo_2: {
        lname.activate_frog_fast_travel:
            AWData(AWType.location, [[iname.flute]]),
        lname.key_frog_guard_room_west:
            AWData(AWType.location, [[iname.yoyo], [iname.flute]]),  # todo: top, ball, wheel?
        lname.guard_room_match:  # hit guard then jump off its head, or jump up with mobility
            AWData(AWType.location, [[iname.yoyo], [iname.flute], [iname.disc_hop], [iname.bubble]]), # todo: top, ball, wheel?
        # 2 doors in the top right of this region
        lname.key_frog_guard_room_east:  # todo: can you move the guards with ball or top?
            AWData(AWType.location, [[iname.yoyo], [iname.bubble, iname.flute]]),
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
            AWData(AWType.location),  # you need yoyo and bubble to get to this region
            # if you have yoyo, you can swap the mouse direction and lock yourself out of the check without bubbles
        lname.egg_obsidian:  # bounce disc between the moving walls
            AWData(AWType.location, [[iname.disc]]),
        lname.egg_golden:
            AWData(AWType.location, [[iname.wheel]]),
        lname.flame_green:
            AWData(AWType.location),
        # bird_area:  # pipe after flame, you need bubble to be here so no need to put the item requirement
        #     AWData(AWType.region),
    },

    top_of_the_well: {
        lname.egg_pickled:  # hold right while falling down the well
            AWData(AWType.location),
        lname.center_well_match:  # hold left while falling down well, switch might need to be flipped
            AWData(AWType.location),  # todo: verify if this should be in this region
        lname.egg_chocolate:  # todo: verify if this should be in this region
            AWData(AWType.location, [[iname.bubble]]),  # across from center well match, maybe remote should be involved?
    },

    fast_travel: {
        starting_area:
            AWData(AWType.region, [[iname.flute]]),
        fish_west:
            AWData(AWType.region, [[iname.flute]]),
        frog_dark_room:
            AWData(AWType.region, [[iname.activated_frog_fast_travel]]),
        bear_upper_phone_room:
            AWData(AWType.region, [[iname.activated_bear_fast_travel]]),
    },

    fast_travel_fake: {  # for direct teleport spells
        fast_travel:
            AWData(AWType.region),  # probably never randomizing fast travel song, so no rule
        top_of_the_well:
            AWData(AWType.region, [[iname.song_home]]),
        bear_chinchilla_song_room:
            AWData(AWType.region, [[iname.song_chinchilla]]),
    },
}
