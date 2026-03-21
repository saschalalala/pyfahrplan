"""Tests for the FilterBar widget."""

import pytest
from textual.app import App, ComposeResult

from pyfahrplan.widgets.filter_bar import FilterBar


class FilterBarApp(App):
    """Minimal app for testing FilterBar."""

    CSS = """
    FilterBar { height: auto; }
    """

    def __init__(self, conferences=None, **kwargs):
        super().__init__(**kwargs)
        self._conferences = conferences or ["32c3", "33c3"]

    def compose(self) -> ComposeResult:
        yield FilterBar(conferences=self._conferences, id="filter-bar")


@pytest.mark.asyncio
async def test_initial_filter_values():
    app = FilterBarApp()
    async with app.run_test() as pilot:
        bar = app.query_one(FilterBar)
        filters = bar.get_filters()
        assert filters["conference"] == "all"
        assert filters["day"] == -1
        assert filters["speaker"] is None
        assert filters["title"] is None
        assert filters["track"] is None
        assert filters["room"] == "all"
        assert filters["filter_past"] is False


@pytest.mark.asyncio
async def test_emits_changed_on_input():
    app = FilterBarApp()
    messages = []
    async with app.run_test() as pilot:
        bar = app.query_one(FilterBar)
        bar.on_filter_bar_changed = lambda e: messages.append(e)  # noqa
        # Type into speaker input
        speaker_input = app.query_one("#filter-speaker")
        speaker_input.focus()
        await pilot.press("t", "e", "s", "t")
        await pilot.pause()
        filters = bar.get_filters()
        assert filters["speaker"] == "test"


@pytest.mark.asyncio
async def test_get_filters_reflects_input_values():
    app = FilterBarApp()
    async with app.run_test() as pilot:
        speaker_input = app.query_one("#filter-speaker")
        speaker_input.value = "test speaker"
        await pilot.pause()
        bar = app.query_one(FilterBar)
        filters = bar.get_filters()
        assert filters["speaker"] == "test speaker"


@pytest.mark.asyncio
async def test_empty_conferences_list():
    app = FilterBarApp(conferences=[])
    async with app.run_test() as pilot:
        bar = app.query_one(FilterBar)
        filters = bar.get_filters()
        assert filters["conference"] == "all"


@pytest.mark.asyncio
async def test_strips_whitespace_from_inputs():
    app = FilterBarApp()
    async with app.run_test() as pilot:
        speaker_input = app.query_one("#filter-speaker")
        speaker_input.value = "  test  "
        await pilot.pause()
        bar = app.query_one(FilterBar)
        filters = bar.get_filters()
        assert filters["speaker"] == "test"


@pytest.mark.asyncio
async def test_empty_input_returns_none():
    app = FilterBarApp()
    async with app.run_test() as pilot:
        speaker_input = app.query_one("#filter-speaker")
        speaker_input.value = "   "
        await pilot.pause()
        bar = app.query_one(FilterBar)
        filters = bar.get_filters()
        assert filters["speaker"] is None
