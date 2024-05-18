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
candle_area = "Squirrel Candle Area"
fish_area = "Fish Main"
fish_west = "Fish West"  # after the b. wand chest, rename
fish_tube_room = "Fish Tube Room"  # rename?
bear_area = "Bear Main"
bear_chinchilla_song_room = "Bear Chinchilla Song Room"  # where the bunny is

# instructions for contributors:
# the outer string is the name of the origin region
# the inner string is the name of the destination region or location
# use AWData to specify if it's a region or location, and then put the rules in the second parameter if any
# add item names used within rules to the names.py file if any are missing
# reason: we will probably change the names of things, so this'll make it easier
# if you want to add something like an event to a rule, do so, that's fine
# this is to set them apart from the rest for now, just making it easier as we write it initially
traversal_requirements: Dict[str, Dict[str, AWData]] = {
    fast_travel: {
        starting_area:
            AWData(AWType.region, [[iname.flute]]),
        fish_west:
            AWData(AWType.region, [[iname.flute]]),
    },
    bird_area: {
        fish_area:
            AWData(AWType.region),
        bear_area:
            AWData(AWType.region),
        lname.stamp_chest:
            AWData(AWType.location),
        lname.flute_chest:
            AWData(AWType.location, [["8 Eggs"]]),
        lname.duckarabbit:  # edit rule if we shuffle songs
            AWData(AWType.location, [[iname.flute]]),
        lname.bunny_mural:
            AWData(AWType.location, [[iname.remote]]),
    },
    starting_area: {
        starting_after_ghost:  # it would feel weird to call this the central area imo
            AWData(AWType.region, [[iname.firecrackers]]),  # not sure if randoing firecrackers yet
        candle_area:
            AWData(AWType.region, [["Light All Candles"]]),  # turn this into an event later
        s_disc_area:
            AWData(AWType.region, [[iname.s_medal, iname.bubble], [iname.s_medal, iname.disc]]),
        "Clover Egg":  # in room where you see the status of the candles
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
        "Gorgeous Egg":  # up and right of the candle
            AWData(AWType.location),
        lname.map_chest:
            AWData(AWType.location),
    },
    fish_area: {
        fish_west:
            AWData(AWType.region, [[iname.bubble]]),  # todo: check what else can be used for this connection
        lname.fish_mural_match:  # right at the start, just some platforming
            AWData(AWType.location),
        lname.fish_bunny:
            AWData(AWType.location, [[iname.flute]]),
        # todo: upper right of fish mural
        # upper right of first bubble room leads to a door that requires a button hit on both sides
        "Mystic Egg":  # avoid the fireball thrower, hit some buttons
            AWData(AWType.location),
        "Great Egg":  # east end of the crane room
            AWData(AWType.location, [[iname.bubble_short], [iname.disc]]),  # verify you can do this with just one disc
        "Normal Egg":  # hidden wall in lower left of first bubble room
            AWData(AWType.location),
        "Dazzle Egg":  # little obstacle course, feels like the bubble jump tutorial?
            AWData(AWType.location, [[iname.bubble_short]]),
        fish_tube_room:  # enter at the save room fish pipe, the rooms with all the fish pipes
            AWData(AWType.region, [[iname.bubble]]),
        # todo: item in spike room under save room
        lname.b_wand_chest:  # after seahorse room, need warp to start or b. wand to escape
            AWData(AWType.location),
    },
    fish_west: {
        "Ancient Egg":  # one room up and left of save point, vines in top right
            AWData(AWType.location, [[iname.bubble]]),  # todo: check if you can get here with disc
        # todo: to the left of the fast travel fish room
    },
    fish_tube_room: {  # no location access rules because you need bubble wand to get here anyway
        "Friendship Egg":  # the green pipe in the fish tube room
            AWData(AWType.location),  # tight timing with no midair bubble jumps
        "Magic Egg":  # open the gate in the fish tube room
            AWData(AWType.location),
    },
    bear_area: {
        lname.key_chinchilla:
            AWData(AWType.location),
        "Future Egg":  # chinchilla on the moving platforms puzzle room
            AWData(AWType.location),
    },
    bear_chinchilla_song_room: {
        lname.chinchilla_vine_bunny:
            AWData(AWType.location),
        bear_area:
            AWData(AWType.region),
    },
    fast_travel_fake: {
        fast_travel:
            AWData(AWType.region),  # probably never randomizing fast travel song, so no rule
        bear_chinchilla_song_room:
            AWData(AWType.region, [[iname.song_chinchilla]])
    },
}
