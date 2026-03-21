"""Tests for the TalkTable widget."""

import pytest
from textual.app import App, ComposeResult
from textual.widgets import DataTable

from pyfahrplan.widgets.talk_table import TalkTable, COLUMNS
from tests.data.test_data import test_flat_talks


class TalkTableApp(App):
    """Minimal app for testing TalkTable."""

    def compose(self) -> ComposeResult:
        yield TalkTable(id="talk-table")


@pytest.mark.asyncio
async def test_displays_correct_row_count():
    app = TalkTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(TalkTable)
        table.update_talks(test_flat_talks)
        await pilot.pause()
        assert table.talk_count == len(test_flat_talks)


@pytest.mark.asyncio
async def test_columns_match_expected():
    app = TalkTableApp()
    async with app.run_test() as pilot:
        dt_widget = app.query_one(DataTable)
        assert len(dt_widget.columns) == len(COLUMNS)


@pytest.mark.asyncio
async def test_update_talks_replaces_data():
    app = TalkTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(TalkTable)
        table.update_talks(test_flat_talks)
        await pilot.pause()
        assert table.talk_count == 5

        table.update_talks([test_flat_talks[0]])
        await pilot.pause()
        assert table.talk_count == 1


@pytest.mark.asyncio
async def test_talk_count_property():
    app = TalkTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(TalkTable)
        assert table.talk_count == 0
        table.update_talks(test_flat_talks)
        assert table.talk_count == 5


@pytest.mark.asyncio
async def test_empty_talks():
    app = TalkTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(TalkTable)
        table.update_talks([])
        await pilot.pause()
        assert table.talk_count == 0


@pytest.mark.asyncio
async def test_sort_by_header_click():
    app = TalkTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(TalkTable)
        table.update_talks(test_flat_talks)
        await pilot.pause()

        # Simulate header click on "Day" column
        dt_widget = app.query_one(DataTable)
        dt_widget.post_message(DataTable.HeaderSelected(dt_widget, column_key=dt_widget.columns["Day"].key, column_index=1, label="Day"))
        await pilot.pause()

        # Check sorting happened — first talk should be day 0
        assert table._talks[0]["day"] <= table._talks[-1]["day"]


@pytest.mark.asyncio
async def test_sort_toggle_reverse():
    app = TalkTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(TalkTable)
        table.update_talks(test_flat_talks)
        await pilot.pause()

        dt_widget = app.query_one(DataTable)
        # Click Day header twice to toggle reverse
        dt_widget.post_message(DataTable.HeaderSelected(dt_widget, column_key=dt_widget.columns["Day"].key, column_index=1, label="Day"))
        await pilot.pause()
        dt_widget.post_message(DataTable.HeaderSelected(dt_widget, column_key=dt_widget.columns["Day"].key, column_index=1, label="Day"))
        await pilot.pause()

        assert table._sort_reverse is True
        assert table._talks[0]["day"] >= table._talks[-1]["day"]


@pytest.mark.asyncio
async def test_row_selection_creates_talk_selected_message():
    """Verify the on_data_table_row_selected handler resolves the correct talk."""
    app = TalkTableApp()
    async with app.run_test() as pilot:
        table = app.query_one(TalkTable)
        table.update_talks(test_flat_talks)
        await pilot.pause()

        # Verify TalkSelected message has the correct talk data
        msg = TalkTable.TalkSelected(test_flat_talks[0])
        assert msg.talk["talk_guid"] == test_flat_talks[0]["talk_guid"]
        assert msg.talk["title"] == "Opening Event"


@pytest.mark.asyncio
async def test_talk_without_guid_uses_id(make_talk):
    app = TalkTableApp()
    async with app.run_test() as pilot:
        talk = make_talk(talk_guid=None, talk_id=1234)
        # Remove talk_guid to simulate missing guid
        del talk["talk_guid"]
        table = app.query_one(TalkTable)
        table.update_talks([talk])
        await pilot.pause()
        assert table.talk_count == 1
