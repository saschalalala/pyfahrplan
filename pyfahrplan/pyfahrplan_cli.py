import datetime as dt

import click

from pyfahrplan.config import config_defaults as cli_defaults
from pyfahrplan.lib import Fahrplan, filter_talk, print_formatted_talks

@click.command()
@click.option(
    "--conference",
    "-c",
    default="rc3-2021",
    help="CCC acronym (32c3 to 36c3 plus rc3 and rc3-2021) that you want to filter on, 'all' for all conferences",
)
@click.option(
    "--day",
    "-d",
    default=cli_defaults["day"],
    help="Day you want to filter [1-4] or 0 for all days.",
)
@click.option(
    "--room",
    "-r",
    default=cli_defaults["room"],
    help="Name of the room you want to filter [room names] or 'all' for all rooms",
)
@click.option("--speaker", "-s", default=None, help="Name of a speaker you want to search.")
@click.option(
    "--start",
    "-st",
    default=cli_defaults["start"],
    type=click.DateTime(formats=["%H:%M"]),
    help="Start time of the talk(s) you want to search.",
)
@click.option(
    "--title",
    "-t",
    default=cli_defaults["title"],
    help="A part of the title of the talk(s) you want to search.",
)
@click.option(
    "--track",
    "-tr",
    default=cli_defaults["track"],
    help="A part of the track description you want to search.",
)
@click.option("--reverse", default=False, help="Reverse results", is_flag=True)
@click.option(
    "--show-abstract",
    default=cli_defaults["show_abstract"],
    help="Shows abstracts, default False, experimental",
    is_flag=True,
)
@click.option(
    "--show-description",
    default=cli_defaults["show_description"],
    help="Shows descriptions, default False, experimental",
    is_flag=True,
)
@click.option(
    "--sort",
    default=cli_defaults["sort"],
    type=click.Choice(["day", "speakers", "title", "track", "room", "talk_start"]),
    help="Sort by day|speakers|title|track|room|talk_start",
)
@click.option(
    "--update-cache",
    default=cli_defaults["update_cache"],
    help="Delete the cache file and redownload all fahrplans",
    is_flag=True,
)
@click.option(
    "--no-past",
    default=cli_defaults["no_past"],
    help="Filter out talks that lay in the past",
    is_flag=True,
)
def cli(
    speaker,
    title,
    track,
    day,
    start: dt.datetime,
    room,
    show_abstract,
    show_description,
    conference,
    sort,
    reverse,
    update_cache,
    no_past,
):
    now = dt.datetime.now().astimezone()
    start = None if start is None else f"{start.hour}:{start.minute}"
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
    )


if __name__ == "__main__":
    cli()
