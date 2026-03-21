"""Tests for the Fahrplan class in pyfahrplan.lib."""

from pathlib import Path

import pytest

from pyfahrplan.lib import Fahrplan


def test_initialization_populates_flat_plans(mock_schedule_data):
    fahrplan = Fahrplan()
    assert len(fahrplan.flat_plans) > 0


def test_errors_empty_on_success(mock_schedule_data):
    fahrplan = Fahrplan()
    assert fahrplan.errors == []


def test_missing_db_gives_error(tmp_path, monkeypatch):
    import pyfahrplan.lib
    monkeypatch.setattr(pyfahrplan.lib, "DB_PATH", tmp_path / "nonexistent.db")
    fahrplan = Fahrplan()
    assert any("No talks database found" in e for e in fahrplan.errors)


def test_produces_expected_fields(mock_schedule_data):
    fahrplan = Fahrplan()
    expected_keys = {
        "conference_title", "conference_acronym", "day", "room", "title",
        "talk_guid", "talk_id", "talk_start", "talk_date", "talk_duration",
        "talk_description", "talk_abstract", "track", "speakers",
        "_start_parsed", "_start_end_parsed", "_date_end_parsed",
    }
    for plan in fahrplan.flat_plans:
        assert set(plan.keys()) == expected_keys


def test_get_conference_acronyms_sorted_unique(mock_schedule_data):
    fahrplan = Fahrplan()
    acronyms = fahrplan.get_conference_acronyms()
    assert acronyms == sorted(set(acronyms))
    assert len(acronyms) > 0
