from typing import Dict, List, Set, NamedTuple
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
starting_area = "Squirrel Main"
s_disc_area = "Squirrel S. Disc Area"
starting_after_ghost = "Squirrel After Ghost"
fast_travel = "Fast Travel Room"
central_area = "Central Area"
candle_area = "Squirrel Candle Area"
fish_area = "Fish Main"


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
        fish_area:
            AWData(AWType.region, [[iname.flute]]),
    },
    central_area: {
        fish_area:
            AWData(AWType.region),
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

    },
    starting_after_ghost: {
        central_area:
            AWData(AWType.region),
        lname.first_candle:
            AWData(AWType.location, [[iname.match]]),  # idk if we're even doing these
        "Gorgeous Egg":  # up and right of the candle
            AWData(AWType.location),
        lname.map_chest:
            AWData(AWType.location),
    },
    fish_area: {
        lname.fish_mural_match:  # right at the start, just some platforming
            AWData(AWType.location),
        lname.fish_bunny:
            AWData(AWType.location, [[iname.flute]]),
        # todo: upper right of fish mural
        # todo: upper right of first bubble room
        "Mystic Egg":  # avoid the fireball thrower, hit some buttons
            AWData(AWType.location),
        # todo: lower right of first bubble room
        "Normal Egg":  # hidden wall in lower left of first bubble room
            AWData(AWType.location),
        # todo: after fan room, little obstacle course with vines at top left
        # todo: fish pipe in save room
        # todo: upper left of save room, maybe the spikes too?
        # todo: item in spike room under save room
        lname.b_wand_chest:  # after seahorse room, need warp to start or b. wand to escape
            AWData(AWType.location),
    }
}
