"""Tests for FahrplanApp."""

import pytest
from unittest.mock import patch, MagicMock

from textual.widgets import Static

from pyfahrplan.app import FahrplanApp


@pytest.mark.asyncio
async def test_app_shows_loading_on_start():
    app = FahrplanApp()
    async with app.run_test() as pilot:
        loading = app.query_one("#loading-message", Static)
        assert "Loading" in str(loading.content)


@pytest.mark.asyncio
async def test_app_transitions_to_main_screen():
    from tests.data.test_data import test_flat_talks

    mock_fp = MagicMock()
    mock_fp.errors = []
    mock_fp.flat_plans = test_flat_talks
    mock_fp.get_conference_acronyms.return_value = ["32c3", "33c3", "34c3", "35c3", "36c3"]

    with patch("pyfahrplan.lib.Fahrplan", return_value=mock_fp):
        app = FahrplanApp()
        async with app.run_test() as pilot:
            await pilot.pause(delay=2)
            from pyfahrplan.screens.main_screen import MainScreen
            assert any(isinstance(s, MainScreen) for s in app.screen_stack)


@pytest.mark.asyncio
async def test_app_shows_error_when_all_fail():
    mock_fp = MagicMock()
    mock_fp.errors = ["Test error message"]
    mock_fp.flat_plans = []

    with patch("pyfahrplan.lib.Fahrplan", return_value=mock_fp):
        app = FahrplanApp()
        async with app.run_test() as pilot:
            await pilot.pause(delay=2)
            loading = app.query_one("#loading-message", Static)
            rendered = str(loading.content)
            assert "Test error" in rendered
