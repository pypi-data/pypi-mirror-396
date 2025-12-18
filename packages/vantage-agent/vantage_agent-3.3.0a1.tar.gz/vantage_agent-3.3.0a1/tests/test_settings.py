"""Core module for testing the vantage_agent/settings.py module."""

from pathlib import Path
from unittest import mock

import pytest

from vantage_agent.settings import Settings, _define_dotenv_file_location, _init_settings


@pytest.mark.parametrize(
    "scontrol_path",
    [
        Path("relative/scontrol"),
        Path("usr/bin/scontrol"),
    ],
)
def test_validate_scontrol_path(scontrol_path: Path):
    """Test whether the Settings class accepts a non-absolute path for SCONTROL_PATH or not."""
    with pytest.raises(ValueError):
        Settings(SCONTROL_PATH=scontrol_path)  # type: ignore[call-arg]


@pytest.mark.parametrize(
    "error",
    [
        ValueError("Testing foo"),
        ValueError("Testing bar"),
        ValueError("Best pubs are in Camden Town"),
    ],
)
@mock.patch("vantage_agent.settings.Settings")
@mock.patch("vantage_agent.settings.logger")
@mock.patch("vantage_agent.settings.sys")
def test_init_settings(
    mock_sys: mock.MagicMock, mock_logger: mock.MagicMock, mock_settings: mock.MagicMock, error: ValueError
):
    """Test if the _init_settings function raises ValueError when any validation doesn't pass."""
    mock_settings.side_effect = error
    mock_sys.exit = mock.Mock()
    _init_settings()
    mock_logger.error.assert_called_once_with(error)
    mock_sys.exit.assert_called_once_with(1)


class TestDefineDotenvFileLocation:
    """Test the behaviour of the function _define_dotenv_file_location upon different cases."""

    @mock.patch("vantage_agent.settings.Path")
    def test_define_dotenv_file_location(self, mock_path: mock.MagicMock):
        """Test the `_define_dotenv_file_location` returns `/var/snap/vantage-agent/common/.env` when it exists."""  #  noqa: E501
        mocked_path = mock.Mock()
        mocked_path.exists = mock.Mock(return_value=True)
        mock_path.return_value = mocked_path
        assert _define_dotenv_file_location() is mock_path.return_value
        mocked_path.exists.assert_called_once_with()
        mock_path.assert_called_once_with("/var/snap/vantage-agent/common/.env")

    def test_define_dotenv_file_location_default(self):
        """Test if the `_define_dotenv_file_location` returns the default path (`.env`)."""
        assert _define_dotenv_file_location() == Path(".env")
