"""
Conference schedule sources.

Each entry maps a local filename to its remote URL.
Both lib.py and the GitHub Actions download workflow use this as the
single source of truth.
"""

SCHEDULE_SOURCES = {
    # Chaos Communication Congress (via voc GitHub repos)
    "32c3.json": "https://raw.githubusercontent.com/voc/32C3_schedule/master/everything.schedule.json",
    "33c3.json": "https://raw.githubusercontent.com/voc/33C3_schedule/master/everything.schedule.json",
    "34c3.json": "https://raw.githubusercontent.com/voc/34C3_schedule/master/everything.schedule.json",
    "35c3.json": "https://raw.githubusercontent.com/voc/35C3_schedule/master/everything.schedule.json",
    "36c3.json": "https://raw.githubusercontent.com/voc/36C3_schedule/master/everything.schedule.json",

    # Chaos Communication Congress (via fahrplan.events.ccc.de)
    "37c3.json": "https://fahrplan.events.ccc.de/congress/2023/fahrplan/schedule.json",
    "38c3.json": "https://fahrplan.events.ccc.de/congress/2024/fahrplan/schedule.json",
    "39c3.json": "https://fahrplan.events.ccc.de/congress/2025/fahrplan/schedule.json",

    # Remote Chaos Experience
    "rc3.json": "https://data.c3voc.de/rC3/everything.schedule.json",
    "rc3_21.json": "https://data.c3voc.de/rC3_21/everything.schedule.json",

    # Chaos Communication Camp
    "camp2023.json": "https://data.c3voc.de/camp2023/everything.schedule.json",

    # GPN (Gulaschprogrammiernacht)
    "gpn22.json": "https://cfp.gulas.ch/gpn22/schedule/export/schedule.json",

    # MRMCD (MetaRheinMainChaosDays)
    "mrmcd2024.json": "https://cfp.mrmcd.net/2024/schedule/export/schedule.json",

    # Easterhegg
    "eh21.json": "https://cfp.easterhegg.eu/eh21/schedule/export/schedule.json",

    # Datenspuren
    "ds2024.json": "https://cfp.datenspuren.de/ds2024/schedule/export/schedule.json",

    # FrOSCon
    "froscon2024.json": "https://programm.froscon.org/2024/schedule.json",
    "froscon2023.json": "https://programm.froscon.org/2023/schedule.json",
    "froscon2022.json": "https://programm.froscon.org/2022/schedule.json",
}
