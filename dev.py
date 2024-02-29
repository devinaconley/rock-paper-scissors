"""
dev script for image rendering
"""

import time

import requests

from api.warpcast import get_user
from api.models import User, Match, Result, MatchStatus, MatchState, Gesture
from api.render import render_match, render_bracket
from api.storage import get_supabase, get_matches_count
from api.rps import get_final_bracket


def main():
    # render_test_match()
    render_test_bracket()
    # find_degen_matches()


def render_test_match():
    now = time.time()
    u0 = get_user(8268)
    u1 = get_user(12224)
    m = Match(
        id='1234', created=now, updated=now, tournament=1, round=5, slot=33,
        user0=u0.fid, user1=u1.fid,
        result=Result.PENDING, winner=None, loser=None
    )
    s = MatchState(
        match='1234', turn=1, status=MatchStatus.DRAW, winner=None, loser=None,
        history0=[Gesture.ROCK],
        history1=[Gesture.ROCK]
    )
    is_user0 = True
    # u1 = None
    print(u0)
    print(u1)
    render_match(m, u0 if is_user0 else u1, u1 if is_user0 else u0, m.round, s, 7215)


def render_test_bracket():
    s = get_supabase()
    bracket = get_final_bracket(s, 5, 32)
    print(bracket)
    users = {}
    for _, r in bracket.items():
        for _, m in r.items():
            if m.user0 not in users:
                users[m.user0] = get_user(m.user0)
            if m.user1 not in users:
                users[m.user1] = get_user(m.user1)

    render_bracket(bracket, users, 1)


def find_degen_matches():
    tournament = 1
    round_ = 13
    base = 'https://tournament.network/match'
    base_degen = 'https://degen.tips/api/airdrop2'
    for i in range(0, 32):
        print(i)
        slot = f'{base}/{tournament}/{round_}/{i}'
        while 1:
            r = requests.get(slot)
            if r.status_code == 200:
                break
        body = r.json()
        # print(body)
        fid0 = body['match']['user0']
        fid1 = body['match']['user1']
        slot = body['match']['slot']

        r = requests.get(f'{base_degen}/tip-allowance?fid={fid0}')
        b0 = r.json()
        if not b0:
            continue
        addr0 = b0[0]['wallet_address']
        r = requests.get(f'{base_degen}/season1/points?address={addr0}')
        b0 = r.json()
        if not b0:
            continue
        p0 = int(b0[0]['points'])
        # print(p0)
        if p0 < 1000:
            continue

        r = requests.get(f'{base_degen}/tip-allowance?fid={fid1}')
        b1 = r.json()
        if not b1:
            continue
        addr1 = b1[0]['wallet_address']
        r = requests.get(f'{base_degen}/season1/points?address={addr1}')
        b1 = r.json()
        if not b1:
            continue
        p1 = int(b1[0]['points'])
        # print(p1)
        if p1 < 1000:
            continue

        print(f'DEGEN MATCHUP: {slot}, {fid0} v. {fid1}, points {p0} {p1}')


if __name__ == '__main__':
    main()
