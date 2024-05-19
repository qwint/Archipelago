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


# region names
fast_travel_fake = "Fast Travel Mid-Warp"  # for the purpose of not putting all the entrances at the starting region
starting_area = "Squirrel Main"
s_disc_area = "Squirrel S. Disc Area"
starting_after_ghost = "Squirrel After Ghost"
fast_travel = "Fast Travel Room"
bird_area = "Bird Area"  # the central portion of the map
bird_capybara_waterfall = "Bird Capybara Waterfall"  # up and right of the ladder
candle_area = "Squirrel Candle Area"
fish_upper = "Fish Upper"  # everything prior to the bubble wand chest
fish_lower = "Fish Lower"
fish_boss = "Fish Boss Arena"
fish_wand_pit = "Fish B.Wand Chest Pit"
fish_west = "Fish Warp Room"  # after the b. wand chest, rename
fish_tube_room = "Fish Pipe Maze"  # rename?
abyss = "Bone Fish Area"
bear_area = "Bear Main"
bear_chinchilla_song_room = "Bear Chinchilla Song Room"  # where the bunny is
dog_area = "Dog Main"
dog_chinchilla_skull = "Dog Chinchilla Skull Room"
dog_at_mock_disc = "Dog at Mock Disc Chest"
dog_upper = "Dog Area Upper"  # rename this variable and name
dog_upper_past_lake = "Dog Area Upper Past Lake"
dog_upper_above_switch_lines = "Dog Area Upper Above Switch Lines"  # rename, that spot where you go up the levels?
dog_upper_above_switch_lines_to_upper_east = "Dog Area Upper Above Switch Lines to Upper East"  # where the button is
dog_upper_east = "Dog Area Upper East"  # to the right of the area above the switch lines
wave_room = "Wave Room"  # rename after figuring out which area this is
bobcat_room = "Bobcat Room"

