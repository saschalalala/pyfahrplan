from dateutil.parser import parse
import datetime as dt
from json.decoder import JSONDecodeError
import sys

import click
import requests
import termtables as tt


class Colour:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Fahrplan:
    def __init__(self):
        self.urls = [
            "https://fahrplan.events.ccc.de/congress/2019/Fahrplan/schedule.json",
            "https://fahrplan.chaos-west.de/36c3/schedule/export/schedule.json",
        ]
        self.fahrplan = []
        self.flat_plan = []
        self._get_fahrplan()
        self.flatten_fahrplan()

    def _get_fahrplan(self):
        try:
            self.fahrplan = []
            for url in self.urls:
                self.fahrplan.extend(
                    requests.get(url).json()["schedule"]["conference"]["days"]
                )
        except JSONDecodeError as e:
            print(
                f"{Colour.FAIL}Problem downloading the Fahrplan. Check your internet connection.{Colour.ENDC}"
            )
            print(e)
            sys.exit()

    def flatten_fahrplan(self):
        self.flat_plan = []
        for day in self.fahrplan:
            for room_name, room in day["rooms"].items():
                for talk in room:
                    self.flat_plan.append(
                        {
                            "day": day["index"],
                            "room_name": room_name,
                            "talk_title": talk["title"],
                            "talk_guid": talk["guid"],
                            "talk_id": talk["id"],
                            "talk_start": talk["start"],
                            "talk_duration": talk["duration"],
                            "talk_description": ""
                            if talk["description"] is None
                            else talk["description"][:50],
                            "talk_abstract": ""
                            if talk["abstract"] is None
                            else talk["abstract"][:50],
                            "track": "" if talk["track"] is None else talk["track"],
                            "persons": [
                                person["public_name"] for person in talk["persons"]
                            ],
                        }
                    )


def speaker_in_talk(name: str, persons: list) -> bool:
    name = name.lower()
    persons = [x.lower() for x in persons]
    return any([person for person in persons if name in person])


def talk_in_timerange(talk: dict, start: str) -> bool:
    start_time = parse(start)
    talk_start = parse(talk["talk_start"])
    duration = parse(talk["talk_duration"])
    talk_end = talk_start + dt.timedelta(hours=duration.hour, minutes=duration.minute)
    current_hour_end = start_time.replace(minute=59)
    current_hour_begin = start_time.replace(minute=0)
    talk_in_timerange = talk_start <= start_time <= talk_end
    talk_starts_in_current_hour = current_hour_begin <= talk_start <= current_hour_end
    return talk_in_timerange or talk_starts_in_current_hour


def filter_talk(
    talk: dict, speaker: str, title: str, track: str, day: int, start: str, room: str
) -> bool:
    """
    Some simple filter rules (one rule per filter criteria)
    """
    speaker_matches = speaker is None or speaker_in_talk(speaker, talk["persons"])
    title_matches = title is None or title.lower() in talk["talk_title"].lower()
    track_matches = track is None or track.lower() in talk["track"].lower()
    day_matches = day == 0 or day == talk["day"]
    start_matches = start is None or talk_in_timerange(talk, start)
    room_matches = room == "all" or room.lower() in talk["room_name"].lower()
    return (
        speaker_matches
        and title_matches
        and track_matches
        and day_matches
        and start_matches
        and room_matches
    )


def print_formatted_talks(
    talks: list, show_abstract: bool, show_description: bool
) -> None:
    header = ["Day", "Time", "Duration", "Room", "Title", "Speaker(s)", "Track"]
    if show_abstract:
        header.append("Abstract")
    if show_description:
        header.append("Description")
    data = []
    for index, talk in enumerate(talks):
        current_data_point = [
            talk["day"],
            talk["talk_start"],
            talk["talk_duration"],
            talk["room_name"],
            talk["talk_title"],
            ", ".join(talk["persons"]),
            talk["track"],
        ]
        if show_abstract:
            current_data_point.append(talk["talk_abstract"])
        if show_description:
            current_data_point.append(talk["talk_description"])
        # TODO think about coloring every second row (needs theming and config tho)
        data.append(current_data_point)
    print(tt.to_string(data, header=header))


@click.command()
@click.option(
    "--speaker", "-s", default=None, help="Name of a speaker you want to search."
)
@click.option(
    "--title",
    "-t",
    default=None,
    help="A part of the title of the talk(s) you want to search.",
)
@click.option(
    "--track",
    "-tr",
    default=None,
    help="A part of the track description you want to search.",
)
@click.option(
    "--day", "-d", default=0, help="Day you want to filter [1-4] or 0 for all days."
)
@click.option(
    "--start", "-st", default=None, help="Start time of the talk(s) you want to search."
)
@click.option(
    "--room",
    "-r",
    default="all",
    help="Name of the room you want to filter [room names] or 'all' for all rooms",
)
@click.option(
    "--show-abstract",
    default=False,
    help="Shows abstracts, default False, experimental",
    is_flag=True,
)
@click.option(
    "--show-description",
    default=False,
    help="Shows descriptions, default False, experimental",
    is_flag=True,
)
def cli(speaker, title, track, day, start, room, show_abstract, show_description):
    matching_talks = [
        x
        for x in Fahrplan().flat_plan
        if filter_talk(x, speaker, title, track, day, start, room)
    ]
    print_formatted_talks(matching_talks, show_abstract, show_description)


if __name__ == "__main__":
    cli()
