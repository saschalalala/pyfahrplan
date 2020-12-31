from functools import wraps
import json
from pathlib import Path
import os

import requests_mock

from pyfahrplan import __version__
from pyfahrplan.pyfahrplan import Fahrplan, filter_talk
from .data.test_data import test_flat_talks

script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
data_dir = script_dir / "data"


def mock_requests(func):
    print("decorator")

    @wraps(func)
    def function_wrapper():
        print("function wrapper")
        with requests_mock.Mocker() as m:
            for c3 in range(32, 37):
                json_file = Path(f"{c3}.json")
                fahrplan_data = json.load(open(data_dir / json_file, "r"))
                m.get(
                    f"https://raw.githubusercontent.com/voc/{c3}C3_schedule/master/everything.schedule.json",
                    text=json.dumps(fahrplan_data),
                )
            json_file = Path("rc3.json")
            rc3_data = json.load(open(data_dir / json_file, "r"))
            m.get("https://data.c3voc.de/rC3/everything.schedule.json", text=json.dumps(rc3_data))
            return func()

    return function_wrapper


def test_version():
    assert __version__ == '1.0.12'


@mock_requests
def test_fahrplan_initialization():
    fahrplan = Fahrplan()
    assert len(fahrplan.flat_plans) > 0


def test_conference_filter():
    filtered_talk = filter_talk(test_flat_talks[0], conference="32c3")
    filtered_talk_2 = filter_talk(test_flat_talks[0], conference="rc")
    assert filtered_talk is True and filtered_talk_2 is False


def test_speaker_filter():
    filtered_talk = filter_talk(test_flat_talks[0], conference="32c3", speaker="CaRiNa")
    filtered_talk_2 = filter_talk(test_flat_talks[0], conference="32c3", speaker="CaRiNa2")
    assert filtered_talk is True and filtered_talk_2 is False


def test_title_filter():
    filtered_talk = filter_talk(test_flat_talks[0], conference="32c3", title="OPENIng")
    filtered_talk_2 = filter_talk(test_flat_talks[0], conference="32c3", speaker="0p3N!ng")
    assert filtered_talk is True and filtered_talk_2 is False


def test_day_filter():
    filtered_talk = filter_talk(test_flat_talks[0], conference="32c3", day=0)
    filtered_talk_2 = filter_talk(test_flat_talks[0], conference="32c3", day=5)
    assert filtered_talk is True and filtered_talk_2 is False


def test_start_filter():
    filtered_talk = filter_talk(test_flat_talks[0], conference="32c3", start="11:00")
    filtered_talk_2 = filter_talk(test_flat_talks[0], conference="32c3", start="12:00")
    assert filtered_talk is True and filtered_talk_2 is False


def test_room_filter():
    filtered_talk = filter_talk(test_flat_talks[0], conference="32c3", room="Hall 1")
    filtered_talk_2 = filter_talk(test_flat_talks[0], conference="32c3", room="Hall 10")
    assert filtered_talk is True and filtered_talk_2 is False


def test_filter_past_filter():
    filtered_talk = filter_talk(test_flat_talks[0], conference="32c3", filter_past=False)
    filtered_talk_2 = filter_talk(test_flat_talks[0], conference="32c3", filter_past=True)
    assert filtered_talk is True and filtered_talk_2 is False
