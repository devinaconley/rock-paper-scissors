"""
game logic and state management on top of raw storage
"""
import math

from supabase import Client

from .models import Tournament, Match, Move, Gesture, MatchState, TournamentState
from .storage import get_current_tournament

# constants
ROUND_START = 18000  # midnight EST
ROUND_DURATION = 86400


def current_round(start: int, current: int) -> int:
    # get next increment for actual tournament start time
    days = math.ceil((start - ROUND_START) / ROUND_DURATION)
    t0 = ROUND_DURATION * days + ROUND_START

    if current < t0:
        return -1  # not started

    return (current - t0) // ROUND_DURATION  # first round = 0


def round_size(total: int, round_: int) -> int:
    if total < 2:
        raise ValueError('fewer than two people')
    if round_ < 0:
        raise ValueError(f'invalid round: {round_}')

    # find next power of 2
    total_rounds = math.ceil(math.log2(total))

    # split for each round passed
    sz = 2 ** (total_rounds - round_)

    if sz < 1:
        return 1  # tournament over
    return int(sz)


def remaining_users(total: int, round_: int, settled: int) -> int:
    return round_size(total, round_) - settled


def match_slot(total: int, round_: int, fid: int) -> int:
    # note: fid index starts at 1
    # need to match 1 vs N, 2 vs N-1, etc...
    if fid > total:
        raise ValueError(f'user too high: {fid}, total: {total}')
    if round_ < 0:
        raise ValueError(f'invalid round: {round_}')

    sz = round_size(total, 0)
    slot = fid - 1
    for i in range(round_ + 1):
        slot = slot if slot < sz / 2 else sz - slot - 1
        sz /= 2

    return int(slot)


def parent_slots(total: int, round_: int, slot: int) -> (int, int):
    if round_ < 1:
        raise ValueError(f'invalid round: {round_}')
    sz = round_size(total, round_)
    if slot >= sz / 2:
        raise ValueError(f'slot too high: {slot}, round size: {sz}')

    mirror = sz - slot - 1
    return slot, mirror


def get_round_settled(supabase: Client, tournament: int, round_: int) -> int:
    # TODO
    return 0


def get_match_user(supabase: Client, tournament: int, round_: int, fid: int) -> Match:
    # compute match slot and parent slots
    # get users by previous match results (recurse and backfill as needed)
    # winner: check for explicit result, then check for draw, then check for uncontested play, then prefer lower fid
    # lazy init of match object
    # lazy scoring to settle match
    # TODO
    pass


def get_match_state(supabase: Client, match: str) -> MatchState:
    # TODO
    pass


def get_match_user_last(supabase: Client, tournament: int, fid: int) -> Match:
    # TODO
    pass


def get_match_winner(supabase: Client, tournament: int, round_: int, slot: int) -> int:
    # TODO
    pass


def get_winner(supabase: Client, tournament: int) -> int:
    # TODO
    pass


def get_final_bracket(supabase: Client, tournament: int):
    # TODO
    pass


def get_tournament_state(supabase: Client, tournament: int, round_: int) -> TournamentState:
    # TODO
    pass
