from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Select, Switch, Static, Label


class FilterBar(Widget):
    """Composite widget with all filter inputs for talks."""

    class Changed(Message):
        """Emitted when any filter value changes."""

        def __init__(self, filters: dict) -> None:
            self.filters = filters
            super().__init__()

    DEFAULT_CSS = """
    FilterBar {
        height: auto;
        padding: 0 1;
    }
    """

    def __init__(self, conferences: list[str] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._conferences = conferences or []

    def compose(self) -> ComposeResult:
        conf_options = [("All conferences", "all")] + [
            (c, c) for c in self._conferences
        ]
        day_options = [("All days", -1)] + [(f"Day {i}", i) for i in range(0, 5)]

        with Vertical(id="filter-container"):
            with Horizontal(classes="filter-row"):
                yield Label("Conference", classes="filter-label")
                yield Select(conf_options, value="all", id="filter-conference", allow_blank=False)
                yield Label("Day", classes="filter-label")
                yield Select(day_options, value=-1, id="filter-day", allow_blank=False)
            with Horizontal(classes="filter-row"):
                yield Label("Speaker", classes="filter-label")
                yield Input(placeholder="Filter speaker...", id="filter-speaker")
                yield Label("Title", classes="filter-label")
                yield Input(placeholder="Filter title...", id="filter-title")
            with Horizontal(classes="filter-row"):
                yield Label("Track", classes="filter-label")
                yield Input(placeholder="Filter track...", id="filter-track")
                yield Label("Room", classes="filter-label")
                yield Input(placeholder="Filter room...", id="filter-room")
            with Horizontal(classes="filter-row"):
                yield Label("Hide past", classes="filter-label")
                yield Switch(value=False, id="filter-past")

    def get_filters(self) -> dict:
        """Return current filter values as a dict suitable for filter_talk()."""
        conf = self.query_one("#filter-conference", Select).value
        day = self.query_one("#filter-day", Select).value
        speaker = self.query_one("#filter-speaker", Input).value.strip() or None
        title = self.query_one("#filter-title", Input).value.strip() or None
        track = self.query_one("#filter-track", Input).value.strip() or None
        room = self.query_one("#filter-room", Input).value.strip() or "all"
        filter_past = self.query_one("#filter-past", Switch).value

        return {
            "conference": conf if conf != Select.BLANK else "all",
            "day": day if day != Select.BLANK else -1,
            "speaker": speaker,
            "title": title,
            "track": track,
            "room": room,
            "filter_past": filter_past,
        }

    def on_input_changed(self, event: Input.Changed) -> None:
        self._emit_changed()

    def on_select_changed(self, event: Select.Changed) -> None:
        self._emit_changed()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        self._emit_changed()

    def _emit_changed(self) -> None:
        self.post_message(self.Changed(self.get_filters()))
