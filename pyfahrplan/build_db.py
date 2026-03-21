"""
Build the talks SQLite database from raw schedule JSON files.

This script is run by the GitHub Actions workflow after downloading
and validating schedule JSONs. It flattens all schedules into a single
talks table for fast loading at runtime.

Usage:
    python -m pyfahrplan.build_db [--data-dir DIR] [--db-path PATH]
"""

import argparse
import json
import sqlite3
from pathlib import Path

import datetime as dt

from dateutil.parser import parse as dateutil_parse

from pyfahrplan.schedules import SCHEDULE_SOURCES

DEFAULT_DATA_DIR = Path(__file__).parent / "data"
DEFAULT_DB_PATH = Path(__file__).parent / "data" / "talks.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS talks (
    conference_title TEXT NOT NULL,
    conference_acronym TEXT NOT NULL,
    day INTEGER NOT NULL,
    room TEXT NOT NULL,
    title TEXT NOT NULL,
    talk_guid TEXT,
    talk_id INTEGER NOT NULL,
    talk_start TEXT NOT NULL,
    talk_date TEXT NOT NULL,
    talk_duration TEXT NOT NULL,
    talk_description TEXT NOT NULL DEFAULT '',
    talk_abstract TEXT NOT NULL DEFAULT '',
    track TEXT NOT NULL DEFAULT '',
    speakers TEXT NOT NULL DEFAULT '',
    start_parsed TEXT NOT NULL,
    start_end_parsed TEXT NOT NULL,
    date_end_parsed TEXT NOT NULL
);
"""


def _parse_duration(duration_str: str) -> dt.timedelta:
    parts = duration_str.split(":")
    return dt.timedelta(hours=int(parts[0]), minutes=int(parts[1]) if len(parts) > 1 else 0)


def flatten_schedule(schedule: dict) -> list[dict]:
    """Flatten a single schedule JSON into a list of talk dicts."""
    talks = []
    for day in schedule["conference"]["days"]:
        for room_name, room in day["rooms"].items():
            for talk in room:
                start_parsed = dateutil_parse(talk["start"])
                duration_td = _parse_duration(talk["duration"])
                date_parsed = dateutil_parse(talk["date"])
                talks.append({
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
                    "talk_description": talk.get("description") or "",
                    "talk_abstract": talk.get("abstract") or "",
                    "track": talk.get("track") or "",
                    "speakers": ", ".join(
                        person.get("public_name", person.get("full_public_name", ""))
                        for person in talk.get("persons", [])
                    ),
                    "start_parsed": start_parsed.isoformat(),
                    "start_end_parsed": (start_parsed + duration_td).isoformat(),
                    "date_end_parsed": (date_parsed + duration_td).isoformat(),
                })
    return talks


def build_db(data_dir: Path = DEFAULT_DATA_DIR, db_path: Path = DEFAULT_DB_PATH) -> int:
    """Build the SQLite database from JSON files. Returns talk count."""
    all_talks = []
    for filename in SCHEDULE_SOURCES:
        path = data_dir / filename
        if not path.exists():
            print(f"  Skipping {filename} (not found)")
            continue
        try:
            with open(path) as f:
                schedule = json.load(f)["schedule"]
            talks = flatten_schedule(schedule)
            all_talks.extend(talks)
            print(f"  {filename}: {len(talks)} talks")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Skipping {filename}: {e}")

    conn = sqlite3.connect(str(db_path))
    conn.execute("DROP TABLE IF EXISTS talks")
    conn.execute(SCHEMA)

    columns = [
        "conference_title", "conference_acronym", "day", "room", "title",
        "talk_guid", "talk_id", "talk_start", "talk_date", "talk_duration",
        "talk_description", "talk_abstract", "track", "speakers",
        "start_parsed", "start_end_parsed", "date_end_parsed",
    ]
    placeholders = ", ".join("?" for _ in columns)
    conn.executemany(
        f"INSERT INTO talks ({', '.join(columns)}) VALUES ({placeholders})",
        [tuple(talk[c] for c in columns) for talk in all_talks],
    )
    conn.commit()
    conn.close()

    print(f"Built {db_path}: {len(all_talks)} talks total")
    return len(all_talks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build talks database")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()
    build_db(args.data_dir, args.db_path)
