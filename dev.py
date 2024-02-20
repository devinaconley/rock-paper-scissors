"""
dev script for image rendering
"""

import time

from api.warpcast import get_user
from api.models import User, Match, Result, MatchStatus, MatchState, Gesture
from api.render import render_match
from api.storage import get_supabase, get_matches_count


def main():
    # s = get_supabase()
    # res = get_matches_count(s, 1, 7, result=Result.PLAYED)
    # print(res)
    # return

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


if __name__ == '__main__':
    main()
