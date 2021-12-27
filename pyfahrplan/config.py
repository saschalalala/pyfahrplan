config_defaults = {
    "speaker": None,
    "title": None,
    "track": None,
    "day": -1,  # 0 seems to be a valid day value in some c3s
    "start": None,
    "room": "all",
    "conference": "all",
    "show_abstract": False,
    "show_description": False,
    "sort": None,
    "tablefmt": "fancy_grid",
    "update_cache": False,
    "no_past": False
}


class Colour:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
