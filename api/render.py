"""
dynamic image rendering for frames
"""

import os
import requests
import numpy as np
import cv2

from .models import Tournament, Match, MatchStatus, User

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
        turn: int,
        status: MatchStatus
) -> bytes:
    # setup background
    im = cv2.imread('api/static/match.png')

    # player data
    im = cv2.putText(im, f'{user.displayName:.16s}', (328, 158), FONT, 0.4, (0, 0, 0))
    im = cv2.putText(im, f'Fid.{user.fid}', (460, 158), FONT, 0.3, (0, 0, 0))
    pfp_user = get_pfp(user.pfp.url)
    x = 100
    y = 120
    im[y:y + PFP_SZ, x:x + PFP_SZ] = pfp_user

    # opponent data
    im = cv2.putText(im, f'{opponent.displayName:.16s}', (45, 25), FONT, 0.4, (0, 0, 0))
    im = cv2.putText(im, f'Fid.{opponent.fid}', (175, 25), FONT, 0.3, (0, 0, 0))
    pfp_opp = get_pfp(opponent.pfp.url)
    x = 360
    y = 20
    im[y:y + PFP_SZ, x:x + PFP_SZ] = pfp_opp

    # message
    im = write_message(
        im, line0=f'Round {round_} matchup, {user.displayName:.16s} vs. {opponent.displayName:.16s}. Turn {turn}.')

    # TODO more message details (gestures, result, etc.)
    if match.winner is not None:
        if match.winner == user.fid:
            msg = f'You defeated {opponent.displayName:.16s}!'
        else:
            msg = f'You were knocked out by {opponent.displayName:.16s}.'
    elif status == MatchStatus.DRAW:
        msg = 'Draw! Play your next move.'
    elif (user.fid == match.user0 and status == MatchStatus.USER_0_PLAYED) or (
            user.fid == match.user1 and status == MatchStatus.USER_1_PLAYED):
        msg = 'Waiting on your opponent.'
    elif (user.fid == match.user0 and status == MatchStatus.USER_1_PLAYED) or (
            user.fid == match.user1 and status == MatchStatus.USER_0_PLAYED):
        msg = 'Your opponent has played. Make a move!'
    else:
        # NEW
        msg = 'Play your move!'
    im = write_message(im, line1=msg)

    # cv2.imshow('debug', im)
    # cv2.waitKey(0)
    # return

    # encode
    _, b = cv2.imencode('.png', im)
    return b.tobytes()


def get_pfp(url: str) -> np.ndarray:
    if 'imgur' in url:
        url = url.replace('.jpg', 'b.jpg')
    elif 'ipfs.decentralized-content' in url:
        url = f'https://res.cloudinary.com/merkle-manufactory/image/fetch/c_fill,f_png,w_168/{url}'
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
