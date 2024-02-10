"""
methods to read from and write to postgres database
"""

# lib
import os

from dotenv import load_dotenv
from supabase import create_client, Client
from postgrest.types import CountMethod

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


def get_matches_count(supabase: Client, tournament: int, round_: int, result: Result = None) -> int:
    q = supabase.table('match').select(count=CountMethod.exact).eq('tournament', tournament).eq('round', round_)
    if result is not None:
        q = q.eq('result', result.value)
    res = q.execute()
    print(res)
    return res.count


def get_match(supabase: Client, tournament: int, round_: int, slot: int) -> Match:
    match_id = f'{tournament}_{round_}_{slot}'
    res = supabase.table('match').select('*').eq('id', match_id).execute()
    print(f'get_match: {match_id}')
    print(res)
    if not res.data:
        return None
    return Match(**res.data[0])


def set_match(supabase: Client, match: Match):
    match_id = f'{match.tournament}_{match.round}_{match.slot}'
    if match.id != match_id:
        print(f'warning: match id was wrong {match.id} {match_id}, fixing...')
        match.id = match_id
    body = match.model_dump(mode='json', exclude_none=True)
    print(body)
    res = supabase.table('match').upsert(body).execute()
    print(f'set match result {res}')
    return res


def get_moves(supabase: Client, match: str) -> list[Move]:
    # TODO
    return []


def set_move(supabase: Client, match: str, fid: int, turn: int, gesture: Gesture):
    # TODO
    pass
