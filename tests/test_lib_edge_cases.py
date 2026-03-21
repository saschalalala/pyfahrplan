"""Edge case tests for filter_talk(), filter_talks(), and sort_talks()."""

import datetime as dt

from pyfahrplan.lib import filter_talk, filter_talks, sort_talks
from tests.data.test_data import test_flat_talks


def test_filter_talk_no_filters_returns_true():
    assert filter_talk(test_flat_talks[0]) is True


def test_filter_talk_case_insensitive_conference():
    assert filter_talk(test_flat_talks[0], conference="32C3") is True


def test_filter_talk_partial_match_speaker():
    assert filter_talk(test_flat_talks[0], speaker="Carina") is True


def test_filter_talk_partial_match_room():
    assert filter_talk(test_flat_talks[0], room="Hall") is True


def test_filter_talk_multiple_filters_must_all_match():
    # Speaker is in 32c3, not 33c3
    assert filter_talk(test_flat_talks[0], speaker="Carina", conference="33c3") is False


def test_filter_talk_day_zero_is_valid():
    assert filter_talk(test_flat_talks[0], day=0) is True


def test_filter_talk_day_minus_one_matches_all():
    assert filter_talk(test_flat_talks[0], day=-1) is True


def test_filter_talk_start_none_matches_all():
    assert filter_talk(test_flat_talks[0], start=None) is True


def test_filter_talk_filter_past_false_keeps_old_talks():
    assert filter_talk(test_flat_talks[0], filter_past=False) is True


def test_filter_talk_filter_past_with_future_now():
    """When now is before talk end, talk is not filtered as past."""
    early = dt.datetime(2015, 12, 27, 11, 15, 0, tzinfo=dt.timezone(dt.timedelta(hours=1)))
    assert filter_talk(test_flat_talks[0], filter_past=True, now=early) is True


def test_filter_talk_empty_speaker_field():
    """Talk with empty speakers should not match a specific speaker filter."""
    assert filter_talk(test_flat_talks[2], speaker="Someone") is False


def test_filter_talk_track_filter():
    assert filter_talk(test_flat_talks[0], track="CCC") is True
    assert filter_talk(test_flat_talks[0], track="nonexistent") is False


def test_filter_talks_empty_list():
    assert filter_talks([], conference="32c3") == []


def test_filter_talks_no_matches():
    assert filter_talks(test_flat_talks, conference="nonexistent") == []


def test_filter_talks_preserves_order():
    results = filter_talks(test_flat_talks, conference="all")
    assert results == test_flat_talks


def test_sort_talks_empty_list():
    assert sort_talks([], sort_key="day") == []


def test_sort_talks_single_element():
    result = sort_talks([test_flat_talks[0]], sort_key="day")
    assert result == [test_flat_talks[0]]


def test_sort_talks_by_title():
    result = sort_talks(test_flat_talks, sort_key="title")
    titles = [t["title"] for t in result]
    assert titles == sorted(titles)


def test_sort_talks_returns_new_list():
    original = list(test_flat_talks)
    result = sort_talks(original, sort_key="day")
    assert result is not original


def test_sort_talks_none_key_returns_copy():
    result = sort_talks(test_flat_talks, sort_key=None)
    assert result == test_flat_talks
    assert result is not test_flat_talks


def test_sort_talks_missing_key():
    """sort_key that doesn't exist falls back to empty string for all."""
    result = sort_talks(test_flat_talks, sort_key="nonexistent")
    assert len(result) == len(test_flat_talks)
