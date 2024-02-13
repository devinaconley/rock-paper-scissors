"""
main entry point for rock paper scissors app
"""
# lib
import json
import time
from flask import Flask, render_template, url_for, request, redirect, send_file, make_response

# src
from .warpcast import get_user
from .neynar import validate_message_or_mock
from .storage import get_supabase, get_current_tournament, get_tournament, get_match
from .models import FrameMessage, Gesture, MatchState, MatchStatus
from .rps import (
    get_round_settled,
    current_round,
    get_match_user,
    get_match_user_eliminated,
    get_match_state,
    submit_move,
    remaining_users
)
from .render import render_home, render_match

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    # static home page
    s = get_supabase()
    t = get_current_tournament(s)

    return render_template(
        'frame.html',
        title='farcaster rock paper scissors',
        image=url_for('home_image', _external=True, tournament=t.id),
        content='welcome to rock paper scissors!',
        post_url=url_for('match', _external=True),
        button1='play \U00002694\U0000fe0f'
    ), 200


@app.route('/match', methods=['POST'])
def match():
    # note: consider this an unauthenticated endpoint
    # TODO
    # get current tournament/round
    # get user match
    # get match state

    # render current match status
    # show emoji buttons if they can play, else back
    # note probably won't show what they played if waiting, would require auth

    # parse action message
    msg = FrameMessage(**json.loads(request.data))
    print(msg)

    # tournament state
    now = time.time()
    s = get_supabase()
    t = get_current_tournament(s)
    r = current_round(int(t.start.timestamp()), int(now))

    if msg.untrustedData.fid > t.size:
        print(f'fid {msg.untrustedData.fid} not competing')
        return ''  # TODO not competing

    m = get_match_user(s, int(now), t.id, t.size, r, msg.untrustedData.fid)
    print(m)
    if m is None:
        m = get_match_user_eliminated(s, t.id, msg.untrustedData.fid)
        print(f'eliminated {m}')
        # TODO eliminated
        return render_template(
            'frame.html',
            title='you were eliminated',
            image='https://img.freepik.com/free-photo/hourglass-with-sand-middle-word-sand-it_123827-23414.jpg',
            post_url=url_for('home', _external=True),
            button1='\U0001F519'  # back
        ), 200

    state = get_match_state(s, m)
    print(state)

    if ((state.status == MatchStatus.USER_0_PLAYED and msg.untrustedData.fid == m.user0)
            or (state.status == MatchStatus.USER_1_PLAYED and msg.untrustedData.fid == m.user1)):
        print('you played a move waiting on opponent')
        # TODO waiting
        return render_template(
            'frame.html',
            title='waiting on opponent',
            image='https://img.freepik.com/free-photo/hourglass-with-sand-middle-word-sand-it_123827-23414.jpg',
            post_url=url_for('home', _external=True),
            button1='\U0001F519'  # back
        ), 200

    elif state.status == MatchStatus.SETTLED:
        # TODO results
        print(f'settled: {state}')
        return render_template(
            'frame.html',
            title='match settled',
            image='https://img.freepik.com/free-photo/hourglass-with-sand-middle-word-sand-it_123827-23414.jpg',
            post_url=url_for('home', _external=True),
            button1='\U0001F519'  # back
        ), 200

    # else user needs to play (NEW, OPPONENT_PLAYED, DRAW)

    user = get_user(msg.untrustedData.fid)
    print(user)

    return render_template(
        'frame.html',
        title='match info',
        image='https://img.freepik.com/premium-photo/versus-screen-fight-backgrounds-competition-3d-rendering_578102-1434.jpg',
        content='rock paper scissors current matchup',
        post_url=url_for('move', _external=True),
        button1='\U0001F5FF',  # rock
        button2='\U0001f4c3',  # paper
        button3='\U00002702\U0000fe0f',  # scissors
    ), 200


@app.route('/move', methods=['POST'])
def move():
    msg = FrameMessage(**json.loads(request.data))
    print(msg)

    # verify game state (turn unplayed)
    now = time.time()
    s = get_supabase()
    t = get_current_tournament(s)
    r = current_round(int(t.start.timestamp()), int(now))

    if msg.untrustedData.fid > t.size:
        raise ValueError(f'fid {msg.untrustedData.fid} not competing')

    m = get_match_user(s, int(now), t.id, t.size, r, msg.untrustedData.fid)
    if m is None:
        raise ValueError(f'fid {msg.untrustedData.fid} has been eliminated')

    state = get_match_state(s, m)
    print(state)
    if state.status == MatchStatus.SETTLED:
        raise ValueError(f'match {m.id} already settled, winner {m.winner}')

    if ((state.status == MatchStatus.USER_0_PLAYED and msg.untrustedData.fid == m.user0)
            or (state.status == MatchStatus.USER_1_PLAYED and msg.untrustedData.fid == m.user1)):
        raise ValueError(f'{msg.untrustedData.fid} already played a move for match {m.id} turn {state.turn}')

    # authenticate action here
    val, action = validate_message_or_mock(msg)
    if not val:
        raise ValueError(f'invalid message! {msg.model_dump_json()}')

    print(f'played: {action.tapped_button.index}')
    g = Gesture(action.tapped_button.index)
    print(g)

    # submit action
    submit_move(s, int(now), m.id, action.interactor.fid, state.turn, g, msg.trustedData.messageBytes)

    return render_template(
        'frame.html',
        title='you played a move!',
        image=url_for('match_image', _external=True, tournament=t.id, round_=r, slot=0, turn=0, user=0, status=0),
        content='you played a move!',
        post_url=url_for('home', _external=True),
        button1='back'
    ), 200


@app.route('/render/tournament/<int:tournament>/im.png')
@app.route('/render/tournament/<int:tournament>/<int:timestamp>/im.png')
def home_image(tournament: int, timestamp: int = None):
    print(f'requesting image render for tournament {tournament} {timestamp}')
    s = get_supabase()
    t = get_tournament(s, tournament)
    if t is None:
        raise ValueError(f'invalid tournament {tournament}')

    # get tournament state
    now = time.time()
    r = current_round(int(t.start.timestamp()), int(now))
    print(f'round {r}')
    r_settled = get_round_settled(s, t.id, r)
    remaining = remaining_users(t.size, r, r_settled)
    print(f'settled {r_settled}')
    print(f'remaining {remaining}')
    # TODO get bounty?

    # render image
    res = make_response(render_home(t.id, t.size, r, 'TBD', remaining))
    res.headers.set('Content-Type', 'image/png')
    return res


@app.route('/render/match/<int:tournament>/<int:round_>}/<int:slot>/<int:turn>/<int:user>/<int:status>/im.png')
def match_image(tournament: int, round_: int, slot: int, turn: int, user: int, status: int):
    # get match state
    status = MatchStatus(status)
    u = bool(user)
    s = get_supabase()
    m = get_match(s, tournament, round_, slot)
    if m is None:
        raise ValueError(f'invalid match {tournament} {round_} {slot}')

    # render image
    res = make_response(render_match(m, round_, turn, u, status))
    res.headers.set('Content-Type', 'image/png')
    return res
