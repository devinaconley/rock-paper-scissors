"""
methods to read from and write to postgres database
"""

# lib
import os

from dotenv import load_dotenv
from supabase import create_client, Client

# src
from .models import Tournament, Match, Result, Move, Gesture


def get_supabase() -> Client:
    if os.getenv('VERCEL_ENV') is None:
        load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    supabase = create_client(url, key)
    return supabase


def get_current_tournament(supabase: Client) -> Tournament:
    res = supabase.table('tournament').select('*').order('id', desc=True).limit(1).execute()
    if res.count == 0:
        raise Exception('could not get current tournament')
    return Tournament(**res.data[0])


def get_match(supabase: Client, tournament: int, round_: int, slot: int) -> Match:
    # TODO
    pass


def set_match(
        supabase: Client,
        tournament: int,
        round_: int,
        slot: int,
        user0: int,
        user1: int,
        winner: int = None,
        result: Result = None
):
    # TODO
    pass


def get_moves(supabase: Client, match: str) -> list[Move]:
    # TODO
    pass


def set_move(supabase: Client, match: str, fid: int, gesture: Gesture):
    # TODO
    pass
