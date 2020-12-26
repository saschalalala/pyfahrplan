from dateutil.parser import parse
import datetime as dt
from json.decoder import JSONDecodeError
import os
from pathlib import Path
import sys

import click
import requests
import requests_cache
from tabulate import tabulate, _table_formats

script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
cache_file = Path("fahrplan_cache")
requests_cache.install_cache(str(script_dir / cache_file))


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
    def __init__(self, column_width, update_cache):
        self.urls = [
            f"https://raw.githubusercontent.com/voc/{x}C3_schedule/master/everything.schedule.json"
            for x in range(32, 37)
        ]
        self.urls.append("https://fahrplan.events.ccc.de/rc3/2020/Fahrplan/schedule.json")
        self.fahrplans = []
        self.flat_plans = []
        self.column_width = column_width
        self.update_cache = update_cache
        self._get_fahrplans()
        self.flatten_fahrplans()

    def _get_fahrplans(self):
        if self.update_cache:
            requests_cache.clear()
        self.fahrplans = []
        for url in self.urls:
            try:
                self.fahrplans.append(requests.get(url).json()["schedule"])
            except JSONDecodeError as e:
                print(
                    f"{Colour.FAIL}Problem downloading the Fahrplan {url}. Check your internet connection.{Colour.ENDC}"  # noqa: E501
                )
                print(e)
        if not self.fahrplans:
            print(
                f"{Colour.FAIL}Fahrplan empty. Something is wrong with your urls. Exiting.{Colour.ENDC}"  # noqa: E501
            )
            sys.exit()

    def format_row(self, row_content):
        for key in row_content.keys():
            cell_value = row_content[key]
            if type(cell_value) == str and (value_length := len(cell_value)) >= self.column_width:
                row_content[key] = " \n".join(
                    # fmt: off
                    cell_value[n:n + self.column_width]
                    # fmt: on
                    for n in range(0, value_length, self.column_width)
                )

    def flatten_fahrplans(self):
        self.flat_plans = []
        for schedule in self.fahrplans:
            for day in schedule["conference"]["days"]:
                for room_name, room in day["rooms"].items():
                    for talk in room:
                        current_talk = {
                            "conference_title": schedule["conference"]["title"],
                            "conference_acronym": schedule["conference"]["acronym"],
                            "day": day["index"],
                            "room": room_name,
                            "title": talk["title"],
                            "talk_guid": talk.get("guid"),
                            "talk_id": talk["id"],
                            "talk_start": talk["start"],
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
                                    for person in talk["persons"]
                                ]
                            ),
                        }
                        self.format_row(current_talk)
                        # print(current_talk)
                        self.flat_plans.append(current_talk)


def is_speaker_in_talk(name: str, persons: list) -> bool:
    name = name.lower()
    persons = [x.lower() for x in persons]
    return any([person for person in persons if name in person])


def is_talk_in_timerange(talk: dict, start: str) -> bool:
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
    talk: dict,
    speaker: str,
    title: str,
    track: str,
    day: int,
    start: str,
    room: str,
    conference: str,
) -> bool:
    """
    Some simple filter rules (one rule per filter criteria)
    """
    speaker_matches = speaker is None or is_speaker_in_talk(speaker, talk["speakers"])
    title_matches = title is None or title.lower() in talk["title"].lower()
    track_matches = track is None or track.lower() in talk["track"].lower()
    day_matches = day == 0 or day == talk["day"]
    start_matches = start is None or is_talk_in_timerange(talk, start)
    room_matches = room == "all" or room.lower() in talk["room"].lower()
    conference_matches = conference == "all" or conference == talk["conference_acronym"]
    return (
        speaker_matches
        and title_matches
        and track_matches
        and day_matches
        and start_matches
        and room_matches
        and conference_matches
    )


def print_formatted_talks(
    talks: list,
    show_abstract: bool,
    show_description: bool,
    sort_by: str,
    reverse: bool,
    tablefmt: str,
) -> None:
    header = [
        "Conference",
        "Day",
        "Time",
        "Duration",
        "Room",
        "Title",
        "Speaker(s)",
        "Track",
    ]
    fields = [
        "conference_title",
        "day",
        "talk_start",
        "talk_duration",
        "room",
        "title",
        "speakers",
        "track",
    ]

    if show_abstract:
        header.append("Abstract")
    if show_description:
        header.append("Description")
    data = []

    for index, talk in enumerate(talks):
        current_data_point = [talk[field] for field in fields]
        if show_abstract:
            current_data_point.append(talk["talk_abstract"])
        if show_description:
            current_data_point.append(talk["talk_description"])
        # TODO think about coloring every second row (needs theming and config tho)
        data.append(current_data_point)
    try:
        if sort_by is not None:
            data.sort(key=lambda x: x[fields.index(sort_by)])
        if reverse:
            data.reverse()
        print(tabulate(data, headers=header, tablefmt=tablefmt))
    except ValueError:
        print("No talks in this period.")


@click.command()
@click.option("--speaker", "-s", default=None, help="Name of a speaker you want to search.")
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
@click.option("--day", "-d", default=0, help="Day you want to filter [1-4] or 0 for all days.")
@click.option("--start", "-st", default=None, help="Start time of the talk(s) you want to search.")
@click.option(
    "--room",
    "-r",
    default="all",
    help="Name of the room you want to filter [room names] or 'all' for all rooms",
)
@click.option(
    "--conference",
    "-c",
    default="rc3",
    help="CCC acronym (32c3 to 36c3 plus rc3) that you want to filter on, all for all conferences",
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
@click.option(
    "--sort",
    default=None,
    type=click.Choice(["day", "speakers", "title", "track", "room"]),
    help="Sort by day|speakers|title|track|room",
)
@click.option("--reverse", default=False, help="Reverse results", is_flag=True)
@click.option(
    "--tablefmt",
    default="fancy_grid",
    help="Choose a tableformat that is supported by python-tabular",
    type=click.Choice(_table_formats),
)
@click.option(
    "--column-width",
    default=60,
    help="Set the max width of the wide columns (which is everything string based)"
)
@click.option(
    "--update-cache",
    default=False,
    help="Delete the cache file and redownload all fahrplans",
    is_flag="True",
)
def cli(
    speaker,
    title,
    track,
    day,
    start,
    room,
    show_abstract,
    show_description,
    conference,
    sort,
    reverse,
    tablefmt,
    column_width,
    update_cache
):
    matching_talks = [
        x
        for x in Fahrplan(column_width=column_width, update_cache=update_cache).flat_plans
        if filter_talk(x, speaker, title, track, day, start, room, conference)
    ]
    print_formatted_talks(
        matching_talks,
        show_abstract,
        show_description,
        sort_by=sort,
        reverse=reverse,
        tablefmt=tablefmt,
    )


if __name__ == "__main__":
    cli()
