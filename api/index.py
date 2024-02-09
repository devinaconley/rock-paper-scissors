"""
main entry point for rock paper scissors app
"""
# lib
import json
from flask import Flask, render_template, url_for, request, redirect

# src
from .warpcast import get_user
from .neynar import validate_message_or_mock
from .storage import get_supabase, get_current_tournament
from .models import FrameMessage, Gesture

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    # get current tournament round
    # get remaining players
    # get bounty
    # render image
    # TODO

    supabase = get_supabase()
    curr = get_current_tournament(supabase)
    print(curr)

    return render_template(
        'frame.html',
        title='rock paper scissors',
        image='https://img.freepik.com/free-psd/isolated-golden-luxury-photo-frame_1409-3600.jpg',
        content='welcome to rock paper scissors!',
        post_url=url_for('match', _external=True),
        button1='play \U00002694\U0000fe0f'
    ), 200


@app.route('/match', methods=['POST'])
def match():
    # TODO
    # get current tournament/round
    # get user match
    # get match state

    # render current match status
    # show emoji buttons if they can play, else back
    # note probably won't show what they played if waiting, would require auth

    print(request.data)
    print(request.headers)
    print(request.method)

    msg = FrameMessage(**json.loads(request.data))
    print(msg)

    user = get_user(msg.untrustedData.fid)
    print(user)

    return render_template(
        'frame.html',
        title='match info',
        image='https://img.freepik.com/premium-photo/versus-screen-fight-backgrounds-competition-3d-rendering_578102-1434.jpg',
        content='rock paper scissors current matchup',
        post_url=url_for('move', _external=True),
        button1='\U0001faa8',  # rock
        button2='\U0001f4c3',  # paper
        button3='\U00002702\U0000fe0f',  # scissors
    ), 200


@app.route('/move', methods=['POST'])
def move():
    msg = FrameMessage(**json.loads(request.data))
    print(msg)

    # TODO verify game state (turn unplayed)

    val, action = validate_message_or_mock(msg)
    if val:
        print(f'played: {action.tapped_button.index}')
        g = Gesture(action.tapped_button.index)
        print(g)

    # TODO submit action, etc.

    return render_template(
        'frame.html',
        title='you played a move! waiting on opponent...',
        image='https://img.freepik.com/free-photo/hourglass-with-sand-middle-word-sand-it_123827-23414.jpg',
        content='you played a move! waiting on opponent',
        post_url=url_for('home', _external=True),
        button1='back'
    ), 200
