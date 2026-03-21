"""Tests for the Fahrplan class in pyfahrplan.lib."""

import json
from unittest.mock import patch

import pytest
import requests_mock as rm

from pyfahrplan.lib import Fahrplan


def test_initialization_populates_flat_plans(mock_fahrplan_requests):
    fahrplan = Fahrplan()
    assert len(fahrplan.flat_plans) > 0


def test_errors_empty_on_success(mock_fahrplan_requests):
    fahrplan = Fahrplan()
    assert fahrplan.errors == []


def test_handles_json_decode_error():
    with rm.Mocker() as m:
        # One valid, rest invalid
        for c3 in range(32, 37):
            m.get(
                f"https://raw.githubusercontent.com/voc/{c3}C3_schedule/master/everything.schedule.json",
                text="not json",
            )
        for rc3 in ["rc3", "rc3_21"]:
            m.get(
                f"https://data.c3voc.de/{rc3}/everything.schedule.json",
                text="not json",
            )
        fahrplan = Fahrplan()
        assert len(fahrplan.errors) > 0
        assert any("Problem downloading" in e for e in fahrplan.errors)


def test_all_urls_fail_gives_empty_message():
    with rm.Mocker() as m:
        for c3 in range(32, 37):
            m.get(
                f"https://raw.githubusercontent.com/voc/{c3}C3_schedule/master/everything.schedule.json",
                text="bad",
            )
        for rc3 in ["rc3", "rc3_21"]:
            m.get(
                f"https://data.c3voc.de/{rc3}/everything.schedule.json",
                text="bad",
            )
        fahrplan = Fahrplan()
        assert any("Fahrplan empty" in e for e in fahrplan.errors)


def test_update_cache_clears_cache(mock_fahrplan_requests):
    with patch("pyfahrplan.lib.requests_cache") as mock_cache:
        mock_cache.install_cache = lambda *a, **kw: None
        fahrplan = Fahrplan(update_cache=True)
        mock_cache.clear.assert_called_once()


def test_flatten_produces_expected_fields(mock_fahrplan_requests):
    fahrplan = Fahrplan()
    expected_keys = {
        "conference_title", "conference_acronym", "day", "room", "title",
        "talk_guid", "talk_id", "talk_start", "talk_date", "talk_duration",
        "talk_description", "talk_abstract", "track", "speakers",
    }
    for plan in fahrplan.flat_plans:
        assert set(plan.keys()) == expected_keys


def test_get_conference_acronyms_sorted_unique(mock_fahrplan_requests):
    fahrplan = Fahrplan()
    acronyms = fahrplan.get_conference_acronyms()
    assert acronyms == sorted(set(acronyms))
    assert len(acronyms) > 0
