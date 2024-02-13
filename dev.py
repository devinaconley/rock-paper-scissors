"""
dev script for image rendering
"""

import time

from api.warpcast import get_user
from api.models import User, Match, Result, MatchStatus
from api.render import render_match


def main():
    now = time.time()
    u0 = get_user(8268)
    u1 = get_user(13724)
    m = Match(id='1234', created=now, updated=now, tournament=1, round=5, slot=33, user0=u0.fid, user1=u1.fid,
              result=Result.PLAYED, winner=u0.fid)
    is_user0 = True
    print(u0)
    print(u1)
    render_match(m, u0 if is_user0 else u1, u1 if is_user0 else u0, m.round, 3, MatchStatus.USER_1_PLAYED)


if __name__ == '__main__':
    main()
