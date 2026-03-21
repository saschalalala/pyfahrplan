import sys
from pathlib import Path

from textual.app import App
from textual.widgets import Static, LoadingIndicator

from pyfahrplan import __version__


class FahrplanApp(App):
    """CCC Fahrplan TUI — browse and filter conference schedules."""

    TITLE = "pyfahrplan"
    SUB_TITLE = f"CCC Schedule Browser v{__version__}"
    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self, update_cache: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self._update_cache = update_cache

    def compose(self):
        yield Static("Loading schedules...", id="loading-message")
        yield LoadingIndicator()

    def on_mount(self) -> None:
        """Load data in a worker thread so the UI stays responsive."""
        self.run_worker(self._load_data, thread=True)

    async def _load_data(self) -> None:
        from pyfahrplan.lib import Fahrplan
        fahrplan = Fahrplan(update_cache=self._update_cache)

        if fahrplan.errors and not fahrplan.flat_plans:
            self.call_from_thread(self._show_error, "\n".join(fahrplan.errors))
            return

        talks = fahrplan.flat_plans
        conferences = fahrplan.get_conference_acronyms()
        self.call_from_thread(self._show_main, talks, conferences)

    def _show_error(self, message: str) -> None:
        self.query_one("#loading-message", Static).update(
            f"[red]{message}[/red]\n\nPress q to quit."
        )
        try:
            self.query_one(LoadingIndicator).remove()
        except Exception:
            pass

    def _show_main(self, talks: list[dict], conferences: list[str]) -> None:
        from pyfahrplan.screens.main_screen import MainScreen
        self.push_screen(MainScreen(talks, conferences))

    def action_quit(self) -> None:
        self.exit()


def main():
    """Entry point for the pyfahrplan TUI."""
    update_cache = "--update-cache" in sys.argv
    app = FahrplanApp(update_cache=update_cache)
    app.run()


if __name__ == "__main__":
    main()
