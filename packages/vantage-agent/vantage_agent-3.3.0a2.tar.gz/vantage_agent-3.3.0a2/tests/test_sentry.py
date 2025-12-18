"""Core module for testing the vantage_agent/sentry.py module."""

import uuid
from unittest import mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from sentry_sdk.utils import BadDsn

from vantage_agent.sentry import init_sentry


@pytest.fixture
def mock_logger(monkeypatch: MonkeyPatch) -> mock.MagicMock:
    """Mock the logger instance."""
    mock_logger = mock.Mock()
    monkeypatch.setattr("vantage_agent.sentry.logger", mock_logger)
    return mock_logger


@pytest.fixture
def mock_sentry_sdk(monkeypatch: MonkeyPatch) -> mock.MagicMock:
    """Mock the sentry_sdk instance."""
    mock_sentry_sdk = mock.Mock()
    monkeypatch.setattr("vantage_agent.sentry.sentry_sdk", mock_sentry_sdk)
    return mock_sentry_sdk


@pytest.fixture
def mock_settings(monkeypatch: MonkeyPatch) -> mock.MagicMock:
    """Mock the settings instance."""
    mock_settings = mock.Mock()
    monkeypatch.setattr("vantage_agent.sentry.SETTINGS", mock_settings)
    return mock_settings


class TestInitSentry:
    """Test cases for the init_sentry function."""

    def test_init_sentry_bad_dsn(self, mock_logger: mock.MagicMock, mock_sentry_sdk: mock.MagicMock) -> None:
        """Test the init_sentry function when the DSN is invalid."""
        mock_sentry_sdk.init.side_effect = BadDsn("Invalid DSN")

        init_sentry()

        mock_sentry_sdk.init.assert_called_once()
        mock_logger.debug.assert_called_once_with("Sentry could not be enabled: Invalid DSN")

    def test_init_sentry_success(
        self, mock_logger: mock.MagicMock, mock_sentry_sdk: mock.MagicMock, mock_settings: mock.MagicMock
    ) -> None:
        """Test the init_sentry function when the DSN is valid."""
        mock_settings.SENTRY_DSN = str(uuid.uuid4())

        init_sentry()

        mock_sentry_sdk.init.assert_called_once()
        mock_logger.debug.assert_called_once_with("Enabled Sentry since a valid DSN key was provided.")

    def test_init_sentry_empty_dsn(
        self, mock_logger: mock.MagicMock, mock_sentry_sdk: mock.MagicMock, mock_settings: mock.MagicMock
    ) -> None:
        """Test the init_sentry function when the DSN is empty."""
        mock_settings.SENTRY_DSN = ""

        init_sentry()

        mock_sentry_sdk.init.assert_called_once()
        mock_logger.debug.assert_called_once_with("Enabled Sentry since a valid DSN key was provided.")
