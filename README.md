# pyfahrplan

CLI application for CCC several fahrplan files (schedule.json), currently based on:

 - https://raw.githubusercontent.com/voc/{32-36}C3_schedule/master/everything.schedule.json
 - https://data.c3voc.de/rC3/everything.schedule.json
 - https://data.c3voc.de/rC3_21/everything.schedule.json

## Usage

```
Usage: pyfahrplan.py [OPTIONS]

Options:
  -c, --conference TEXT           CCC acronym (32c3 to 36c3 plus rc3 and
                                  rc3-2021) that you want to filter on, 'all'
                                  for all conferences

  -d, --day INTEGER               Day you want to filter [1-4] or 0 for all
                                  days.

  -r, --room TEXT                 Name of the room you want to filter [room
                                  names] or 'all' for all rooms

  -s, --speaker TEXT              Name of a speaker you want to search.
  -st, --start TEXT               Start time of the talk(s) you want to
                                  search.

  -t, --title TEXT                A part of the title of the talk(s) you want
                                  to search.

  -tr, --track TEXT               A part of the track description you want to
                                  search.

  --reverse                       Reverse results
  --show-abstract                 Shows abstracts, default False, experimental
  --show-description              Shows descriptions, default False,
                                  experimental

  --sort [day|speakers|title|track|room|talk_start]
                                  Sort by
                                  day|speakers|title|track|room|talk_start

  --update-cache                  Delete the cache file and redownload all
                                  fahrplans

  --no-past                       Filter out talks that lay in the past
  --help                          Show this message and exit.
```

## Development

Clone this repository, then create a virtualenv, e.g., inside the repository:

```bash
python3 -m venv .venv
pip install poetry  # if you don't have it globally installed
poetry install  # install all dependencies, including dev dependencies
poe test  # to run the tests
pytest --cov=pyfahrplan tests/ && coverage html  # to create a coverage report
```
