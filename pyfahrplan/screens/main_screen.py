from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static

from pyfahrplan.lib import filter_talks
from pyfahrplan.widgets.filter_bar import FilterBar
from pyfahrplan.widgets.talk_table import TalkTable


class MainScreen(Screen):
    """Main screen with filter bar and talk table."""

    BINDINGS = [
        ("slash", "focus_filter", "Filter"),
        ("escape", "clear_filters", "Clear filters"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, talks: list[dict], conferences: list[str], **kwargs) -> None:
        super().__init__(**kwargs)
        self._all_talks = talks
        self._conferences = conferences

    def compose(self) -> ComposeResult:
        yield Header()
        yield FilterBar(conferences=self._conferences, id="filter-bar")
        yield Static("", id="status-bar")
        yield TalkTable(id="talk-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(TalkTable)
        table.update_talks(self._all_talks)
        self._update_status(len(self._all_talks))

    def on_filter_bar_changed(self, event: FilterBar.Changed) -> None:
        """Re-filter talks when any filter changes."""
        filtered = filter_talks(self._all_talks, **event.filters)
        table = self.query_one(TalkTable)
        table.update_talks(filtered)
        self._update_status(len(filtered))

    def on_talk_table_talk_selected(self, event: TalkTable.TalkSelected) -> None:
        """Open detail screen for the selected talk."""
        from pyfahrplan.screens.detail_screen import DetailScreen
        self.app.push_screen(DetailScreen(event.talk))

    def action_focus_filter(self) -> None:
        """Focus the first filter input."""
        try:
            self.query_one("#filter-speaker").focus()
        except Exception:
            pass

    def action_clear_filters(self) -> None:
        """Reset all filters and show all talks."""
        from textual.widgets import Input, Select, Switch
        for inp in self.query(Input):
            inp.value = ""
        for sel in self.query(Select):
            # Reset to first option
            if sel.id == "filter-conference":
                sel.value = "all"
            elif sel.id == "filter-day":
                sel.value = -1
        for sw in self.query(Switch):
            sw.value = False
        table = self.query_one(TalkTable)
        table.update_talks(self._all_talks)
        self._update_status(len(self._all_talks))

    def action_quit(self) -> None:
        self.app.exit()

    def _update_status(self, count: int) -> None:
        status = self.query_one("#status-bar", Static)
        status.update(f" {count} talks")
