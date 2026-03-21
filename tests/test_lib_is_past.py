"""Tests for is_talk_in_past() in pyfahrplan.lib."""

import datetime as dt

from pyfahrplan.lib import is_talk_in_past


def test_talk_ended(make_talk):
    talk = make_talk(talk_date="2015-12-27T11:00:00+01:00", talk_duration="00:30")
    now = dt.datetime(2015, 12, 27, 12, 0, 0, tzinfo=dt.timezone(dt.timedelta(hours=1)))
    assert is_talk_in_past(talk, now) is True


def test_talk_ongoing(make_talk):
    talk = make_talk(talk_date="2015-12-27T11:00:00+01:00", talk_duration="00:30")
    now = dt.datetime(2015, 12, 27, 11, 15, 0, tzinfo=dt.timezone(dt.timedelta(hours=1)))
    assert is_talk_in_past(talk, now) is False


def test_talk_future(make_talk):
    talk = make_talk(talk_date="2025-12-27T11:00:00+01:00", talk_duration="00:30")
    now = dt.datetime(2024, 1, 1, 0, 0, 0, tzinfo=dt.timezone(dt.timedelta(hours=1)))
    assert is_talk_in_past(talk, now) is False


def test_exactly_at_end(make_talk):
    """now == end exactly -> False (strict >)."""
    talk = make_talk(talk_date="2015-12-27T11:00:00+01:00", talk_duration="00:30")
    now = dt.datetime(2015, 12, 27, 11, 30, 0, tzinfo=dt.timezone(dt.timedelta(hours=1)))
    assert is_talk_in_past(talk, now) is False


def test_one_second_after_end(make_talk):
    talk = make_talk(talk_date="2015-12-27T11:00:00+01:00", talk_duration="00:30")
    now = dt.datetime(2015, 12, 27, 11, 30, 1, tzinfo=dt.timezone(dt.timedelta(hours=1)))
    assert is_talk_in_past(talk, now) is True


def test_long_duration_not_past(make_talk):
    talk = make_talk(talk_date="2015-12-27T18:45:00+01:00", talk_duration="1:15")
    now = dt.datetime(2015, 12, 27, 19, 30, 0, tzinfo=dt.timezone(dt.timedelta(hours=1)))
    assert is_talk_in_past(talk, now) is False


def test_long_duration_past(make_talk):
    talk = make_talk(talk_date="2015-12-27T18:45:00+01:00", talk_duration="1:15")
    now = dt.datetime(2015, 12, 27, 20, 1, 0, tzinfo=dt.timezone(dt.timedelta(hours=1)))
    assert is_talk_in_past(talk, now) is True
