"""Tests for pyfahrplan.config."""

from pyfahrplan.config import config_defaults, Colour


def test_config_defaults_keys():
    expected = {
        "speaker", "title", "track", "day", "start", "room",
        "conference", "show_abstract", "show_description", "sort",
        "tablefmt", "update_cache", "no_past",
    }
    assert set(config_defaults.keys()) == expected


def test_config_defaults_values():
    assert config_defaults["day"] == -1
    assert config_defaults["room"] == "all"
    assert config_defaults["conference"] == "all"
    assert config_defaults["no_past"] is False
    assert config_defaults["update_cache"] is False
    assert config_defaults["speaker"] is None
    assert config_defaults["title"] is None
    assert config_defaults["start"] is None


def test_colour_attributes():
    assert Colour.HEADER == "\033[95m"
    assert Colour.BOLD == "\033[1m"
    assert Colour.ENDC == "\033[0m"
    assert Colour.UNDERLINE == "\033[4m"
