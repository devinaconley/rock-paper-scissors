"""
methods to call neynar api
"""
import os

import requests

from .models import FrameMessage, ValidatedMessage, Interactor, Profile, Bio, Button, Input


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
        # mock
        return True, ValidatedMessage(
            object='validated_frame_action',
            interactor=Interactor(
                object='user',
                fid=msg.untrustedData.fid,
                username='',
                display_name='',
                pfp_url='',
                profile=Profile(
                    bio=Bio(
                        text=''
                    )
                ),
                follower_count=0,
                following_count=0,
                verifications=['0x'],
                active_status='',
            ),
            tapped_button=Button(
                index=msg.untrustedData.buttonIndex
            ),
            input=Input(
                text=msg.untrustedData.inputText or ''
            ),
            url=msg.untrustedData.url,
            cast={}
        )  # TODO populate

    return validate_message(msg)
