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
from .models import FrameMessage, Gesture, MatchState, MatchStatus, MessageCode, Result, Tournament
from .rps import (
    get_round_settled,
    current_round,
    current_round_end,
    round_size,
    total_rounds,
    get_match_user,
    get_match_user_last,
    get_match_state,
    get_match_slot,
    submit_move,
    remaining_users,
    update_match_result,
    ROUND_BUFFER,
    get_final_bracket
)
from .render import render_home, render_match, render_message, render_bracket

app = Flask(__name__)


class BadRequest(Exception):
    pass


@app.errorhandler(BadRequest)
def handle_invalid_usage(e):
    response = jsonify({'status_code': 403, 'message': str(e)})
    response.status_code = 403
    return response


# ---- core frame views ----

@app.route('/', methods=['GET', 'POST'])
def home():
    # tournament status home page
    s = get_supabase()
    t = get_current_tournament(s)

    response = make_response(render_template(
        'frame.html',
        title='farcaster rock paper scissors',
        image=url_for('home_image', _external=True, tournament=t.id),
        content='welcome to rock paper scissors!',
        post_url=url_for('match', _external=True),
        button1='play \U00002694\U0000fe0f',
        button2='bracket \U0001F3C6',
        button2_target=url_for('bracket', _external=True)
    ))
    response.cache_control.max_age = 900  # expire cached image after 15 minutes
    response.status_code = 200
    return response


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
    end = current_round_end(int(t.start.timestamp()), r)

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
    print(state)
    if m is None:
        m = get_match_user_last(s, t.id, msg.untrustedData.fid)
        print(f'last match {m.id}')
        return render_template(
            'frame.html',
            title='your last match',
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

    elif m.result in {Result.BYE, Result.PLAYED} or state.status == MatchStatus.SETTLED:
        print(f'settled: {m.result}')
        return render_template(
            'frame.html',
            title='match settled',
            image=url_for('match_image', _external=True, tournament=t.id, round_=r, slot=m.slot, turn=state.turn,
                          user=msg.untrustedData.fid, status=state.status.value),
            post_url=url_for('home', _external=True),
            button1='\U0001F519'  # back
        ), 200

    elif state.status == MatchStatus.DRAW and (end - now) < ROUND_BUFFER:
        print(f'draw in buffer window: {state}')
        return render_template(
            'frame.html',
            title='match draw',
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
    end = current_round_end(int(t.start.timestamp()), r)

    if msg.untrustedData.fid > t.size:
        raise BadRequest(f'fid {msg.untrustedData.fid} not competing')

    sz = round_size(t.size, r)
    if sz < 2:
        raise BadRequest('tournament over')

    m, state = get_match_user(s, int(now), t.id, t.size, r, msg.untrustedData.fid)
    if m is None:
        raise BadRequest(f'fid {msg.untrustedData.fid} has been eliminated')
    print(state)

    if state.status == MatchStatus.SETTLED:
        raise BadRequest(f'match {m.id} already settled, winner {m.winner}')

    if ((state.status == MatchStatus.USER_0_PLAYED and msg.untrustedData.fid == m.user0)
            or (state.status == MatchStatus.USER_1_PLAYED and msg.untrustedData.fid == m.user1)):
        raise BadRequest(f'{msg.untrustedData.fid} already played a move for match {m.id} turn {state.turn}')

    elif state.status == MatchStatus.DRAW and (end - now) < ROUND_BUFFER:
        raise BadRequest(f'cannot start a new turn {state.turn} for match {m.id} inside of round buffer window {now}')

    # authenticate action here
    val, action = validate_message_or_mock(msg)
    if not val:
        raise BadRequest(f'invalid message! {msg.model_dump_json()}')

    g = Gesture(action.tapped_button.index)
    print(f'played: {g}')

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


# ---- auxiliary frame views ----

def _validate_slot(now: int, tournament: Tournament, round_: int, slot: int):
    r = current_round(int(tournament.start.timestamp()), now)
    if round_ < 0:
        raise BadRequest(f'invalid round {round_}')
    if round_ > r:
        raise BadRequest(f'future round {round_}')

    sz = round_size(tournament.size, round_)
    if slot >= sz / 2:
        raise BadRequest(f'invalid slot {slot} for tournament {tournament} round {round_}')


@app.route('/spectate/<int:tournament>/<int:round_>/<int:slot>', methods=['GET', 'POST'])
def spectate(tournament: int, round_: int, slot: int):
    # validate match slot
    now = time.time()
    s = get_supabase()
    t = get_tournament(s, tournament)
    if t is None:
        raise BadRequest(f'invalid tournament {tournament}')

    _validate_slot(int(now), t, round_, slot)

    # get match and state
    m, state = get_match_slot(s, int(now), t.id, t.size, round_, round_, slot)
    if state is None:
        state = get_match_state(s, m)

    return render_template(
        'frame.html',
        title='spectating',
        image=url_for('match_image', _external=True, tournament=t.id, round_=round_, slot=m.slot, turn=state.turn,
                      user=min(m.user0, m.user1), status=state.status.value),
        content=f'spectating {m.id}',
        post_url=url_for('spectate', _external=True, tournament=t.id, round_=round_, slot=slot),
        button1='\U0001F504'  # refresh
    ), 200


@app.route('/bracket', methods=['GET', 'POST'])
def bracket():
    s = get_supabase()
    t = get_current_tournament(s)

    response = make_response(render_template(
        'frame.html',
        title='bracket',
        image=url_for('bracket_image', _external=True, tournament=t.id),
        content=f'bracket {t.id}',
        post_url=url_for('home', _external=True),
        button1='\U0001F519'  # back
    ))

    response.cache_control.max_age = 300
    response.status_code = 200
    return response


# ---- json info endpoints ----
@app.route('/match/<int:fid>', methods=['GET'])
def info_get_match_fid(fid: int):
    # tournament state
    now = time.time()
    s = get_supabase()
    t = get_current_tournament(s)
    r = current_round(int(t.start.timestamp()), int(now))

    if r < 0:
        return jsonify({'msg': 'tournament not started'})

    if fid > t.size:
        return jsonify({'msg': f'fid {fid} not competing'})

    # get current or latest match
    m, state = get_match_user(s, int(now), t.id, t.size, r, fid)
    if m is None:
        m = get_match_user_last(s, t.id, fid)
        return jsonify({'msg': f'last {m.id}', 'match': m.model_dump(mode='json')})

    return jsonify({
        'msg': f'current match {fid} {m.id}',
        'match': m.model_dump(mode='json'),
        'state': state.model_dump(mode='json')
    })


@app.route('/match/<int:tournament>/<int:round_>/<int:slot>', methods=['GET'])
def info_get_match_slot(tournament: int, round_: int, slot: int):
    # validate match slot
    now = time.time()
    s = get_supabase()
    t = get_tournament(s, tournament)
    if t is None:
        raise BadRequest(f'invalid tournament {tournament}')

    _validate_slot(int(now), t, round_, slot)

    # get match and state
    m, state = get_match_slot(s, int(now), t.id, t.size, round_, round_, slot)
    if state is None:
        state = get_match_state(s, m)

    return jsonify({
        'msg': f'match slot {tournament} {round_} {slot}',
        'match': m.model_dump(mode='json'),
        'state': state.model_dump(mode='json')
    })


# ---- image rendering endpoints ----

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
    sz = round_size(t.size, r)
    if r < 0:
        # not started yet
        r_settled = 0
        remaining = t.size
    elif sz < 2:
        # tournament over
        r = total_rounds(t.size) - 1
        r_settled = 0
        remaining = 1
    else:
        r_settled = get_round_settled(s, t.id, r)
        remaining = remaining_users(t.size, r, r_settled)
    prize = '500k $DEGEN'  # TODO get bounty live
    print(f'tournament {tournament}, size {t.size}, round {r}, settled {r_settled}, remaining {remaining}')

    # render image
    res = make_response(render_home(t.id, t.size, r, prize, remaining))
    res.headers.set('Content-Type', 'image/png')
    res.cache_control.max_age = 900
    return res


@app.route('/render/match/<int:tournament>/<int:round_>/<int:slot>/<int:turn>/<int:user>/<int:status>/im.png')
def match_image(tournament: int, round_: int, slot: int, turn: int, user: int, status: int):
    # get match
    now = time.time()
    s = get_supabase()
    t = get_tournament(s, tournament)
    if t is None:
        raise BadRequest(f'invalid tournament {tournament}')
    m = get_match(s, tournament, round_, slot)
    if m is None:
        raise BadRequest(f'invalid match {tournament} {round_} {slot}')
    if user == 0:
        raise BadRequest('invalid user 0')
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
    end = current_round_end(int(t.start.timestamp()), round_)

    # get user info
    u0 = get_user(m.user0)
    u1 = get_user(m.user1) if m.user1 > 0 else None

    # render image
    res = make_response(render_match(m, u0 if u else u1, u1 if u else u0, round_, state, end - int(now)))
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


@app.route('/render/bracket/<int:tournament>/im.png')
def bracket_image(tournament: int):
    # get tournament
    s = get_supabase()
    t = get_tournament(s, tournament)
    if t is None:
        raise BadRequest(f'invalid tournament {tournament}')
    now = time.time()
    r = current_round(int(t.start.timestamp()), int(now))

    # get bracket
    bracket_matches = get_final_bracket(s, t.id, t.size)

    # get user profiles
    users = {}
    for _, bracket_round in bracket_matches.items():
        for _, m in bracket_round.items():
            if m.user0 not in users:
                users[m.user0] = get_user(m.user0)
            if m.user1 not in users:
                users[m.user1] = get_user(m.user1)

    # render image
    res = make_response(render_bracket(bracket_matches, users, r))
    res.headers.set('Content-Type', 'image/png')
    res.cache_control.max_age = 300

    return res
