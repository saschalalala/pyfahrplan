"""Tests for the MainScreen."""

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from pyfahrplan.screens.main_screen import MainScreen
from pyfahrplan.widgets.talk_table import TalkTable
from tests.data.test_data import test_flat_talks


CONFERENCES = ["32c3", "33c3", "34c3", "35c3", "36c3"]


class MainScreenApp(App):
    """Minimal app that pushes MainScreen for testing."""

    CSS_PATH = None

    def __init__(self, talks=None, conferences=None, **kwargs):
        super().__init__(**kwargs)
        self._talks = talks or test_flat_talks
        self._conferences = conferences or CONFERENCES

    def on_mount(self) -> None:
        self.push_screen(MainScreen(self._talks, self._conferences))


@pytest.mark.asyncio
async def test_displays_all_talks():
    app = MainScreenApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        table = app.screen.query_one(TalkTable)
        assert table.talk_count == len(test_flat_talks)


@pytest.mark.asyncio
async def test_status_bar_shows_count():
    app = MainScreenApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        status = app.screen.query_one("#status-bar", Static)
        assert "5 talks" in str(status.content)


@pytest.mark.asyncio
async def test_clear_filters_with_escape():
    app = MainScreenApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen
        speaker_input = screen.query_one("#filter-speaker")
        speaker_input.value = "Carina"
        await pilot.pause()

        # Press escape to clear
        await pilot.press("escape")
        await pilot.pause()

        table = screen.query_one(TalkTable)
        assert table.talk_count == len(test_flat_talks)
        assert speaker_input.value == ""


@pytest.mark.asyncio
async def test_talk_selection_opens_detail():
    app = MainScreenApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        table_widget = app.screen.query_one("#talks-table")
        table_widget.focus()
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        from pyfahrplan.screens.detail_screen import DetailScreen
        assert any(isinstance(s, DetailScreen) for s in app.screen_stack)
