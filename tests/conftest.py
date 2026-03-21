import json
from pathlib import Path

import pytest
import requests_mock as rm

from tests.data.test_data import test_flat_talks

data_dir = Path(__file__).parent / "data"


@pytest.fixture
def mock_fahrplan_requests():
    """Mock all Fahrplan HTTP requests using local JSON test data."""
    with rm.Mocker() as m:
        for c3 in range(32, 37):
            json_file = data_dir / f"{c3}.json"
            fahrplan_data = json.load(open(json_file, "r"))
            m.get(
                f"https://raw.githubusercontent.com/voc/{c3}C3_schedule/master/everything.schedule.json",
                text=json.dumps(fahrplan_data),
            )
        for rc3 in ["rC3", "rC3_21"]:
            json_file = data_dir / f"{rc3.lower()}.json"
            rc3_data = json.load(open(json_file, "r"))
            m.get(
                f"https://data.c3voc.de/{rc3.lower()}/everything.schedule.json",
                text=json.dumps(rc3_data),
            )
        yield m


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
