"""
data models
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


# ---- storage ----

class Tournament(BaseModel):
    id: int
    created: datetime
    start: datetime
    size: int
    seed: Optional[int] = None


class Result(Enum):
    PENDING = 0
    PLAYED = 1
    DRAW = 2
    FORFEIT = 3
    PASS = 4
    BYE = 5


class Match(BaseModel):
    id: str
    created: datetime
    updated: datetime
    tournament: int
    round: int
    slot: int
    user0: int
    user1: int
    winner: Optional[int] = None
    loser: Optional[int] = None
    result: Result


class Gesture(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3


class Move(BaseModel):
    id: str
    created: datetime
    match: str
    user: int
    turn: int
    move: Gesture
    signature: str


# ---- frame message ----

class CastId(BaseModel):
    fid: int
    hash: str


class UntrustedData(BaseModel):
    fid: int
    url: str
    messageHash: str
    timestamp: int
    network: int
    buttonIndex: int
    inputText: Optional[str] = None
    castId: CastId


class TrustedData(BaseModel):
    messageBytes: str


class FrameMessage(BaseModel):
    untrustedData: UntrustedData
    trustedData: TrustedData


# ---- neynar ----

class Viewer(BaseModel):
    following: bool
    followed_by: bool


class Bio(BaseModel):
    text: str
    mentioned_profiles: Optional[list[str]] = []


class Profile(BaseModel):
    bio: Bio


class Interactor(BaseModel):
    object: str
    fid: int
    username: str
    display_name: str
    custody_address: Optional[str] = None
    pfp_url: str
    profile: Profile
    follower_count: int
    following_count: int
    verifications: list[str]
    active_status: str
    viewer_context: Optional[Viewer] = None


class Button(BaseModel):
    title: Optional[str] = None
    index: int
    action_type: Optional[str] = None


class Input(BaseModel):
    text: str


class ValidatedMessage(BaseModel):
    object: str
    interactor: Interactor
    tapped_button: Button
    input: Input
    url: str
    cast: dict


# ---- warpcast ----

class Pfp(BaseModel):
    url: str
    verified: bool


class WarpBio(BaseModel):
    text: str
    mentions: Optional[list[str]] = []
    channelMentions: Optional[list[str]] = []


class WarpLocation(BaseModel):
    placeId: str
    description: str


class WarpProfile(BaseModel):
    bio: WarpBio
    location: WarpLocation


class User(BaseModel):
    fid: int
    username: str
    displayName: str
    pfp: Pfp
    profile: WarpProfile
    followerCount: int
    followingCount: int
    activeOnFcNetwork: bool


# ---- internal ----
class MatchStatus(Enum):
    NEW = 0
    USER_0_PLAYED = 1
    USER_1_PLAYED = 2
    DRAW = 3
    SETTLED = 4


class MatchState(BaseModel):
    match: str
    turn: int
    status: MatchStatus
    winner: Optional[int] = None
    loser: Optional[int] = None
    history0: list[int] = []
    history1: list[int] = []


class TournamentState(BaseModel):
    tournament: int
    # TODO ...
