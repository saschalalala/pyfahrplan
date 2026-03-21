"""Tests for the Fahrplan class in pyfahrplan.lib."""

import json
from pathlib import Path

import pytest

from pyfahrplan.lib import Fahrplan


def test_initialization_populates_flat_plans(mock_schedule_data):
    fahrplan = Fahrplan()
    assert len(fahrplan.flat_plans) > 0


def test_errors_empty_on_success(mock_schedule_data):
    fahrplan = Fahrplan()
    assert fahrplan.errors == []


def test_handles_invalid_json(mock_schedule_data):
    # Corrupt one file
    (mock_schedule_data / "32c3.json").write_text("not json")
    fahrplan = Fahrplan()
    assert len(fahrplan.errors) > 0
    assert any("Problem loading" in e for e in fahrplan.errors)


def test_all_files_missing_gives_empty_message(tmp_path, monkeypatch):
    import pyfahrplan.lib
    monkeypatch.setattr(pyfahrplan.lib, "DATA_DIR", tmp_path)
    fahrplan = Fahrplan()
    assert any("No schedules found" in e for e in fahrplan.errors)


def test_flatten_produces_expected_fields(mock_schedule_data):
    fahrplan = Fahrplan()
    expected_keys = {
        "conference_title", "conference_acronym", "day", "room", "title",
        "talk_guid", "talk_id", "talk_start", "talk_date", "talk_duration",
        "talk_description", "talk_abstract", "track", "speakers",
    }
    for plan in fahrplan.flat_plans:
        assert set(plan.keys()) == expected_keys


def test_get_conference_acronyms_sorted_unique(mock_schedule_data):
    fahrplan = Fahrplan()
    acronyms = fahrplan.get_conference_acronyms()
    assert acronyms == sorted(set(acronyms))
    assert len(acronyms) > 0
