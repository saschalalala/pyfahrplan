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
    "camp2019.json": "https://data.c3voc.de/camp2019/everything.schedule.json",
    "camp2023.json": "https://data.c3voc.de/camp2023/everything.schedule.json",

    # DiVOC (Digital Verteiltes Online-Chaos)
    "divoc.json": "https://data.c3voc.de/divoc/everything.schedule.json",
    "divoc_r2r.json": "https://pretalx.c3voc.de/divoc-reboot-to-respawn-2021/schedule/export/schedule.json",
    "divoc_bb3.json": "https://pretalx.c3voc.de/divoc-bb3/schedule/export/schedule.json",

    # GPN (Gulaschprogrammiernacht)
    "gpn22.json": "https://cfp.gulas.ch/gpn22/schedule/export/schedule.json",
    "gpn23.json": "https://cfp.gulas.ch/gpn23/schedule/export/schedule.json",

    # MRMCD (MetaRheinMainChaosDays)
    "mrmcd2023.json": "https://talks.mrmcd.net/2023/schedule/export/schedule.json",
    "mrmcd2024.json": "https://talks.mrmcd.net/2024/schedule/export/schedule.json",
    "mrmcd2025.json": "https://talks.mrmcd.net/2025/schedule/export/schedule.json",

    # Easterhegg
    "eh20.json": "https://cfp.eh20.easterhegg.eu/eh20/schedule/export/schedule.json",
    "eh21.json": "https://fahrplan.eh21.easterhegg.eu/eh/schedule/export/schedule.json",
    "eh22.json": "https://cfp.eh22.easterhegg.eu/eh22/schedule/export/schedule.json",

    # Datenspuren
    "ds2024.json": "https://talks.datenspuren.de/ds24/schedule/export/schedule.json",
    "ds2025.json": "https://talks.datenspuren.de/ds25/schedule/export/schedule.json",

    # FrOSCon
    "froscon2022.json": "https://programm.froscon.org/2022/schedule.json",
    "froscon2023.json": "https://programm.froscon.org/2023/schedule.json",
    "froscon2024.json": "https://programm.froscon.org/2024/schedule.json",
}
