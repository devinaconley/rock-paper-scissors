"""
main entry point for rock paper scissors app
"""
# lib
import json
import time
from flask import Flask, render_template, url_for, request, make_response, jsonify

# src
from .warpcast import get_user
from .neynar import validate_message_or_mock
from .storage import get_supabase, get_current_tournament, get_tournament, get_match
from .models import FrameMessage, Gesture, MatchState, MatchStatus, MessageCode
from .rps import (
    get_round_settled,
    current_round,
    get_match_user,
    get_match_user_eliminated,
    get_match_state,
    submit_move,
    remaining_users,
    update_match_result
)
from .render import render_home, render_match, render_message

app = Flask(__name__)


class BadRequest(Exception):
    pass


@app.errorhandler(BadRequest)
def handle_invalid_usage(e):
    response = jsonify({'status_code': 403, 'message': str(e)})
    response.status_code = 403
    return response


@app.route('/', methods=['GET', 'POST'])
def home():
    # tournament status home page
    s = get_supabase()
    t = get_current_tournament(s)

    # include hour in path to skip cached image and serve fresh
    # TODO: remove this concept once we get official first page cache expiry
    hour = None
    if request.method == 'POST':
        now = time.time()
        hour = now - now % 3600

    return render_template(
        'frame.html',
        title='farcaster rock paper scissors',
        image=url_for('home_image', _external=True, tournament=t.id, timestamp=hour),
        content='welcome to rock paper scissors!',
        post_url=url_for('match', _external=True),
        button1='play \U00002694\U0000fe0f'
    ), 200


