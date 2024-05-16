from dataclasses import dataclass

from Options import DefaultOnToggle, Toggle, StartInventoryPool, Choice, Range, TextChoice, PerGameCommonOptions


class EggsNeeded(Range):
    """
    How many Eggs you need to do the Egg Song.
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


class BubbleJumping(Toggle):
    """
    Include using the standard Bubble Wand and chaining bubble jumps together in logic.
    The BB Wand does not put anything additional in logic with this option on.
    """
    internal_name = "bubble_jumping"
    display_name = "Bubble Jumping"


@dataclass
class AnimalWellOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    eggs_needed: EggsNeeded
    bunnies_as_checks: BunniesAsChecks
    candle_checks: CandleChecks
    bubble_jumping: BubbleJumping
