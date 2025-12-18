"""Core module for testing the vantage_agent/scheduler.py module.

Copied and adapted from https://github.com/omnivector-solutions/jobbergate/blob/main/jobbergate-agent/tests/utils.py/test_scheduler.py.
"""

from unittest import mock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from vantage_agent.scheduler import (
    AsyncIOScheduler,
    init_scheduler,
    load_plugins,
    schedule_tasks,
    shut_down_scheduler,
)


@pytest.fixture
def mock_load_plugins(monkeypatch: MonkeyPatch) -> mock.MagicMock:
    """Mock the load_plugins function."""
    mock_scheduler = mock.Mock()
    monkeypatch.setattr("vantage_agent.scheduler.load_plugins", mock_scheduler)
    return mock_scheduler


@pytest.fixture
def mock_scheduler(monkeypatch: MonkeyPatch) -> mock.MagicMock:
    """Mock the AsyncIOScheduler class."""
    mock_scheduler = mock.Mock()
    monkeypatch.setattr("vantage_agent.scheduler.scheduler", mock_scheduler)
    return mock_scheduler


class TestScheduleTasks:
    """Test the schedule_tasks function."""

    def test_schedule_tasks__success(self, mock_load_plugins: mock.MagicMock):
        """Test that schedule_tasks returns the expected result."""
        discovered_functions = load_plugins("tasks")
        mocked_functions = {name: mock.Mock() for name in discovered_functions.keys()}

        mock_load_plugins.return_value = mocked_functions

        scheduler = AsyncIOScheduler()
        schedule_tasks(scheduler)

        mock_load_plugins.assert_called_once_with("tasks")
        assert all(m.call_count == 1 for m in mocked_functions.values())
        assert all(m.call_args(scheduler=scheduler) for m in mocked_functions.values())

    def test_schedule_tasks__fails(self, mock_load_plugins: mock.MagicMock):
        """Test that schedule_tasks raises RuntimeError when fails to schedule a task."""
        mocked_functions = {"supposed-to-fail": mock.Mock(side_effect=Exception("Test"))}

        mock_load_plugins.return_value = mocked_functions

        scheduler = AsyncIOScheduler()

        with pytest.raises(RuntimeError, match="^Failed to execute"):
            schedule_tasks(scheduler)

        mock_load_plugins.assert_called_once_with("tasks")


@mock.patch("vantage_agent.scheduler.schedule_tasks")
def test_init_scheduler(mock_schedule_tasks: mock.MagicMock, mock_scheduler: mock.MagicMock):
    """Test the init_scheduler function."""
    scheduler = init_scheduler()
    mock_scheduler.start.assert_called_once_with()
    mock_schedule_tasks.assert_called_once_with(mock_scheduler)
    assert scheduler is mock_scheduler


@pytest.mark.parametrize("wait", [True, False])
def test_shut_down_scheduler(wait: bool, mock_scheduler: mock.MagicMock):
    """Test the shut_down_scheduler function."""
    shut_down_scheduler(mock_scheduler, wait)
    mock_scheduler.shutdown.assert_called_once_with(wait)
