"""
game logic and state management on top of raw storage
"""

from supabase import Client

from .models import Tournament, Match, Move, Gesture, MatchState, TournamentState
from .storage import get_current_tournament

# constants
ROUND_START = 18000  # midnight EST
ROUND_DURATION = 86400


def current_round(start: int, current: int) -> int:
    # TODO
    return 0


def round_size(total: int, round_: int) -> int:
    # TODO
    # note: return 0 if over
    return 0


def remaining_users(tournament: int, total: int, round_: int, settled: int) -> int:
    # TODO
    return 0


def match_slot(total: int, round_: int, fid: int) -> int:
    # TODO
    return 0


def parent_slots(round_: int, slot: int) -> (int, int):
    # TODO
    return 0, 1


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
