from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Markdown


class DetailScreen(Screen):
    """Full-screen detail view for a single talk."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("b", "go_back", "Back"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, talk: dict, **kwargs) -> None:
        super().__init__(**kwargs)
        self._talk = talk

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="detail-scroll"):
            yield Static(id="detail-content")
        yield Footer()

    def on_mount(self) -> None:
        t = self._talk
        content = self.query_one("#detail-content", Static)

        parts = [
            f"[bold]{t.get('title', 'Untitled')}[/bold]",
            "",
            f"[dim]Conference:[/dim]  {t.get('conference_title', '')} ({t.get('conference_acronym', '')})",
            f"[dim]Day:[/dim]         {t.get('day', '')}",
            f"[dim]Start:[/dim]       {t.get('talk_start', '')}",
            f"[dim]Duration:[/dim]    {t.get('talk_duration', '')}",
            f"[dim]Room:[/dim]        {t.get('room', '')}",
            f"[dim]Track:[/dim]       {t.get('track', '')}",
            f"[dim]Speaker(s):[/dim]  {t.get('speakers', '')}",
        ]

        abstract = t.get("talk_abstract", "").strip()
        if abstract:
            parts += ["", "[bold]Abstract[/bold]", "", abstract]

        description = t.get("talk_description", "").strip()
        if description:
            parts += ["", "[bold]Description[/bold]", "", description]

        content.update("\n".join(parts))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_quit(self) -> None:
        self.app.exit()
