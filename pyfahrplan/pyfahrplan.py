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
    def __init__(self, update_cache):
        self.urls = [
            f"https://raw.githubusercontent.com/voc/{x}C3_schedule/master/everything.schedule.json"
            for x in range(32, 37)
        ]
        self.urls.append("https://data.c3voc.de/rC3/everything.schedule.json")
        self.fahrplans = []
        self.flat_plans = []
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
                        }
                        self.flat_plans.append(current_talk)


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


def is_talk_in_past(talk: dict, now: dt.datetime) -> bool:
    talk_start_datetime = parse(talk["talk_date"])
    duration = parse(talk["talk_duration"])
    end = talk_start_datetime + dt.timedelta(hours=duration.hour, minutes=duration.minute)
    return now > end


def format_row(row, column_width):
    def format_cell(cell, column_width):
        if type(cell) == str and (value_length := len(cell)) >= column_width:
            cell = " \n".join(
                # fmt: off
                cell[n:n + column_width]
                # fmt: on
                for n in range(0, value_length, column_width)
            )
        return cell
    return [format_cell(cell, column_width) for cell in row]


def filter_talk(
    talk: dict,
    speaker: str,
    title: str,
    track: str,
    day: int,
    start: str,
    room: str,
    conference: str,
    filter_past: bool,
    now: dt.datetime,
) -> bool:
    """
    Some simple filter rules as functions
    """

    def speaker_matches():
        return speaker is None or speaker.lower() in talk["speakers"].lower()

    def title_matches():
        return title is None or title.lower() in talk["title"].lower()

    def track_matches():
        return track is None or track.lower() in talk["track"].lower()

    def day_matches():
        return day == 0 or day == talk["day"]

    def start_matches():
        return start is None or is_talk_in_timerange(talk, start)

    def room_matches():
        return room == "all" or room.lower() in talk["room"].lower()

    def conference_matches():
        return conference == "all" or conference == talk["conference_acronym"]

    def filtered_as_past():
        return filter_past and is_talk_in_past(talk, now)

    return (
        speaker_matches()
        and title_matches()
        and track_matches()
        and day_matches()
        and start_matches()
        and room_matches()
        and conference_matches()
        and not filtered_as_past()
    )


def print_formatted_talks(
    talks: list,
    show_abstract: bool,
    show_description: bool,
    sort_by: str,
    reverse: bool,
    tablefmt: str,
    column_width: int
) -> None:
    header = [
        "Conference",
        "Day",
        "Talk Start",
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

    for talk in talks:
        current_data_point = [talk.get(field, "") for field in fields]
        if show_abstract:
            current_data_point.append(talk["talk_abstract"])
        if show_description:
            current_data_point.append(talk["talk_description"])
        # TODO think about coloring every second row (needs theming and config tho)
        data.append(format_row(current_data_point, column_width))
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
    type=click.Choice(["day", "speakers", "title", "track", "room", "talk_start"]),
    help="Sort by day|speakers|title|track|room|talk_start",
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
    help="Set the max width of the wide columns (which is everything string based)",
)
@click.option(
    "--update-cache",
    default=False,
    help="Delete the cache file and redownload all fahrplans",
    is_flag=True,
)
@click.option(
    "--no-past", default=False, help="Filter out talks that lay in the past", is_flag=True
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
    update_cache,
    no_past,
):
    now = dt.datetime.now().astimezone()
    matching_talks = [
        x
        for x in Fahrplan(update_cache=update_cache).flat_plans
        if filter_talk(x, speaker, title, track, day, start, room, conference, no_past, now)
    ]
    print_formatted_talks(
        matching_talks,
        show_abstract,
        show_description,
        sort_by=sort,
        reverse=reverse,
        tablefmt=tablefmt,
        column_width=column_width
    )


if __name__ == "__main__":
    cli()
