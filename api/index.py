"""
main entry point for rock paper scissors app
"""
# lib
import json
from flask import Flask, render_template, url_for, request

# src
from .warpcast import get_user
from .neynar import validate_message
from .storage import get_supabase, get_current_tournament
from .models import FrameMessage

app = Flask(__name__)


@app.route('/')
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
        button1='Play'
    ), 200


@app.route('/match', methods=['POST'])
def match():
    fid = 8268
    total = 2 ** 19
    seed = None  # might actually be funnier to matchup ogs against newbies (i.e. rank by fid)

    # get current round
    # compute match slot and parent slots
    # get users by previous match results (recurse and backfill as needed)
    # winner: check for explicit result, then check for draw, then check for uncontested play, then prefer lower fid

    # render current match status
    # show emoji buttons if they can play, else back
    # TODO
    print(request.data)

    msg = FrameMessage(**json.loads(request.data))
    print(msg)

    user = get_user(msg.untrustedData.fid)
    print(user)

    return render_template(
        'frame.html',
        title='match info',
        image='https://img.freepik.com/free-psd/isolated-golden-luxury-photo-frame_1409-3600.jpg',
        content='rock paper scissors current matchup',
        post_url=url_for('match', _external=True),
        button1='back',
        button1_action='link',
        button1_target=url_for('home', _external=True),
        button2='U+2618',
        button3='U+1F4C4',
        button4='U+2702'
    ), 200
