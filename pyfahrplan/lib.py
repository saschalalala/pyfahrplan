import datetime as dt
from dateutil.parser import parse
from pathlib import Path
import sqlite3

from pyfahrplan.config import config_defaults as cli_defaults, Colour

DB_PATH = Path(__file__).parent / "data" / "talks.db"

TALK_COLUMNS = [
    "conference_title", "conference_acronym", "day", "room", "title",
    "talk_guid", "talk_id", "talk_start", "talk_date", "talk_duration",
    "talk_description", "talk_abstract", "track", "speakers",
    "start_parsed", "start_end_parsed", "date_end_parsed",
]


def _parse_duration(duration_str: str) -> dt.timedelta:
    """Parse a duration string like '1:15' or '25:00' into a timedelta."""
    parts = duration_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0
    return dt.timedelta(hours=hours, minutes=minutes)


def _hydrate_talk(talk: dict) -> dict:
    """Convert ISO datetime strings from DB into datetime objects."""
    talk["_start_parsed"] = dt.datetime.fromisoformat(talk.pop("start_parsed"))
    talk["_start_end_parsed"] = dt.datetime.fromisoformat(talk.pop("start_end_parsed"))
    talk["_date_end_parsed"] = dt.datetime.fromisoformat(talk.pop("date_end_parsed"))
    return talk


class Fahrplan:
    def __init__(self, db_path: Path = None):
        self.flat_plans = []
        self.errors = []
        self._load_from_db(db_path or DB_PATH)

    def _load_from_db(self, db_path: Path):
        if not db_path.exists():
            self.errors.append(
                "No talks database found. Run 'python -m pyfahrplan.build_db' "
                "or the update-schedules workflow to build it."
            )
            return
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            rows = conn.execute(f"SELECT {', '.join(TALK_COLUMNS)} FROM talks").fetchall()
            conn.close()
            self.flat_plans = [_hydrate_talk(dict(row)) for row in rows]
        except sqlite3.Error as e:
            self.errors.append(f"Error reading talks database: {e}")

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
