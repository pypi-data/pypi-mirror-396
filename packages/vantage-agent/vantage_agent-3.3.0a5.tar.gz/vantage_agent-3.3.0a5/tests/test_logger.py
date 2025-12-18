"""Core module for testing the vantage_agent/logger.py module."""

from traceback import format_tb
from unittest import mock

import pytest

from vantage_agent.logger import DoExceptParams, log_error, logger_wraps


def sample_function(a, b):
    """This is a sample function to be decorated for testing."""  # noqa: D401,D404
    return a + b


@pytest.fixture
def mock_logger(monkeypatch):
    """Mock the logger object."""
    mock_logger = mock.Mock()
    monkeypatch.setattr("vantage_agent.logger.logger", mock_logger)
    return mock_logger


class TestLogError:
    """Test the log_error function."""

    def test_log_error(self, mock_logger):
        """Test the log_error function."""
        try:
            1 / 0
        except ZeroDivisionError as e:
            params = DoExceptParams(
                err=e,
                base_message="Sample error message",
                final_message="Sample error message",
                trace=e.__traceback__,
            )
            log_error(params)

        expected_message = "\n".join(
            [
                "Sample error message",
                "--------",
                "Traceback:",
                "".join(format_tb(params.trace)),
            ]
        )
        mock_logger.error.assert_called_once_with(expected_message)


class TestLoggerWraps:
    """Test the logger_wraps decorator."""

    def test_entry_only(self, mock_logger):
        """Test logging only the entry message."""

        @logger_wraps(exit=False)
        def decorated_func(a, b):
            return sample_function(a, b)

        result = decorated_func(2, 3)

        mock_logger.opt.assert_called_once_with(depth=1)
        mock_logger.opt.return_value.log.assert_called_once_with(
            "DEBUG", "Entering 'decorated_func' (args=(2, 3), kwargs={})"
        )
        assert result == 5

    def test_exit_only(self, mock_logger):
        """Test logging only the exit message."""

        @logger_wraps(entry=False)
        def decorated_func(a, b):
            return sample_function(a, b)

        result = decorated_func(2, 3)

        mock_logger.opt.assert_called_once_with(depth=1)
        mock_logger.opt.return_value.log.assert_called_once_with(
            "DEBUG", "Exiting 'decorated_func' (result=5)"
        )
        assert result == 5

    def test_no_logging(self, mock_logger):
        """Test that no logging occurs when both entry and exit are False."""

        @logger_wraps(entry=False, exit=False)
        def decorated_func(a, b):
            return sample_function(a, b)

        result = decorated_func(2, 3)

        mock_logger.opt.assert_called_once_with(depth=1)
        mock_logger.opt.return_value.log.assert_not_called()
        assert result == 5

    def test_custom_log_level(self, mock_logger):
        """Test logging at a custom log level (INFO)."""

        @logger_wraps(level="INFO")
        def decorated_func(a, b):
            return sample_function(a, b)

        result = decorated_func(2, 3)

        mock_logger.opt.assert_called_once_with(depth=1)
        mock_logger.opt.return_value.log.assert_has_calls(
            [
                mock.call("INFO", "Entering 'decorated_func' (args=(2, 3), kwargs={})"),
                mock.call("INFO", "Exiting 'decorated_func' (result=5)"),
            ]
        )
        assert result == 5
