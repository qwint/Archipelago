from dataclasses import dataclass

from Options import DefaultOnToggle, Toggle, StartInventoryPool, Choice, Range, TextChoice, PerGameCommonOptions


class Goal(Choice):
    """
    What you need to do to beat the game.
    Fireworks requires you to get the 4 flames and defeat the Manticore.
    Bunny Land requires you to find the 65th Egg, bring it to the incubator, and leave the Well.
    Egg Hunt requires you to collect the amount of eggs you need to open the 4th Egg Door, then open the chest inside.
    """
    internal_name = "goal"
    display_name = "Goal"
    option_fireworks: 1
    option_bunny_land: 2
    option_egg_hunt: 3
    default: 0


class EvilEggLocation(Choice):
    """
    Choose whether the 65th Egg is shuffled into the multiworld item pool or placed in its vanilla location, requiring opening the 4th Egg Door to access it.
    """
    internal_name = "65th_egg_location"
    display_name = "65th Egg Location"
    option_randomized: 0
    option_vanilla: 1
    default: 1


class EggsNeeded(Range):
    """
    How many Eggs you need to open the 4th Egg Door.
    """
    internal_name = "eggs_needed"
    display_name = "Eggs Required"
    range_start = 8
    range_end = 64
    default = 48


class BunniesAsChecks(Choice):
    """
    Include the secret bunnies as checks.
    """
    internal_name = "bunnies_as_checks"
    display_name = "Bunnies as Checks"
    option_off = 0
    option_exclude_tedious = 1
    option_all_bunnies = 2
    default = 0


class CandleChecks(DefaultOnToggle):
    """
    Lighting each of the candles sends a check.
    """
    internal_name = "candle_checks"
    display_name = "Candle Checks"


class BubbleJumping(Choice):
    """
    Include using the standard Bubble Wand and chaining bubble jumps together in logic.
    Exclude Long Chains makes it so you may be required to chain a few bubble jumps before landing.
    """
    internal_name = "bubble_jumping"
    display_name = "Bubble Jumping"
    option_off = 0
    option_exclude_long_chains = 1
    option_on = 2
    default = 1


class DiscRiding(Toggle):
    """
    Include jumping onto the disc without letting it bounce off of a wall first in logic.
    Exception: The bunny that requires this technique.
    """
    internal_name = "disc_riding"
    display_name = "Midair Disc Riding"


@dataclass
class AnimalWellOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    goal: Goal
    eggs_needed: EggsNeeded
    evil_egg_location: EvilEggLocation
    bunnies_as_checks: BunniesAsChecks
    candle_checks: CandleChecks
    bubble_jumping: BubbleJumping
    disc_riding: DiscRiding
