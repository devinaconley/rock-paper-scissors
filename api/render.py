"""
dynamic image rendering for frames
"""

import datetime
import requests
import numpy as np
import cv2

from .models import Tournament, Match, MatchState, MatchStatus, User, Result
from .rps import ROUND_BUFFER

FONT = cv2.FONT_HERSHEY_SIMPLEX
PFP_SZ = 96


def render_home(tournament: int, total: int, round_: int, prize, remaining: int) -> bytes:
    # setup background
    im = cv2.imread('api/static/tournament.png')

    # stats
    x = 12
    im = cv2.putText(im, 'Farcaster rock paper scissors', (x, 30), FONT, 0.7, (0, 0, 0), 2)
    im = cv2.putText(im, f'tournament {tournament}', (x, 70), FONT, 0.7, (0, 0, 0), 1)
    im = cv2.putText(im, f'prize {prize}', (x, 100), FONT, 0.7, (0, 0, 0), 1)
    im = cv2.putText(im, f'round {round_}', (x, 130), FONT, 0.7, (0, 0, 0), 1)
    im = cv2.putText(im, f'{total} users entered', (x, 160), FONT, 0.7, (0, 0, 0), 1)
    im = cv2.putText(im, f'{remaining} competitors remain', (x, 190), FONT, 0.7, (0, 0, 0), 1)

    # message
    im = write_message(im, line0='Welcome to Farcaster rock paper scissors. Click below to play.', line1='Good luck!')

    # encode
    _, b = cv2.imencode('.png', im)
    return b.tobytes()


def render_message(line0: str = None, line1: str = None) -> bytes:
    # setup background
    im = cv2.imread('api/static/tournament.png')

    # message
    im = write_message(im, line0=line0, line1=line1)

    # encode
    _, b = cv2.imencode('.png', im)
    return b.tobytes()


def render_match(
        match: Match,
        user: User,
        opponent: User,
        round_: int,
        state: MatchState,
        remaining: int
) -> bytes:
    # setup background
    im = cv2.imread('api/static/match.png')

    # match data
    im = cv2.putText(im, f'round {round_}', (510, 15), FONT, 0.3, (0, 0, 0))
    im = cv2.putText(im, f'turn {state.turn}', (518, 25), FONT, 0.3, (0, 0, 0))
    im = cv2.putText(im, f'{datetime.timedelta(seconds=max(0, remaining))}', (510, 35), FONT, 0.3, (0, 0, 0))

    # player data
    name_user = strip_text(f'{user.displayName:.16s}')
    im = cv2.putText(im, name_user, (328, 158), FONT, 0.4, (0, 0, 0))
    im = cv2.putText(im, f'Fid.{user.fid}', (460, 158), FONT, 0.3, (0, 0, 0))
    try:
        pfp_user = get_pfp(user.pfp.url)
        x = 100
        y = 120
        im[y:y + PFP_SZ, x:x + PFP_SZ] = pfp_user
    except Exception as e:
        print(f'failed to render user pfp {user.fid} {e}')

    # opponent data
    if opponent is None:
        name_opp = 'BYE'
        im = cv2.putText(im, 'BYE', (45, 25), FONT, 0.4, (0, 0, 0))
        im = cv2.putText(im, 'Fid.0', (175, 25), FONT, 0.3, (0, 0, 0))
    else:
        name_opp = strip_text(f'{opponent.displayName:.16s}')
        im = cv2.putText(im, name_opp, (45, 25), FONT, 0.4, (0, 0, 0))
        im = cv2.putText(im, f'Fid.{opponent.fid}', (175, 25), FONT, 0.3, (0, 0, 0))
        try:
            pfp_opp = get_pfp(opponent.pfp.url)
            x = 360
            y = 20
            im[y:y + PFP_SZ, x:x + PFP_SZ] = pfp_opp
        except Exception as e:
            print(f'failed to render opponent pfp {user.fid} {e}')

    # TODO bonus features: health bar, loser drop, gif, emoji render

    # message
    if match.result == Result.PENDING:
        if state.status == MatchStatus.DRAW:
            msg = f'Draw! You both played {state.history0[-1].name}.'
            if remaining > ROUND_BUFFER:
                msg += ' Make your next move.'
        elif (user.fid == match.user0 and state.status == MatchStatus.USER_0_PLAYED) or (
                user.fid == match.user1 and state.status == MatchStatus.USER_1_PLAYED):
            msg = 'Waiting on your opponent.'
        elif (user.fid == match.user0 and state.status == MatchStatus.USER_1_PLAYED) or (
                user.fid == match.user1 and state.status == MatchStatus.USER_0_PLAYED):
            msg = 'Your opponent has played. Make a move!'
        else:
            # NEW
            msg = 'Play your move!'

        im = write_message(
            im,
            line0=f'Round {round_} matchup, {name_user} vs. {name_opp}.',
            line1=msg
        )

    elif match.result == Result.PLAYED:
        # get last gesture
        g_user = state.history0[-1]
        g_opp = state.history1[-1]
        if user.fid != match.user0:
            g_user, g_opp = g_opp, g_user
        # winning vs losing text
        if match.winner == user.fid:
            msg = f'You have defeated {name_opp} in round {round_}!'
        else:
            msg = f'You were knocked out by {name_opp} in round {round_}!'
        im = write_message(im, line0=f'Opponent played {g_opp.name} against your {g_user.name}.', line1=msg)

    elif match.result == Result.FORFEIT:
        if match.winner == user.fid:
            im = write_message(
                im,
                line0=f'Opponent did not play a move for turn {state.turn}.',
                line1=f'You have defeated {name_opp} in round {round_} by forfeit.'
            )
        else:
            im = write_message(
                im,
                line0=f'You did not play a move for turn {state.turn}.',
                line1=f'You lost to {name_opp} in round {round_} by forfeit.'
            )

    elif match.result == Result.DRAW:
        if match.winner == user.fid:
            im = write_message(
                im,
                line0=f'Match was a draw after {state.turn} turns!',
                line1=f'You have defeated {name_opp} in round {round_} by seniority.'
            )
        else:
            im = write_message(
                im,
                line0=f'Match was a draw after {state.turn} turns!',
                line1=f'You lost to {name_opp} in round {round_} by seniority.'
            )

    elif match.result == Result.PASS:
        if match.winner == user.fid:
            msg = f'You have defeated {name_opp} in round {round_} by seniority.'
        else:
            msg = f'You lost to {name_opp} in round {round_} by seniority.'
        im = write_message(im, line0=f'No contest.', line1=msg)

    elif match.result == Result.BYE:
        im = write_message(
            im,
            line0=f'You received a bye for round {round_}.',
            line1=f'Good luck in your next match.'
        )

    # cv2.imshow('debug', im)
    # cv2.waitKey(0)
    # return

    # encode
    _, b = cv2.imencode('.png', im)
    return b.tobytes()


