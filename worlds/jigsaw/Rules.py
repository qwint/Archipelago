import math
from collections import Counter, defaultdict
from typing import List, Optional

from BaseClasses import MultiWorld

from worlds.generic.Rules import set_rule


def set_jigsaw_rules(world: MultiWorld, player: int, nx: int, ny: int):
    """
    Sets rules on reaching matches
    """

    for location in world.get_locations(player):
        set_rule(
            location,
            lambda state, curmatches=location.nmatches, player=player: state._jc_matches_count(player) >= curmatches,
        )
        
def count_number_of_matches_state(state, player, nx, ny):
    pieces = [int(m[13:]) for m in state.prog_items[player]]
    t = count_number_of_matches_pieces(pieces, nx, ny)
    return t
        
def count_number_of_matches_pieces(pieces, nx, ny):
    len_pieces_groups = group_groups(pieces, nx, ny)
    return len(pieces) - len_pieces_groups

def group_groups(pieces, nx, ny):
    pieces_set = set(pieces)
    all_groups = 0
    
    while pieces_set:
        current_group = [pieces_set.pop()]
        ind = 0
        
        while ind < len(current_group):
            piece = current_group[ind]
            ind += 1
            candidates = []
            if piece > nx:
                candidates.append(piece - nx)
            if piece < nx * (ny - 1):
                candidates.append(piece + nx)
            if piece % nx != 1:
                candidates.append(piece - 1)
            if piece % nx != 0:
                candidates.append(piece + 1)
                
            movable_candidates = [c for c in candidates if c in pieces_set]
            current_group += movable_candidates
            pieces_set.difference_update(movable_candidates)
        all_groups += 1
    return all_groups
