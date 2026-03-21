import datetime as dt
from dateutil.parser import parse
import json
from pathlib import Path

from pyfahrplan.config import config_defaults as cli_defaults, Colour
from pyfahrplan.schedules import SCHEDULE_SOURCES

DATA_DIR = Path(__file__).parent / "data"


def _parse_duration(duration_str: str) -> dt.timedelta:
    """Parse a duration string like '1:15' or '25:00' into a timedelta."""
    parts = duration_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0
    return dt.timedelta(hours=hours, minutes=minutes)


class Fahrplan:
    def __init__(self):
        self.fahrplans = []
        self.flat_plans = []
        self.errors = []
        self._load_schedules()
        self.flatten_fahrplans()

    def _load_schedules(self):
        self.fahrplans = []
        for filename in SCHEDULE_SOURCES:
            path = DATA_DIR / filename
            try:
                with open(path) as f:
                    self.fahrplans.append(json.load(f)["schedule"])
            except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
                self.errors.append(
                    f"Problem loading schedule {filename}: {e}"
                )
        if not self.fahrplans:
            self.errors.append("No schedules found. Run the update-schedules workflow to download data.")

    def flatten_fahrplans(self):
        self.flat_plans = []
        for schedule in self.fahrplans:
            for day in schedule["conference"]["days"]:
                for room_name, room in day["rooms"].items():
                    for talk in room:
                        start_parsed = parse(talk["start"])
                        duration_td = _parse_duration(talk["duration"])
                        date_parsed = parse(talk["date"])
                        current_talk = {
                            "conference_title": schedule["conference"]["title"],
                            "conference_acronym": schedule["conference"]["acronym"],
                            "day": day["index"],
                            "room": room_name,
                            "title": talk["title"],
                            "talk_guid": talk.get("guid"),
                            "talk_id": talk["id"],
                            "talk_start": talk["start"],
                            "talk_date": talk["date"],
                            "talk_duration": talk["duration"],
                            "talk_description": ""
                            if talk["description"] is None
                            else talk["description"],
                            "talk_abstract": "" if talk["abstract"] is None else talk["abstract"],
                            "track": "" if talk["track"] is None else talk["track"],
                            "speakers": ", ".join(
                                [
                                    person.get(
                                        "public_name",
                                        person.get("full_public_name", ""),
                                    )
                                    for person in talk.get("persons", [])
                                ]
                            ),
                            "_start_parsed": start_parsed,
                            "_start_end_parsed": start_parsed + duration_td,
                            "_date_end_parsed": date_parsed + duration_td,
                        }
                        self.flat_plans.append(current_talk)

    def get_conference_acronyms(self):
        """Return sorted list of unique conference acronyms."""
        return sorted(set(t["conference_acronym"] for t in self.flat_plans))


def is_talk_in_timerange(talk: dict, start: str) -> bool:
    start_time = parse(start)
    talk_start = talk.get("_start_parsed") or parse(talk["talk_start"])
    talk_end = talk.get("_start_end_parsed")
    if talk_end is None:
        talk_end = talk_start + _parse_duration(talk["talk_duration"])
    current_hour_end = start_time.replace(minute=59)
    current_hour_begin = start_time.replace(minute=0)
    talk_in_timerange = talk_start <= start_time <= talk_end
    talk_starts_in_current_hour = current_hour_begin <= talk_start <= current_hour_end
    return talk_in_timerange or talk_starts_in_current_hour


def is_talk_in_past(talk: dict, now: dt.datetime) -> bool:
    end = talk.get("_date_end_parsed")
    if end is None:
        end = parse(talk["talk_date"]) + _parse_duration(talk["talk_duration"])
    return now > end


def filter_talk(
    talk: dict = {},
    speaker: str = cli_defaults["speaker"],
    title: str = cli_defaults["title"],
    track: str = cli_defaults["track"],
    day: int = cli_defaults["day"],
    start: str = cli_defaults["start"],
    room: str = cli_defaults["room"],
    conference: str = cli_defaults["conference"],
    filter_past: bool = cli_defaults["no_past"],
    now: dt.datetime = dt.datetime.now().astimezone(),
) -> bool:
    """
    Some simple filter rules as functions
    """

    def generic_in_match(filter_value, filter_key, talk_attribute):
        return (
            filter_value == cli_defaults[filter_key]
            or filter_value.lower() in talk[talk_attribute].lower()
        )

    def day_matches():
        return day == -1 or day == talk["day"]

    def start_matches():
        return start is None or is_talk_in_timerange(talk, start)

    def filtered_as_past():
        return filter_past and is_talk_in_past(talk, now)

    return (
        generic_in_match(conference, "conference", "conference_acronym")
        and generic_in_match(speaker, "speaker", "speakers")
        and generic_in_match(title, "title", "title")
        and generic_in_match(track, "track", "track")
        and day_matches()
        and start_matches()
        and generic_in_match(room, "room", "room")
        and not filtered_as_past()
    )


def filter_talks(talks, **kwargs):
    """Filter a list of talks and return matching ones."""
    return [t for t in talks if filter_talk(t, **kwargs)]


def sort_talks(talks, sort_key=None, reverse=False):
    """Sort talks by a given key. Returns a new sorted list."""
    if sort_key is None:
        return list(talks)
    return sorted(talks, key=lambda t: str(t.get(sort_key, "")), reverse=reverse)