@app.route('/match', methods=['POST'])
def match():
    # note: consider this an unauthenticated endpoint

    # get current tournament/round
    # get user match
    # get match state
    # render current match status
    # show emoji buttons if they can play, else back

    # parse action message
    msg = FrameMessage(**json.loads(request.data))
    print(msg)

    # tournament state
    now = time.time()
    s = get_supabase()
    t = get_current_tournament(s)
    r = current_round(int(t.start.timestamp()), int(now))

    if r < 0:
        return render_template(
            'frame.html',
            title='tournament not started',
            image=url_for('message_image', _external=True, code=MessageCode.NOT_STARTED.value),
            post_url=url_for('home', _external=True),
            button1='\U0001F519'  # back
        ), 200

    if msg.untrustedData.fid > t.size:
        print(f'fid {msg.untrustedData.fid} not competing')
        return render_template(
            'frame.html',
            title='not entered',
            image=url_for('message_image', _external=True, code=MessageCode.NOT_ENTERED.value),
            post_url=url_for('home', _external=True),
            button1='\U0001F519'  # back
        ), 200

    m, state = get_match_user(s, int(now), t.id, t.size, r, msg.untrustedData.fid)
    print(m)
    if m is None:
        m = get_match_user_eliminated(s, t.id, msg.untrustedData.fid)
        print(f'eliminated {m}')
        return render_template(
            'frame.html',
            title='you were eliminated',
            image=url_for('match_image', _external=True, tournament=t.id, round_=m.round, slot=m.slot, turn=0,
                          user=msg.untrustedData.fid, status=MatchStatus.SETTLED.value),
            post_url=url_for('home', _external=True),
            button1='\U0001F519'  # back
        ), 200

    if ((state.status == MatchStatus.USER_0_PLAYED and msg.untrustedData.fid == m.user0)
            or (state.status == MatchStatus.USER_1_PLAYED and msg.untrustedData.fid == m.user1)):
        print('you played a move waiting on opponent')
        return render_template(
            'frame.html',
            title='waiting on opponent',
            image=url_for('match_image', _external=True, tournament=t.id, round_=r, slot=m.slot, turn=state.turn,
                          user=msg.untrustedData.fid, status=state.status.value),
            post_url=url_for('home', _external=True),
            button1='\U0001F519'  # back
        ), 200

    elif state.status == MatchStatus.SETTLED:
        print(f'settled: {state}')
        return render_template(
            'frame.html',
            title='match settled',
            image=url_for('match_image', _external=True, tournament=t.id, round_=r, slot=m.slot, turn=state.turn,
                          user=msg.untrustedData.fid, status=state.status.value),
            post_url=url_for('home', _external=True),
            button1='\U0001F519'  # back
        ), 200

    # else user needs to play (NEW, OPPONENT_PLAYED, DRAW)
    return render_template(
        'frame.html',
        title='match info',
        image=url_for('match_image', _external=True, tournament=t.id, round_=r, slot=m.slot, turn=state.turn,
                      user=msg.untrustedData.fid, status=state.status.value),
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
        raise BadRequest(f'fid {msg.untrustedData.fid} not competing')

    m, state = get_match_user(s, int(now), t.id, t.size, r, msg.untrustedData.fid)
    if m is None:
        raise BadRequest(f'fid {msg.untrustedData.fid} has been eliminated')
    print(state)

    if state.status == MatchStatus.SETTLED:
        raise BadRequest(f'match {m.id} already settled, winner {m.winner}')

    if ((state.status == MatchStatus.USER_0_PLAYED and msg.untrustedData.fid == m.user0)
            or (state.status == MatchStatus.USER_1_PLAYED and msg.untrustedData.fid == m.user1)):
        raise BadRequest(f'{msg.untrustedData.fid} already played a move for match {m.id} turn {state.turn}')

    # authenticate action here
    val, action = validate_message_or_mock(msg)
    if not val:
        raise BadRequest(f'invalid message! {msg.model_dump_json()}')

    print(f'played: {action.tapped_button.index}')
    g = Gesture(action.tapped_button.index)
    print(g)

    # submit action
    submit_move(s, int(now), m.id, action.interactor.fid, state.turn, g, msg.trustedData.messageBytes)

    return render_template(
        'frame.html',
        title='you played a move!',
        image=url_for('match_image', _external=True, tournament=t.id, round_=r, slot=m.slot, turn=state.turn + 1,
                      user=action.interactor.fid, status=MatchStatus.NEW.value),
        content='you played a move!',
        post_url=url_for('home', _external=True),
        button1='\U0001F519'  # back
    ), 200


@app.route('/render/tournament/<int:tournament>/im.png')
@app.route('/render/tournament/<int:tournament>/<int:timestamp>/im.png')
def home_image(tournament: int, timestamp: int = None):
    print(f'requesting image render for tournament {tournament} {timestamp}')
    s = get_supabase()
    t = get_tournament(s, tournament)
    if t is None:
        raise BadRequest(f'invalid tournament {tournament}')

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


@app.route('/render/match/<int:tournament>/<int:round_>/<int:slot>/<int:turn>/<int:user>/<int:status>/im.png')
def match_image(tournament: int, round_: int, slot: int, turn: int, user: int, status: int):
    # get match
    now = time.time()
    s = get_supabase()
    m = get_match(s, tournament, round_, slot)
    if m is None:
        raise BadRequest(f'invalid match {tournament} {round_} {slot}')
    if user == m.user0:
        u = True
    elif user == m.user1:
        u = False
    else:
        raise BadRequest(f'invalid user {m.id} {user}')

    # get match state (with lazy scoring)
    status = MatchStatus(status)
    m, state = update_match_result(s, int(now), round_, m)
    if state is None:
        state = get_match_state(s, m)
    # TODO need any param validation here?

    # get user info
    u0 = get_user(m.user0)
    u1 = get_user(m.user1)

    # render image
    res = make_response(render_match(m, u0 if u else u1, u1 if u else u0, round_, state.turn, state.status))
    res.headers.set('Content-Type', 'image/png')
    return res


@app.route('/render/message/<int:code>/im.png')
def message_image(code: int):
    # render image
    msg = MessageCode(code)
    if msg == MessageCode.NOT_STARTED:
        b = render_message(line0='The tournament has not started yet.', line1='Check back soon!')
    elif msg == MessageCode.NOT_ENTERED:
        b = render_message(line0='You were not entered in this tournament.', line1='Check back soon!')
    else:
        raise BadRequest(f'invalid msg {msg}')

    # response
    res = make_response(b)
    res.headers.set('Content-Type', 'image/png')
    return res
