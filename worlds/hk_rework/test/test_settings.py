import typing

from .bases import HKTestBase, HKGoalBase


class TestGoalAny(HKGoalBase):
    options: typing.ClassVar[dict[str, str]] = {
        "Goal": "any",
    }


class TestGoalHollowknight(HKGoalBase):
    options: typing.ClassVar[dict[str, str]] = {
        "Goal": "hollowknight",
    }


class TestGoalSiblings(HKGoalBase):
    options: typing.ClassVar[dict[str, str]] = {
        "Goal": "siblings",
    }


class TestGoalRadiance(HKGoalBase):
    options: typing.ClassVar[dict[str, str]] = {
        "Goal": "radiance",
    }

# TODO put these back when implemented again
# class TestGoalGodhome(HKGoalBase):
#     options: typing.ClassVar[dict[str, str]] = {
#         "Goal": "godhome",
#     }


# class TestGoalGodhomeFlower(HKGoalBase):
#     options: typing.ClassVar[dict[str, str]] = {
#         "Goal": "godhome_flower",
#     }


class TestRandomizeAll(HKTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "Goal": "any",

        "RandomizeDreamers": True,
        "RandomizeSkills": True,
        "RandomizeFocus": True,
        "RandomizeSwim": True,
        "RandomizeCharms": True,
        "RandomizeKeys": True,
        "RandomizeMaskShards": True,
        "RandomizeVesselFragments": True,
        "RandomizeCharmNotches": True,
        "RandomizePaleOre": True,
        "RandomizeGeoChests": True,
        "RandomizeJunkPitChests": True,
        "RandomizeRancidEggs": True,
        "RandomizeRelics": True,
        "RandomizeWhisperingRoots": True,
        "RandomizeBossEssence": True,
        "RandomizeGrubs": True,
        "RandomizeMimics": True,
        "RandomizeMaps": True,
        "RandomizeStags": True,
        "RandomizeLifebloodCocoons": True,
        "RandomizeGrimmkinFlames": True,
        "RandomizeJournalEntries": True,
        "RandomizeNail": True,
        "RandomizeGeoRocks": True,
        "RandomizeBossGeo": True,
        "RandomizeSoulTotems": True,
        "RandomizeLoreTablets": True,
        "RandomizeElevatorPass": True,
    }


class TestRandomizeNone(HKTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "Goal": "any",

        "RandomizeDreamers": False,
        "RandomizeSkills": False,
        "RandomizeFocus": False,
        "RandomizeSwim": False,
        "RandomizeCharms": False,
        "RandomizeKeys": False,
        "RandomizeMaskShards": False,
        "RandomizeVesselFragments": False,
        "RandomizeCharmNotches": False,
        "RandomizePaleOre": False,
        "RandomizeGeoChests": False,
        "RandomizeJunkPitChests": False,
        "RandomizeRancidEggs": False,
        "RandomizeRelics": False,
        "RandomizeWhisperingRoots": False,
        "RandomizeBossEssence": False,
        "RandomizeGrubs": False,
        "RandomizeMimics": False,
        "RandomizeMaps": False,
        "RandomizeStags": False,
        "RandomizeLifebloodCocoons": False,
        "RandomizeGrimmkinFlames": False,
        "RandomizeJournalEntries": False,
        "RandomizeNail": False,
        "RandomizeGeoRocks": False,
        "RandomizeBossGeo": False,
        "RandomizeSoulTotems": False,
        "RandomizeLoreTablets": False,
        "RandomizeElevatorPass": False,
    }


class TestUnshuffledRandomizeNone(HKTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "AddUnshuffledLocations": True,
        "Goal": "any",

        "RandomizeDreamers": False,
        "RandomizeSkills": False,
        "RandomizeFocus": False,
        "RandomizeSwim": False,
        "RandomizeCharms": False,
        "RandomizeKeys": False,
        "RandomizeMaskShards": False,
        "RandomizeVesselFragments": False,
        "RandomizeCharmNotches": False,
        "RandomizePaleOre": False,
        "RandomizeGeoChests": False,
        "RandomizeJunkPitChests": False,
        "RandomizeRancidEggs": False,
        "RandomizeRelics": False,
        "RandomizeWhisperingRoots": False,
        "RandomizeBossEssence": False,
        "RandomizeGrubs": False,
        "RandomizeMimics": False,
        "RandomizeMaps": False,
        "RandomizeStags": False,
        "RandomizeLifebloodCocoons": False,
        "RandomizeGrimmkinFlames": False,
        "RandomizeJournalEntries": False,
        "RandomizeNail": False,
        "RandomizeGeoRocks": False,
        "RandomizeBossGeo": False,
        "RandomizeSoulTotems": False,
        "RandomizeLoreTablets": False,
        "RandomizeElevatorPass": False,
    }


