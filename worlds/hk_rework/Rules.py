from typing import NamedTuple


class CostTerm(NamedTuple):
    term: str
    option: str
    singular: str
    plural: str
    weight: int  # CostSanity
    sort: int


cost_terms = {x.term: x for x in (
    CostTerm("RANCIDEGGS", "Egg", "Rancid Egg", "Rancid Eggs", 1, 3),
    CostTerm("GRUBS", "Grub", "Grub", "Grubs", 1, 2),
    CostTerm("ESSENCE", "Essence", "Essence", "Essence", 1, 4),
    CostTerm("CHARMS", "Charm", "Charm", "Charms", 1, 1),
    CostTerm("GEO", "Geo", "Geo", "Geo", 8, 9999),
)}


def _hk_nail_combat(state, player) -> bool:
    return state.has_any({'LEFTSLASH', 'RIGHTSLASH', 'UPSLASH'}, player)


def _hk_option(world, option_name: str) -> int:
    return getattr(world.options, option_name).value


def _hk_can_beat_thk(state, player) -> bool:
    return (
        state.has('Opened_Black_Egg_Temple', player)
        and (state.count('FIREBALL', player) + state.count('SCREAM', player) + state.count('QUAKE', player)) > 1
        and _hk_nail_combat(state, player)
        and (
            state.has_any({'LEFTDASH', 'RIGHTDASH'}, player)
            or _hk_option(state.multiworld.worlds[player], 'ProficientCombat')
        )
        and state.has('FOCUS', player)
    )


def _hk_siblings_ending(state, player) -> bool:
    return _hk_can_beat_thk(state, player) and state.has("CHARM36", player, 3)


def _hk_can_beat_radiance(state, player) -> bool:
    return (
        state.has('Opened_Black_Egg_Temple', player)
        and _hk_nail_combat(state, player)
        and state.has("CHARM36", player, 3)
        and state.has('DREAMNAIL', player)
        and (
            (state.has('LEFTCLAW', player) and state.has('RIGHTCLAW', player))
            or state.has('WINGS', player)
        )
        and (state.count('FIREBALL', player) + state.count('SCREAM', player) + state.count('QUAKE', player)) > 1
        and (
            (state.has('LEFTDASH', player, 2) and state.has('RIGHTDASH', player, 2))  # Both Shade Cloaks
            or (_hk_option(state.multiworld.worlds[player], 'ProficientCombat') and state.has('QUAKE', player))  # or Dive
        )
    )
