# pyfahrplan

CLI application for several CCC fahrplan files

## Usage

```
Usage: pyfahrplan.py [OPTIONS]

Options:
  -s, --speaker TEXT              Name of a speaker you want to search.
  -t, --title TEXT                A part of the title of the talk(s) you want
                                  to search.
  -tr, --track TEXT               A part of the track description you want to
                                  search.
  -d, --day INTEGER               Day you want to filter [1-4] or 0 for all
                                  days.
  -st, --start TEXT               Start time of the talk(s) you want to
                                  search.
  -r, --room TEXT                 Name of the room you want to filter [room
                                  names] or 'all' for all rooms
  -c, --conference TEXT           CCC acronym (32c3 to 36c3 plus rc3) that you
                                  want to filter on, all for all conferences
  --show-abstract                 Shows abstracts, default False, experimental
  --show-description              Shows descriptions, default False,
                                  experimental
  --sort [day|speakers|title|track|room]
                                  Sort by day|speakers|title|track|room
  --reverse                       Reverse results
  --tablefmt [simple|plain|grid|fancy_grid|github|pipe|orgtbl|jira|presto|pretty|psql|rst|mediawiki|moinmoin|youtrack|html|latex|latex_raw|latex_booktabs|tsv|textile]
                                  Choose a tableformat that is supported by
                                  python-tabular
  --column-width INTEGER          Set the max width of the wide columns (which is everything string based)
  --update-cache                  Delete the cache file and redownload all fahrplans
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
