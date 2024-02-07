"""
methods to call neynar api
"""
import os

import requests

from .models import FrameMessage, ValidatedMessage


def get_frame_action(msg: str) -> (bool, ValidatedMessage):
    key = os.getenv('NEYNAR_KEY')
    url = 'https://api.neynar.com/v2/farcaster/frame/validate'
    body = {
        'cast_reaction_context': False,
        'follow_context': False,
        'message_bytes_in_hex': msg
    }
    headers = {
        'accept': 'application/json',
        'api_key': key,
        'content-type': 'application/json'
    }
    res = requests.post(url, json=body, headers=headers)

    body = res.json()
    if not body['valid']:
        return False, None

    print(body)
    action = ValidatedMessage(**body['action'])
    print(action)

    return True, action


def validate_message(msg: FrameMessage) -> (bool, ValidatedMessage):
    valid, action = get_frame_action(msg.trustedData.messageBytes)
    print(valid)
    print(msg)
    print(action)
    # TODO compare
    return valid, action


def validate_message_or_mock(msg: FrameMessage) -> (bool, ValidatedMessage):
    if os.getenv('VERCEL_ENV') is None:
        return True, ValidatedMessage()

    return validate_message(msg)
