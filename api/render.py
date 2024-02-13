"""
dynamic image rendering for frames
"""

import os
import numpy as np
import cv2

from .models import Tournament, Match, MatchStatus

FONT = cv2.FONT_HERSHEY_SIMPLEX


def render_home(tournament: int, total: int, round_: int, prize, remaining: int) -> bytes:
    # setup background
    im = cv2.imread('api/static/tournament.png')

    # stats
    x = 12
    im = cv2.putText(im, 'Farcaster rock paper scissors', (x, 30), FONT, 0.8, (0, 0, 0), 2)
    im = cv2.putText(im, f'tournament {tournament}', (x, 70), FONT, 0.7, (0, 0, 0), 1)
    im = cv2.putText(im, f'prize {prize}', (x, 100), FONT, 0.7, (0, 0, 0), 1)
    im = cv2.putText(im, f'round {round_}', (x, 130), FONT, 0.7, (0, 0, 0), 1)
    im = cv2.putText(im, f'{total} users entered', (x, 160), FONT, 0.7, (0, 0, 0), 1)
    im = cv2.putText(im, f'{remaining} competitors remain', (x, 190), FONT, 0.7, (0, 0, 0), 1)

    # message
    im = cv2.putText(im, 'Welcome! Proceed below to play.', (22, 250), FONT, 0.5, (255, 255, 255))
    im = cv2.putText(im, 'Good luck!', (22, 270), FONT, 0.5, (255, 255, 255))

    # encode
    _, b = cv2.imencode('.png', im)
    return b.tobytes()


def render_match(match: Match, round_: int, turn: int, user: bool, status: MatchStatus) -> bytes:
    # setup background
    im = cv2.imread('api/static/match.png')

    # player data
    # TODO

    # message
    # TODO

    # encode
    _, b = cv2.imencode('.png', im)
    return b.tobytes()
