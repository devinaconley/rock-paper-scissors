"""
methods to query farcaster data from the warpcast api
"""

import requests


def get_user(fid: int) -> dict:
    res = requests.get('https://client.warpcast.com/v2/user', params={'fid': fid})
    print(res.text)
    return res.json()
