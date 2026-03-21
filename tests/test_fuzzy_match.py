"""Tests for fuzzy_match() and fuzzy filtering in filter_talk()."""

from pyfahrplan.lib import fuzzy_match, filter_talk
from tests.data.test_data import test_flat_talks


# --- fuzzy_match unit tests ---

def test_empty_query_matches_anything():
    assert fuzzy_match("", "anything") is True


def test_exact_substring():
    assert fuzzy_match("python", "Introduction to Python Programming") is True


def test_case_insensitive():
    assert fuzzy_match("PYTHON", "introduction to python programming") is True


def test_multi_token_both_match():
    """Each space-separated token must match independently."""
    assert fuzzy_match("py scr", "Python Scripting") is True


def test_multi_token_one_fails():
    assert fuzzy_match("py xyz", "Python Scripting") is False


def test_typo_missing_letter():
    """'pythn' should fuzzy-match 'python'."""
    assert fuzzy_match("pythn", "Python Scripting") is True


def test_typo_swapped_letter():
    """'pyhton' should fuzzy-match 'python'."""
    assert fuzzy_match("pyhton", "Learn Python Today") is True


def test_typo_extra_letter():
    """'pythoon' should fuzzy-match 'python'."""
    assert fuzzy_match("pythoon", "Python Workshop") is True


def test_completely_wrong_no_match():
    assert fuzzy_match("quantum", "Python Scripting") is False


def test_multi_token_with_typo():
    """'pythn scr' matches 'Python Scripting' - combined multi-token + typo."""
    assert fuzzy_match("pythn scr", "Python Scripting") is True


def test_short_token_substring():
    """Short tokens like 'op' should match via substring."""
    assert fuzzy_match("op", "Opening Event") is True


def test_no_false_positive_on_short_different_words():
    """'zz' should not match 'ab'."""
    assert fuzzy_match("zz", "ab cd ef") is False


# --- filter_talk integration tests for fuzzy ---

def test_filter_talk_fuzzy_speaker():
    """Typo in speaker name still matches."""
    # test_flat_talks[0] has speaker 'Carina Haupt, Linus Neumann'
    assert filter_talk(test_flat_talks[0], speaker="Carin") is True
    assert filter_talk(test_flat_talks[0], speaker="Carinaa") is True


def test_filter_talk_fuzzy_title():
    """Typo in title still matches."""
    # test_flat_talks[0] has title 'Opening Event'
    assert filter_talk(test_flat_talks[0], title="Openng") is True
    assert filter_talk(test_flat_talks[0], title="Opning Evnt") is True


def test_filter_talk_fuzzy_track():
    # test_flat_talks[2] has track 'self organized sessions'
    assert filter_talk(test_flat_talks[2], track="self org") is True
    assert filter_talk(test_flat_talks[2], track="organzed") is True


def test_filter_talk_conference_stays_exact():
    """Conference filter should NOT fuzzy-match similar acronyms."""
    # '33c3' should not match a talk with conference_acronym '32c3'
    assert filter_talk(test_flat_talks[0], conference="33c3") is False


def test_filter_talk_room_stays_exact():
    """Room filter should NOT fuzzy-match."""
    # test_flat_talks[0] has room 'Hall 1' - 'Hall 10' should not match
    assert filter_talk(test_flat_talks[0], room="Hall 10") is False
