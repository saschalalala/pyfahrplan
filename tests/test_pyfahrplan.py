from pyfahrplan import __version__
from pyfahrplan.lib import Fahrplan, filter_talk, filter_talks, sort_talks
from .data.test_data import test_flat_talks


def test_version():
    assert __version__ == '1.1.0'


def test_fahrplan_initialization(mock_schedule_data):
    fahrplan = Fahrplan()
    assert len(fahrplan.flat_plans) > 0


def test_fahrplan_get_conference_acronyms(mock_schedule_data):
    fahrplan = Fahrplan()
    acronyms = fahrplan.get_conference_acronyms()
    assert "32c3" in acronyms
    assert "36c3" in acronyms
    assert len(acronyms) > 0


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


def test_filter_talks():
    results = filter_talks(test_flat_talks, conference="32c3")
    assert len(results) == 1
    assert results[0]["conference_acronym"] == "32c3"


def test_filter_talks_all():
    results = filter_talks(test_flat_talks, conference="all")
    assert len(results) == len(test_flat_talks)


def test_sort_talks():
    sorted_by_day = sort_talks(test_flat_talks, sort_key="day")
    assert sorted_by_day[0]["day"] <= sorted_by_day[-1]["day"]


def test_sort_talks_reverse():
    sorted_rev = sort_talks(test_flat_talks, sort_key="day", reverse=True)
    assert sorted_rev[0]["day"] >= sorted_rev[-1]["day"]


def test_sort_talks_none():
    result = sort_talks(test_flat_talks, sort_key=None)
    assert result == test_flat_talks
