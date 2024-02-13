"""
test cases for tournament logic utilities
"""

# lib
import pytest

# src
from api.rps import current_round, round_size, match_slot, parent_slots


class TestCurrentRound(object):
    def test_first(self):
        start = 1707541200  # 2024/02/10 00:00 eastern
        curr = 1707564600  # 630a

        r = current_round(start, curr)

        assert r == 0

    def test_many(self):
        start = 1707541200  # 2024/02/10 00:00 eastern
        curr = 1708534800  # 2023/02/21 noon

        r = current_round(start, curr)

        assert r == 11

    def test_before(self):
        start = 1707541200  # 2024/02/10 00:00 eastern
        curr = 1707539400  # 1130p night before

        r = current_round(start, curr)

        assert r == -1

    def test_offset_first(self):
        start = 1707519600  # 2024/02/09 18:00 eastern
        curr = 1707564600  # 630a

        r = current_round(start, curr)

        assert r == 0

    def test_offset_first_later(self):
        start = 1707519600  # 2024/02/09 18:00 eastern
        curr = 1707613200  # 20:00p

        r = current_round(start, curr)

        assert r == 0

    def test_offset_before(self):
        start = 1707519600  # 2024/02/09 18:00 eastern
        curr = 1707539400  # 1130p night before

        r = current_round(start, curr)

        assert start < curr  # note curr is technically after start, but we round to the increment
        assert r == -1


class TestRoundSize(object):
    def test_first_simple(self):
        sz = round_size(64, 0)
        assert sz == 64

    def test_second_simple(self):
        sz = round_size(64, 1)
        assert sz == 32

    def test_final4_simple(self):
        sz = round_size(64, 4)
        assert sz == 4

    def test_over_simple(self):
        sz = round_size(64, 10)
        assert sz == 1

    def test_first_uneven(self):
        sz = round_size(80, 0)
        assert sz == 128

    def test_second_uneven(self):
        sz = round_size(80, 1)
        assert sz == 64

    def test_finals_uneven(self):
        sz = round_size(80, 6)
        assert sz == 2

    def test_over_uneven(self):
        sz = round_size(80, 10)
        assert sz == 1


class TestMatchSlot(object):
    def test_0_1(self):
        slot = match_slot(64, 0, 1)
        assert slot == 0

    def test_0_2(self):
        slot = match_slot(64, 0, 2)
        assert slot == 1

    def test_0_9(self):
        slot = match_slot(64, 0, 9)
        assert slot == 8

    def test_0_32(self):
        slot = match_slot(64, 0, 32)
        assert slot == 31

    def test_0_33(self):
        slot = match_slot(64, 0, 33)
        assert slot == 31

    def test_0_56(self):
        slot = match_slot(64, 0, 56)
        assert slot == 8

    def test_0_63(self):
        slot = match_slot(64, 0, 63)
        assert slot == 1

    def test_0_64(self):
        slot = match_slot(64, 0, 64)
        assert slot == 0

    def test_1_1(self):
        slot = match_slot(64, 1, 1)
        assert slot == 0

    def test_1_2(self):
        slot = match_slot(64, 1, 2)
        assert slot == 1

    def test_1_9(self):
        slot = match_slot(64, 1, 9)
        assert slot == 8

    def test_1_32(self):
        slot = match_slot(64, 1, 32)
        assert slot == 0  # match up against 1v64 winner

    def test_1_33(self):
        slot = match_slot(64, 1, 33)
        assert slot == 0

    def test_1_56(self):
        slot = match_slot(64, 1, 56)
        assert slot == 8

    def test_1_63(self):
        slot = match_slot(64, 1, 63)
        assert slot == 1

    def test_1_64(self):
        slot = match_slot(64, 1, 64)
        assert slot == 0

    def test_elite8_1(self):
        slot = match_slot(64, 3, 1)
        assert slot == 0

    def test_elite8_5(self):
        slot = match_slot(64, 3, 5)
        assert slot == 3  # 4 vs 5

    def test_elite8_63(self):
        slot = match_slot(64, 3, 63)
        assert slot == 1  # upset 2

    def test_final_23(self):
        slot = match_slot(64, 5, 23)
        assert slot == 0

    def test_final_42(self):
        slot = match_slot(64, 5, 42)
        assert slot == 0

    def test_elite8_1_uneven(self):
        slot = match_slot(50, 3, 1)
        assert slot == 0

    def test_elite8_5_uneven(self):
        slot = match_slot(50, 3, 5)
        assert slot == 3

    def test_elite8_30_uneven(self):
        slot = match_slot(50, 3, 30)
        assert slot == 2

    def test_uneven_invalid(self):
        with pytest.raises(ValueError):
            match_slot(50, 3, 51)


class TestParentSlots(object):

    def test_1_0(self):
        a, b = parent_slots(64, 1, 0)
        assert a == 0
        assert b == 31

    def test_1_2(self):
        a, b = parent_slots(64, 1, 2)
        assert a == 2
        assert b == 29

    def test_1_8(self):
        a, b = parent_slots(64, 1, 8)
        assert a == 8
        assert b == 23  # from 24 v 41

    def test_final(self):
        a, b = parent_slots(64, 5, 0)
        assert a == 0
        assert b == 1

    def test_final_uneven(self):
        a, b = parent_slots(48, 5, 0)
        assert a == 0
        assert b == 1

    def test_final_invalid(self):
        with pytest.raises(ValueError):
            parent_slots(64, 5, 1)
