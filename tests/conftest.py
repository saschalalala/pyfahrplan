from pathlib import Path

import pytest

from tests.data.test_data import test_flat_talks

data_dir = Path(__file__).parent / "data"


@pytest.fixture
def mock_schedule_data(tmp_path, monkeypatch):
    """Point Fahrplan.DATA_DIR at a tmp dir populated with test JSON files."""
    import shutil
    for src in data_dir.glob("*.json"):
        # Map test filenames (e.g. 32.json) to expected names (e.g. 32c3.json)
        name = src.stem
        if name.isdigit():
            dest_name = f"{name}c3.json"
        else:
            dest_name = f"{name}.json"
        shutil.copy(src, tmp_path / dest_name)

    import pyfahrplan.lib
    monkeypatch.setattr(pyfahrplan.lib, "DATA_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def sample_talks():
    """Return the test_flat_talks list."""
    return list(test_flat_talks)


@pytest.fixture
def single_talk():
    """Return the first test talk (32c3 Opening Event)."""
    return dict(test_flat_talks[0])


@pytest.fixture
def make_talk():
    """Factory fixture to create talk dicts with sensible defaults."""
    defaults = {
        "conference_title": "Test Conference",
        "conference_acronym": "testc3",
        "day": 1,
        "room": "Room 1",
        "title": "Test Talk",
        "talk_guid": "test-guid-0001",
        "talk_id": 9999,
        "talk_start": "10:00",
        "talk_date": "2024-01-01T10:00:00+01:00",
        "talk_duration": "01:00",
        "talk_description": "A test talk description.",
        "talk_abstract": "A test talk abstract.",
        "track": "Testing",
        "speakers": "Test Speaker",
    }

    def _make(**overrides):
        talk = dict(defaults)
        talk.update(overrides)
        return talk

    return _make