class TestSplitAll(HKTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "Goal": "any",

        "SplitCrystalHeart": True,
        "SplitMothwingCloak": True,
        "SplitMantisClaw": True,
    }


class TestCostsAll(HKTestBase):
    options: typing.ClassVar[dict[str, str]] = {
        "Goal": "any",

        "EggShopSlots": 9,
        "SlyShopSlots": 9,
        "SlyKeyShopSlots": 9,
        "IseldaShopSlots": 9,
        "SalubraShopSlots": 9,
        "SalubraCharmShopSlots": 9,
        "LegEaterShopSlots": 9,
        "GrubfatherRewardSlots": 9,
        "SeerRewardSlots": 9,
        "ExtraShopSlots": 9,
        "CostSanity": True,
        "CostSanityHybridChance": 1,
        "CostSanityEggWeight": 1,
        "CostSanityGrubWeight": 1,
        "CostSanityEssenceWeight": 1,
        "CostSanityCharmWeight": 1,
        "CostSanityGeoWeight": 1,
    }

# RandomizeDreamers,
# RandomizeSkills,
# RandomizeFocus,
# RandomizeSwim,
# RandomizeCharms,
# RandomizeKeys,
# RandomizeMaskShards,
# RandomizeVesselFragments,
# RandomizeCharmNotches,
# RandomizePaleOre,
# RandomizeGeoChests,
# RandomizeJunkPitChests,
# RandomizeRancidEggs,
# RandomizeRelics,
# RandomizeWhisperingRoots,
# RandomizeBossEssence,
# RandomizeGrubs,
# RandomizeMimics,
# RandomizeMaps,
# RandomizeStags,
# RandomizeLifebloodCocoons,
# RandomizeGrimmkinFlames,
# RandomizeJournalEntries,
# RandomizeNail,
# RandomizeGeoRocks,
# RandomizeBossGeo,
# RandomizeSoulTotems,
# RandomizeLoreTablets,
# RandomizeElevatorPass,
# StartLocation,
# Goal,
# WhitePalace,
# SplitCrystalHeart,
# SplitMothwingCloak,
# SplitMantisClaw,
# AddUnshuffledLocations,


# # not useful without more asserts
# PreciseMovement,
# ProficientCombat,
# BackgroundObjectPogos,
# EnemyPogos,
# ObscureSkips,
# ShadeSkips,
# InfectionSkips,
# FireballSkips,
# SpikeTunnels,
# AcidSkips,
# DamageBoosts,
# DangerousSkips,
# DarkRooms,
# ComplexSkips,
# DifficultSkips,
# RemoveSpellUpgrades,
# MinimumGeoPrice,
# MaximumGeoPrice,
# MinimumGrubPrice,
# MaximumGrubPrice,
# MinimumEssencePrice,
# MaximumEssencePrice,
# MinimumCharmPrice,
# MaximumCharmPrice,
# RandomCharmCosts,
# PlandoCharmCosts,
# MinimumEggPrice,
# MaximumEggPrice,
# EggShopSlots,
# SlyShopSlots,
# SlyKeyShopSlots,
# IseldaShopSlots,
# SalubraShopSlots,
# SalubraCharmShopSlots,
# LegEaterShopSlots,
# GrubfatherRewardSlots,
# SeerRewardSlots,
# ExtraShopSlots,
# CostSanity,
# CostSanityHybridChance,
# CostSanityEggWeight,
# CostSanityGrubWeight,
# CostSanityEssenceWeight,
# CostSanityCharmWeight,
# CostSanityGeoWeight,

# # should be ok not testing
# StartingGeo,
# DeathLink,
# DeathLinkShade,
# DeathLinkBreaksFragileCharms,
# ExtraPlatforms,
