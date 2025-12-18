"""Core module for testing the vantage_agent/main.py module."""

import asyncio
from unittest import mock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from vantage_agent.main import main


@pytest.fixture
def mock_init_scheduler(monkeypatch: MonkeyPatch):
    """Mock the init_scheduler function."""
    mock_scheduler = mock.Mock()
    monkeypatch.setattr("vantage_agent.main.init_scheduler", mock_scheduler)
    return mock_scheduler


@pytest.fixture
def mock_new_event_loop(monkeypatch: MonkeyPatch):
    """Mock the new_event_loop function."""
    mock_loop = mock.Mock()
    monkeypatch.setattr(asyncio, "new_event_loop", lambda: mock_loop)
    monkeypatch.setattr(asyncio, "set_event_loop", mock.Mock())
    return mock_loop


@pytest.fixture
def mock_logger(monkeypatch: MonkeyPatch):
    """Mock the logger object."""
    mock_logger = mock.Mock()
    monkeypatch.setattr("vantage_agent.main.logger", mock_logger)
    return mock_logger


@pytest.fixture
def mock_init_sentry(monkeypatch: MonkeyPatch):
    """Mock the init_sentry function."""
    mock_init_sentry = mock.Mock()
    monkeypatch.setattr("vantage_agent.main.init_sentry", mock_init_sentry)
    return mock_init_sentry


class TestMainFunction:
    """Test cases for the main function."""

    def test_normal_execution(
        self,
        mock_init_scheduler: mock.MagicMock,
        mock_new_event_loop: mock.MagicMock,
        mock_logger: mock.MagicMock,
        mock_init_sentry: mock.MagicMock,
    ):
        """Test main function under normal execution (no exceptions)."""

        # Make call_soon execute the callback immediately to trigger init_scheduler
        def execute_callback(callback):
            callback()

        mock_new_event_loop.call_soon.side_effect = execute_callback
        mock_new_event_loop.run_forever.side_effect = lambda: None

        main()

        mock_logger.info.assert_called_once_with("Starting the Vantage Agent")
        mock_init_scheduler.assert_called_once()
        mock_new_event_loop.call_soon.assert_called_once()
        mock_new_event_loop.run_forever.assert_called_once()
        mock_new_event_loop.close.assert_called_once()
        mock_init_sentry.assert_called_once_with()
        assert not mock_init_scheduler.return_value.shut_down.called
