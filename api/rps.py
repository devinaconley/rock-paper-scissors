"""
game logic and state management on top of raw storage
"""
import math

from supabase import Client

from .models import Tournament, Match, Move, Gesture, MatchState, Result, TournamentState
from .storage import get_current_tournament, get_matches_count, get_match, get_moves, set_match

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
    return get_matches_count(supabase, tournament, round_, result=Result.PLAYED)


def get_match_user(supabase: Client, now: int, tournament: int, total: int, round_: int, fid: int) -> Match:
    # compute match slot and parent slots
    slot = match_slot(total, round_, fid)

    # get or lazily create match
    m = get_match_slot(supabase, now, tournament, total, round_, round_, slot)
    print(m)

    # lazy scoring to settle match
    m = update_match_result(supabase, now, round_, m)
    print(m)

    return m


def get_match_slot(
        supabase: Client,
        now: int,
        tournament: int,
        total: int,
        curr_round: int,
        round_: int,
        slot: int
) -> Match:
    # get match if exists
    print(f'get match slot {round_} {slot}')
    m = get_match(supabase, tournament, round_, slot)
    if m is None:
        # lazy init
        if round_ == 0:
            # at beginning
            sz = round_size(total, 0)
            fid0 = slot + 1
            fid1 = sz - slot
            if fid1 > total:
                fid1 = 0  # bye

        else:
            # get users by previous match results
            a, b = parent_slots(total, round_, slot)

            # recurse and backfill as needed
            ma = get_match_slot(supabase, now, tournament, total, curr_round, round_ - 1, a)
            mb = get_match_slot(supabase, now, tournament, total, curr_round, round_ - 1, b)
            if ma.winner is None:
                raise Exception(f'winner missing for match {ma.id}')
            if mb.winner is None:
                raise Exception(f'winner missing for match {mb.id}')

            fid0 = ma.winner
            fid1 = mb.winner

        m = Match(
            id=f'{tournament}_{round_}_{slot}',
            created=now,
            updated=now,
            tournament=tournament,
            round=round_,
            slot=slot,
            user0=fid0,
            user1=fid1,
            result=Result.PENDING
        )

        if fid1 == 0:
            # settle bye
            m.winner = fid0
            m.loser = fid1
            m.result = Result.BYE

        set_match(supabase, m)

    return update_match_result(supabase, now, curr_round, m)


def update_match_result(supabase: Client, now: int, round_: int, match: Match) -> Match:
    if match.winner is not None:
        # already scored
        return match

    # winner: check for explicit result, then check for draw, then check for uncontested play, then prefer lower fid
    moves = get_moves(supabase, match.id)

    if len(moves) == 0:
        if round_ == match.round:
            match.result = Result.PENDING
        else:
            match.winner = min(match.user0, match.user1)
            match.loser = max(match.user0, match.user1)
            match.result = Result.PASS
    else:
        # TODO process moves
        pass

    if match.result == Result.PENDING:
        return match  # nothing to update

    set_match(supabase, match)

    return match


def get_match_state(supabase: Client, match: str) -> MatchState:
    # TODO
    pass


def get_match_user_eliminated(supabase: Client, tournament: int, fid: int) -> Match:
    # TODO
    # convenience just to show user elimination details
    pass


def get_match_winner(supabase: Client, tournament: int, round_: int, slot: int) -> int:
    # TODO
    pass


def get_winner(supabase: Client, tournament: int) -> int:
    # TODO
    pass


def get_final_bracket(supabase: Client, tournament: int):
    # TODO
    # can probably implement later, won't be usable until the end
    pass


def get_tournament_state(supabase: Client, tournament: int, round_: int) -> TournamentState:
    # TODO
    pass
