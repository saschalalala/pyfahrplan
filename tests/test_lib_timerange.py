"""Tests for is_talk_in_timerange() in pyfahrplan.lib."""

import pytest
from pyfahrplan.lib import is_talk_in_timerange


def test_during_talk(make_talk):
    talk = make_talk(talk_start="11:00", talk_duration="00:30")
    assert is_talk_in_timerange(talk, "11:15") is True


def test_at_exact_start(make_talk):
    talk = make_talk(talk_start="11:00", talk_duration="00:30")
    assert is_talk_in_timerange(talk, "11:00") is True


def test_at_exact_end(make_talk):
    talk = make_talk(talk_start="11:00", talk_duration="00:30")
    assert is_talk_in_timerange(talk, "11:30") is True


def test_before_talk(make_talk):
    talk = make_talk(talk_start="11:00", talk_duration="00:30")
    assert is_talk_in_timerange(talk, "10:30") is False


def test_after_talk(make_talk):
    talk = make_talk(talk_start="11:00", talk_duration="00:30")
    assert is_talk_in_timerange(talk, "12:00") is False


def test_same_hour_different_minute(make_talk):
    """Talk at 11:45 should match query at 11:00 (same hour)."""
    talk = make_talk(talk_start="11:45", talk_duration="00:30")
    assert is_talk_in_timerange(talk, "11:00") is True


def test_different_hour(make_talk):
    talk = make_talk(talk_start="14:00", talk_duration="01:00")
    assert is_talk_in_timerange(talk, "11:00") is False


def test_short_duration(make_talk):
    """13-minute talk (like test_flat_talks[3])."""
    talk = make_talk(talk_start="02:12", talk_duration="0:13")
    assert is_talk_in_timerange(talk, "02:12") is True


def test_long_duration(make_talk):
    """1h15m talk, query midway through."""
    talk = make_talk(talk_start="18:45", talk_duration="1:15")
    assert is_talk_in_timerange(talk, "19:30") is True


def test_long_duration_outside(make_talk):
    talk = make_talk(talk_start="18:45", talk_duration="1:15")
    assert is_talk_in_timerange(talk, "21:00") is False
