"""Tests for the DetailScreen."""

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from pyfahrplan.screens.detail_screen import DetailScreen
from tests.data.test_data import test_flat_talks


class DetailApp(App):
    """Minimal app that pushes DetailScreen for testing."""

    CSS_PATH = None

    def __init__(self, talk, **kwargs):
        super().__init__(**kwargs)
        self._talk = talk

    def on_mount(self) -> None:
        self.push_screen(DetailScreen(self._talk))


@pytest.mark.asyncio
async def test_renders_title():
    talk = test_flat_talks[0]
    app = DetailApp(talk)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen
        content = screen.query_one("#detail-content", Static).content
        assert "Opening Event" in str(content)


@pytest.mark.asyncio
async def test_renders_all_metadata():
    talk = test_flat_talks[0]
    app = DetailApp(talk)
    async with app.run_test() as pilot:
        await pilot.pause()
        content = str(app.screen.query_one("#detail-content", Static).content)
        assert "32c3" in content
        assert "Hall 1" in content
        assert "11:00" in content
        assert "00:30" in content
        assert "Carina Haupt" in content


@pytest.mark.asyncio
async def test_renders_abstract_when_present():
    talk = test_flat_talks[1]  # 33c3 talk has abstract
    app = DetailApp(talk)
    async with app.run_test() as pilot:
        await pilot.pause()
        content = str(app.screen.query_one("#detail-content", Static).content)
        assert "Abstract" in content


@pytest.mark.asyncio
async def test_renders_description_when_present():
    talk = test_flat_talks[1]  # 33c3 talk has description
    app = DetailApp(talk)
    async with app.run_test() as pilot:
        await pilot.pause()
        content = str(app.screen.query_one("#detail-content", Static).content)
        assert "Description" in content


@pytest.mark.asyncio
async def test_omits_abstract_when_empty():
    talk = test_flat_talks[0]  # empty abstract
    app = DetailApp(talk)
    async with app.run_test() as pilot:
        await pilot.pause()
        content = str(app.screen.query_one("#detail-content", Static).content)
        assert "Abstract" not in content


@pytest.mark.asyncio
async def test_go_back_with_escape():
    talk = test_flat_talks[0]
    app = DetailApp(talk)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert len(app.screen_stack) == 2  # default + detail
        await pilot.press("escape")
        await pilot.pause()
        assert len(app.screen_stack) == 1


@pytest.mark.asyncio
async def test_go_back_with_b():
    talk = test_flat_talks[0]
    app = DetailApp(talk)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert len(app.screen_stack) == 2
        await pilot.press("b")
        await pilot.pause()
        assert len(app.screen_stack) == 1


@pytest.mark.asyncio
async def test_missing_fields_use_defaults():
    talk = {}  # empty dict
    app = DetailApp(talk)
    async with app.run_test() as pilot:
        await pilot.pause()
        content = str(app.screen.query_one("#detail-content", Static).content)
        assert "Untitled" in content
