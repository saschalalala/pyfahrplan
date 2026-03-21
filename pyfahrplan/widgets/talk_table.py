from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable


COLUMNS = [
    ("Conference", "conference_acronym"),
    ("Day", "day"),
    ("Start", "talk_start"),
    ("Duration", "talk_duration"),
    ("Room", "room"),
    ("Title", "title"),
    ("Speaker(s)", "speakers"),
    ("Track", "track"),
]


class TalkTable(Widget):
    """DataTable wrapper for displaying talks."""

    class TalkSelected(Message):
        """Emitted when a talk row is selected."""

        def __init__(self, talk: dict) -> None:
            self.talk = talk
            super().__init__()

    DEFAULT_CSS = """
    TalkTable {
        height: 1fr;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._talks: list[dict] = []
        self._sort_key: str | None = None
        self._sort_reverse: bool = False

    def compose(self) -> ComposeResult:
        yield DataTable(id="talks-table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        for label, _ in COLUMNS:
            table.add_column(label, key=label)

    def update_talks(self, talks: list[dict]) -> None:
        """Replace the table contents with a new list of talks."""
        self._talks = talks
        table = self.query_one(DataTable)
        table.clear()
        for talk in talks:
            row = [str(talk.get(field, "")) for _, field in COLUMNS]
            table.add_row(*row, key=talk.get("talk_guid", str(talk.get("talk_id", ""))))

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Sort by clicked column header."""
        col_label = str(event.label)
        # Find the field key for this column
        field = None
        for label, f in COLUMNS:
            if label == col_label:
                field = f
                break
        if field is None:
            return

        if self._sort_key == field:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_key = field
            self._sort_reverse = False

        sorted_talks = sorted(
            self._talks,
            key=lambda t: str(t.get(field, "")),
            reverse=self._sort_reverse,
        )
        self.update_talks(sorted_talks)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Emit TalkSelected when a row is activated."""
        row_key = str(event.row_key.value)
        for talk in self._talks:
            guid = talk.get("talk_guid", str(talk.get("talk_id", "")))
            if guid == row_key:
                self.post_message(self.TalkSelected(talk))
                break

    @property
    def talk_count(self) -> int:
        return len(self._talks)
