from typing import Dict, List, Set, NamedTuple
from enum import IntEnum


# makes it more convenient to put together imo
class AWType(IntEnum):
    location = 1
    region = 2


class AWData(NamedTuple):
    type: int  # location or region
    rules: List[List[str]] = []  # how to access it


# todo: move this to a constants file or something later?
firecrackers = "Firecrackers"
disc = "Disc"
flute = "Flute"
bubble = "Bubble Wand"
bubble_short = "Bubble Wand - Short Range"  # small amount of bubble jumps, reasonable with just wand
bubble_long = "BB Wand"  # large amount of jumps, reasonable with BB wand
slink = "Slink"
yoyo = "Yo-Yo"
lantern = "Lantern"
uv = "UV Lantern"
top = "Top"
wheel = "Wheel"
remote = "Remote"
ball = "Bouncy Ball"
m_disc = "Mock Disc"
e_medal = "E Medal"
k_medal = "K Medal"
s_medal = "S Medal"


# instructions for contributors:
# the outer string is the name of the origin region
# the inner string is the name of the destination region or location
# use AWData to specify if it's a region or location, and then put the rules in the second parameter if any
# add item names used within rules to the floating variables above
# reason: we will probably change the names of things, so this'll make it easier
# if you want to add something like an event to a rule, don't add it to the variables above, just write out the string in quotes
# this is to set them apart from the rest for now, just making it easier as we write it initially
traversal_requirements: Dict[str, Dict[str, AWData]] = {
    "Starting Area": {
        "Central Area":
            AWData(AWType.region, [[firecrackers]),  # needed to get past ghost, not sure if randomizing this yet?
        "Candle Room":
            AWData(AWType.region, [["Light All Candles"]]),  # turn this into an event later
        "Ceiling Match":  # rename, this is the match that everyone apparently got last
            AWData(AWType.location),
    }
}
