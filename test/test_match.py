"""
test cases for match gameplay logic utilities
"""

# lib
import time
import pytest

# src
from api.rps import resolve_match, resolve_match_state
from api.models import Match, MatchStatus, MatchState, Move, Gesture, Result


class TestResolveResult(object):
    def test_settled_live(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=3,
            slot=55,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        state = MatchState(match=match.id, turn=2, status=MatchStatus.SETTLED, winner=match.user0, loser=match.user1)

        m = resolve_match(match.round, match, state)

        assert m.result == Result.PLAYED
        assert m.winner == 7
        assert m.loser == 8

    def test_bye(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=0,
            slot=1,
            user0=15,
            user1=0,
            result=Result.PENDING
        )
        state = MatchState(match=match.id, turn=0, status=MatchStatus.NEW)

        m = resolve_match(match.round, match, state)

        assert m.result == Result.BYE
        assert m.winner == 15
        assert m.loser == 0

    def test_pending(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        state = MatchState(match=match.id, turn=0, status=MatchStatus.NEW)

        m = resolve_match(match.round, match, state)

        assert m.result == Result.PENDING
        assert m.winner is None
        assert m.loser is None

    def test_pass(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        state = MatchState(match=match.id, turn=0, status=MatchStatus.NEW)

        m = resolve_match(3, match, state)  # round has ended

        assert m.result == Result.PASS
        assert m.winner == 7
        assert m.loser == 8

    def test_draw(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        state = MatchState(match=match.id, turn=5, status=MatchStatus.DRAW)  # multiple moves played

        m = resolve_match(3, match, state)  # round has ended

        assert m.result == Result.DRAW
        assert m.winner == 7
        assert m.loser == 8

    def test_waiting(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        state = MatchState(match=match.id, turn=5, status=MatchStatus.USER_1_PLAYED)  # waiting

        m = resolve_match(match.round, match, state)  # round still going

        assert m.result == Result.PENDING
        assert m.winner is None
        assert m.loser is None

    def test_forfeit_0(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        state = MatchState(match=match.id, turn=5, status=MatchStatus.USER_0_PLAYED)

        m = resolve_match(3, match, state)  # round has ended

        assert m.result == Result.FORFEIT
        assert m.winner == 7
        assert m.loser == 8

    def test_forfeit_1(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        state = MatchState(match=match.id, turn=5, status=MatchStatus.USER_1_PLAYED)

        m = resolve_match(3, match, state)  # round has ended

        assert m.result == Result.FORFEIT
        assert m.winner == 8  # higher fid, but last to play
        assert m.loser == 7

    def test_invalid_state(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        state = MatchState(match=match.id, turn=5, status=MatchStatus.SETTLED, winner=16, loser=8)

        with pytest.raises(Exception):
            resolve_match(3, match, state)  # invalid winner


class TestResolveState(object):
    def test_new(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        moves = []
        s = resolve_match_state(match, moves)

        assert s.match == match.id
        assert s.turn == 0
        assert s.status == MatchStatus.NEW
        assert s.winner is None
        assert s.loser is None
        assert len(s.history0) == 0
        assert len(s.history1) == 0

    def test_draw(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        moves = [
            Move(id='m0', created=t, match='abcd', turn=0, user=7, move=Gesture.ROCK, signature='0x'),
            Move(id='m1', created=t, match='abcd', turn=0, user=8, move=Gesture.ROCK, signature='0x'),
            Move(id='m2', created=t, match='abcd', turn=1, user=8, move=Gesture.PAPER, signature='0x'),
            Move(id='m3', created=t, match='abcd', turn=1, user=7, move=Gesture.PAPER, signature='0x')
        ]
        s = resolve_match_state(match, moves)

        assert s.match == match.id
        assert s.turn == 2
        assert s.status == MatchStatus.DRAW
        assert s.winner is None
        assert s.loser is None
        assert len(s.history0) == 2
        assert len(s.history1) == 2
        assert s.history0[0] == Gesture.ROCK
        assert s.history1[0] == Gesture.ROCK
        assert s.history0[1] == Gesture.PAPER
        assert s.history1[1] == Gesture.PAPER

    def test_waiting_0(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        moves = [
            Move(id='m0', created=t, match='abcd', turn=0, user=7, move=Gesture.ROCK, signature='0x'),
            Move(id='m1', created=t, match='abcd', turn=0, user=8, move=Gesture.ROCK, signature='0x'),
            Move(id='m2', created=t, match='abcd', turn=1, user=7, move=Gesture.PAPER, signature='0x'),
        ]
        s = resolve_match_state(match, moves)

        assert s.match == match.id
        assert s.turn == 1
        assert s.status == MatchStatus.USER_0_PLAYED
        assert s.winner is None
        assert s.loser is None
        assert len(s.history0) == 1
        assert len(s.history1) == 1
        assert s.history0[0] == Gesture.ROCK
        assert s.history1[0] == Gesture.ROCK

    def test_waiting_1(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        moves = [
            Move(id='m0', created=t, match='abcd', turn=0, user=7, move=Gesture.ROCK, signature='0x'),
            Move(id='m1', created=t, match='abcd', turn=0, user=8, move=Gesture.ROCK, signature='0x'),
            Move(id='m2', created=t, match='abcd', turn=1, user=8, move=Gesture.PAPER, signature='0x'),
            Move(id='m3', created=t, match='abcd', turn=1, user=7, move=Gesture.PAPER, signature='0x'),
            Move(id='m4', created=t, match='abcd', turn=2, user=8, move=Gesture.PAPER, signature='0x')
        ]
        s = resolve_match_state(match, moves)

        assert s.match == match.id
        assert s.turn == 2
        assert s.status == MatchStatus.USER_1_PLAYED
        assert s.winner is None
        assert s.loser is None
        assert len(s.history0) == 2
        assert len(s.history1) == 2

    def test_settled(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        moves = [
            Move(id='m0', created=t, match='abcd', turn=0, user=7, move=Gesture.ROCK, signature='0x'),
            Move(id='m1', created=t, match='abcd', turn=0, user=8, move=Gesture.ROCK, signature='0x'),
            Move(id='m2', created=t, match='abcd', turn=1, user=8, move=Gesture.SCISSORS, signature='0x'),
            Move(id='m3', created=t, match='abcd', turn=1, user=7, move=Gesture.PAPER, signature='0x')
        ]
        s = resolve_match_state(match, moves)

        assert s.match == match.id
        assert s.turn == 1
        assert s.status == MatchStatus.SETTLED
        assert s.winner == 8
        assert s.loser == 7
        assert len(s.history0) == 2
        assert len(s.history1) == 2
        assert s.history0[0] == Gesture.ROCK
        assert s.history1[0] == Gesture.ROCK
        assert s.history0[1] == Gesture.PAPER
        assert s.history1[1] == Gesture.SCISSORS

    def test_invalid_turns(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        moves = [
            Move(id='m0', created=t, match='abcd', turn=0, user=7, move=Gesture.ROCK, signature='0x'),
            Move(id='m1', created=t, match='abcd', turn=1, user=8, move=Gesture.ROCK, signature='0x'),
            Move(id='m2', created=t, match='abcd', turn=1, user=8, move=Gesture.SCISSORS, signature='0x'),
            Move(id='m3', created=t, match='abcd', turn=2, user=7, move=Gesture.PAPER, signature='0x')
        ]
        # misaligned turn indices
        with pytest.raises(Exception):
            resolve_match_state(match, moves)

    def test_invalid_counts(self):
        t = int(time.time())
        match = Match(
            id='abcd',
            created=t,
            updated=t,
            tournament=1,
            round=2,
            slot=1,
            user0=7,
            user1=8,
            result=Result.PENDING
        )
        moves = [
            Move(id='m0', created=t, match='abcd', turn=0, user=7, move=Gesture.ROCK, signature='0x'),
            Move(id='m1', created=t, match='abcd', turn=0, user=8, move=Gesture.ROCK, signature='0x'),
            Move(id='m2', created=t, match='abcd', turn=1, user=7, move=Gesture.SCISSORS, signature='0x'),
            Move(id='m3', created=t, match='abcd', turn=1, user=7, move=Gesture.PAPER, signature='0x')
        ]
        # too many user0 moves
        with pytest.raises(Exception):
            resolve_match_state(match, moves)
