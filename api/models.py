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
    PLAY = 1
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
    mentioned_profiles: list[str]


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
    viewer_context: Viewer


class Button(BaseModel):
    title: str
    index: int
    action_type: str


class Input(BaseModel):
    text: str


class ValidatedMessage(BaseModel):
    object: str
    interactor: Interactor
    button: Button
    input: Input
    cast: dict