def render_bracket(bracket: dict, users: dict[int, User], round_: int) -> bytes:
    # setup background
    im = cv2.imread('api/static/tournament.png')

    # draw bracket
    y0 = 20
    msg = None
    msg_dt = datetime.datetime.fromtimestamp(0)
    for i in range(5):
        x = 20 + i * 100
        dy = 12 * (2 ** i)
        for j in range(int(16 / 2 ** i)):
            y = y0 + j * dy
            # draw bracket lines
            gray = (175, 175, 175)
            im = cv2.line(im, (x, y), (x + 100, y), gray, 1)
            if j % 2 or i == 4:
                continue
            im = cv2.line(im, (x + 100, y), (x + 100, y + dy), gray, 1)

            # draw matchup names
            slot = j // 2
            if i not in bracket:
                continue
            if slot not in bracket[i]:
                continue
            m: Match = bracket[i][slot]
            name_user0 = strip_text(f'{users[m.user0].displayName:.16s}')
            im = cv2.putText(im, name_user0, (x + 2, y - 2), FONT, 0.3, (0, 0, 0))
            name_user1 = strip_text(f'{users[m.user1].displayName:.16s}')
            im = cv2.putText(im, name_user1, (x + 2, y + dy - 2), FONT, 0.3, (0, 0, 0))

            # place winners
            if (m.round == round_ or i == 4) and m.winner is not None:
                name_user = strip_text(f'{users[m.winner].displayName:.16s}')
                im = cv2.putText(im, name_user, (x + 102, int(y + 0.5 * dy - 2)), FONT, 0.3, (0, 0, 0))

            # get update message
            if m.round == round_ and (msg is None or m.updated > msg_dt):
                if m.winner is not None:
                    name_winner = strip_text(f'{users[m.winner].displayName:.16s}')
                    name_loser = strip_text(f'{users[m.loser].displayName:.16s}')
                    msg = f'{name_winner} has just defeated {name_loser}.'
                else:
                    msg = f'playing now! {name_user0} vs. {name_user1}'
                msg_dt = m.updated

        # offset y
        y0 += int(0.5 * dy)

    # write latest update message
    if msg is not None:
        tz = datetime.timezone(datetime.timedelta(hours=-5))
        msg = f'[{msg_dt.astimezone(tz):%H:%M}] ' + msg
        im = write_message(im, line0=msg)

    # cv2.imshow('debug', im)
    # cv2.waitKey(0)
    # return

    # encode
    _, b = cv2.imencode('.png', im)
    return b.tobytes()


def strip_text(msg: str) -> str:
    return ''.join(m for m in msg if ord(m) < 128).strip()


def get_pfp(url: str) -> np.ndarray:
    # if 'imgur' in url:
    #     if 'jpg' in 'url':
    #         url = url.replace('.jpg', 'b.jpg')
    #     elif 'png' in 'url':
    #         url = url.replace('.png', 'b.png')
    # elif 'ipfs.decentralized-content' in url:
    #     url = f'https://res.cloudinary.com/merkle-manufactory/image/fetch/c_fill,f_png,w_168/{url}'
    url = f'https://res.cloudinary.com/merkle-manufactory/image/fetch/c_fill,f_jpg,h_{PFP_SZ},w_{PFP_SZ}/{url}'

    res = requests.get(url, stream=True).raw
    im = np.asarray(bytearray(res.read()), dtype='uint8')
    im = cv2.imdecode(im, cv2.IMREAD_COLOR)
    im = cv2.resize(im, (PFP_SZ, PFP_SZ))
    return im


def write_message(im: np.ndarray, line0: str = None, line1: str = None) -> np.ndarray:
    if line0 is not None:
        im = cv2.putText(im, line0, (22, 250), FONT, 0.5, (255, 255, 255))
    if line1 is not None:
        im = cv2.putText(im, line1, (22, 270), FONT, 0.5, (255, 255, 255))
    return im