# instructions for contributors:
# the outer string is the name of the origin region
# the inner string is the name of the destination region or location
# use AWData to specify if it's a region or location, and then put the rules in the second parameter if any
# add item names used within rules to the names.py file if any are missing
# reason: we will probably change the names of things, so this'll make it easier
# if you want to add something like an event to a rule, do so, that's fine
# this is to set them apart from the rest for now, just making it easier as we write it initially
# the rules are formatted such that [[wand], [disc, remote]] means you need wand OR you need disc + remote
traversal_requirements: Dict[str, Dict[str, AWData]] = {
    bird_area: {
        fish_upper:
            AWData(AWType.region),
        bear_area:
            AWData(AWType.region),
        dog_area:
            AWData(AWType.region),
        dog_upper:
            AWData(AWType.region),
        bird_capybara_waterfall:
            AWData(AWType.region, [[iname.disc], [iname.bubble_short]]),
        lname.stamp_chest:
            AWData(AWType.location),
        lname.flute_chest:
            AWData(AWType.location, [["8 Eggs"]]),
        lname.duckarabbit:  # edit rule if we shuffle songs
            AWData(AWType.location, [[iname.flute]]),
        lname.bunny_mural:
            AWData(AWType.location, [[iname.remote]]),
    },
    bird_capybara_waterfall: {
        "Sweet Egg Chest":
            AWData(AWType.location),
    },

    starting_area: {
        starting_after_ghost:  # it would feel weird to call this the central area imo
            AWData(AWType.region, [[iname.firecrackers]]),  # not sure if randoing firecrackers yet
        candle_area:
            AWData(AWType.region, [["Light All Candles"]]),  # turn this into an event later
        s_disc_area:
            AWData(AWType.region, [[iname.s_medal, iname.bubble], [iname.s_medal, iname.disc]]),
        "Clover Egg Chest":  # in room where you see the status of the candles
            AWData(AWType.location),
        lname.ceiling_match_start:
            AWData(AWType.location),
        lname.face_bunny:
            AWData(AWType.location, [[iname.flute]]),
        fast_travel_fake:
            AWData(AWType.region, [[iname.flute]]),
    },
    starting_after_ghost: {
        bird_area:
            AWData(AWType.region),
        lname.first_candle:
            AWData(AWType.location, [[iname.match]]),  # idk if we're even doing these
        "Gorgeous Egg Chest":  # up and right of the candle
            AWData(AWType.location),
        lname.map_chest:
            AWData(AWType.location),
    },

    fish_upper: {
        # todo, find alternate routes directly into fish_west not through bwand pit. Probably yoyo and top?
        lname.fish_mural_match:  # right at the start, just some platforming
            AWData(AWType.location),
        lname.fish_bunny:
            AWData(AWType.location, [[iname.flute]]),
        # todo: upper right of fish mural
        # upper right of first bubble room leads to a door that requires a button hit on both sides
        "Mystic Egg Chest":  # avoid the fireball thrower, hit some buttons
            AWData(AWType.location),
        "Great Egg Chest":  # east end of the crane room
            AWData(AWType.location, [[iname.bubble_short], [iname.disc]]),  # TODO: verify you can do this with just one disc
        "Normal Egg Chest":  # hidden wall in lower left of first bubble room
            AWData(AWType.location),
        "Dazzle Egg Chest":  # little obstacle course, feels like the bubble jump tutorial?
            AWData(AWType.location, [[iname.bubble_short]]),
        fish_tube_room:  # enter at the save room fish pipe, the rooms with all the fish pipes
            AWData(AWType.region, [[iname.bubble]]),
        # todo: item in spike room under save room

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
        "Ancient Egg Chest":  # one room up and left of save point, vines in top right
            AWData(AWType.location, [[iname.bubble]]),  # todo: check if you can get here with disc
        fish_lower:  # bubble to go down, disc or remote to activate switches TODO: Check if passing stalagtites after save is possible with nothing
            AWData(AWType.region, [[iname.remote, iname.bubble], [iname.bubble, iname.disc]]),
    },
    fish_tube_room: {  # no location access rules because you need bubble wand to get here anyway
        "Friendship Egg Chest":  # the green pipe in the fish tube room
            AWData(AWType.location),  # tight timing with no midair bubble jumps
        "Magic Egg Chest":  # open the gate in the fish tube room
            AWData(AWType.location),
    },
    fish_lower: {
        fish_west:
            AWData(AWType.region, [[]]),  # TODO: find item logic for going back up the chute
        fish_boss:  # disc is required to solve both the windbox puzzle and to cross the whale room
            AWData(AWType.region, [[iname.disc]]),
        bobcat_room:
            AWData(AWType.region, [[iname.top]]),
    },
    fish_boss: {
        bird_area:
            AWData(AWType.region),
        abyss:
            AWData(AWType.region, [[iname.top, iname.e_medal, iname.disc], [iname.top, iname.e_medal, iname.bubble]]),
    },
    bear_area: {
        lname.key_chinchilla:
            AWData(AWType.location),
        "Future Egg Chest":  # chinchilla on the moving platforms puzzle room
            AWData(AWType.location),
    },
    bear_chinchilla_song_room: {
        lname.chinchilla_vine_bunny:
            AWData(AWType.location),
        bear_area:
            AWData(AWType.region),
    },

    dog_area: {
        lname.disc_spot:
            AWData(AWType.location),  # todo: figure out what to do for this
        lname.dog_candle_dark:
            AWData(AWType.location, [[iname.match]]),  # todo: figure out what we're doing for matches/candles
        dog_chinchilla_skull:
            AWData(AWType.region, [[iname.bubble]]),  # can get here without bubble jumps
        "Upside Down Egg Chest":  # upper right of switch platform room above second dog
            AWData(AWType.location, [[iname.bubble_short]]),  # todo: there's another way here from above?
        dog_at_mock_disc:  # you drop down to here, but can't get back up immediately
            AWData(AWType.region),
    },
    dog_at_mock_disc: {
        dog_area:  # can leave by hitting the button or jumping up to the ledge you came from
            AWData(AWType.region, [[iname.bubble], [iname.disc]]),
        "Sour Egg Chest":  # when escaping the dachsund, jump up and right out of the tunnel
            AWData(AWType.location),
        bird_area:  # after the sour egg chest, you escape to the central area
            AWData(AWType.region),
    },
    dog_chinchilla_skull: {
        "Red Egg Chest":
            AWData(AWType.location, [[iname.firecrackers]])  # use a firecracker
    },
    dog_upper: {
        dog_upper_past_lake:
            AWData(AWType.region, [[iname.disc_hop], [iname.bubble_long]]),  # maybe not long?
        dog_upper_above_switch_lines:
            AWData(AWType.region, [[iname.disc], [iname.remote]]),  # double check you can use remote in here
    },
    dog_upper_past_lake: {
        lname.dog_candle_switch_box:
            AWData(AWType.location),
        dog_upper_above_switch_lines:
            AWData(AWType.region, [[iname.can_distract_dogs]]),  # need to get past the 3 dogs
        lname.barcode_bunny:
            AWData(AWType.location, [[iname.flute]]),  # add song req if we're shuffling songs
        lname.mama_cha:
            AWData(AWType.location, [[iname.flute]]),  # add song req if we're shuffling songs
        # todo: floor is lava
    },
    dog_upper_above_switch_lines: {
        lname.dog_match_switch:  # in the little switch area
            AWData(AWType.location, [[iname.disc], [iname.remote]]),
        lname.dog_candle_switch:
            AWData(AWType.location, [[iname.match, iname.disc], [iname.match, iname.remote]]),
        "Depraved Egg Chest":  # in the little switch area, you need to take care of the ghost
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
        wave_room:  # take the bubble pipe by the dynamite, this is the really long pipe
            AWData(AWType.region, [[iname.bubble]]),
        # todo: get slink, go east past the room that needs it for a puzzle
    },

    wave_room: {
        "Jade Egg Chest":  # do the puzzle
            AWData(AWType.location),
        # todo: to the worm room
        bird_capybara_waterfall:  # take the very long pipe to the sweet egg room
            AWData(AWType.region, [[iname.bubble]]),
    },

    fast_travel: {
        starting_area:
            AWData(AWType.region, [[iname.flute]]),
        fish_west:
            AWData(AWType.region, [[iname.flute]]),
    },

    fast_travel_fake: {
        fast_travel:
            AWData(AWType.region),  # probably never randomizing fast travel song, so no rule
        bear_chinchilla_song_room:
            AWData(AWType.region, [[iname.song_chinchilla]])
    },
}
