"""Core module for testing the vantage_agent/logicals/scontrol.py module."""

import asyncio
import subprocess
from typing import Generator
from unittest import mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from jsondiff import diff

from vantage_agent.logicals.squeue import (
    SETTINGS,
    upload_squeue_queue,
)


@pytest.fixture
def mock_upload_squeue_queue(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the upload_slurm_queue function."""
    mock_upload = mock.AsyncMock()
    monkeypatch.setattr("vantage_agent.logicals.squeue.upload_slurm_queue", mock_upload)
    return mock_upload


@pytest.fixture
def mock_subprocess_run(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the subprocess.run function."""
    mock_run = mock.Mock()
    mock_run.return_value.stdout = "Sample squeue config output"
    monkeypatch.setattr(subprocess, "run", mock_run)
    yield mock_run


@pytest.fixture
def mock_load_cached_dict(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the load_cached_dict function."""
    mock_load = mock.Mock()
    mock_load.return_value = [{"sydney": "perth"}]
    monkeypatch.setattr("vantage_agent.logicals.squeue.load_cached_dict", mock_load)
    return mock_load


@pytest.fixture
def mock_cache_dict(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the load_cached_dict function."""
    mock_cache = mock.Mock()
    monkeypatch.setattr("vantage_agent.logicals.squeue.cache_dict", mock_cache)
    return mock_cache


@pytest.fixture
def mock_asyncio_run(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the asyncio.run function."""
    mock_run = mock.MagicMock()
    monkeypatch.setattr(asyncio, "run", mock_run)
    return mock_run


@pytest.fixture
def mock_logger(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the logger."""
    mock_logger = mock.Mock()
    monkeypatch.setattr("vantage_agent.logicals.squeue.logger", mock_logger)
    return mock_logger


@pytest.fixture
def mock_parse_slurm_queue(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the parse_slurm_queue function."""
    mock_parse = mock.Mock()
    mock_parse.return_value = [{"state": "RUNNING", "name": "job-name"}]
    monkeypatch.setattr("vantage_agent.logicals.squeue.parse_slurm_queue", mock_parse)
    return mock_parse


class TestUploadSqueueQueue:
    """Test cases for the upload_squeue_queue function."""

    def test_queue_changes_detected(
        self,
        mock_subprocess_run: mock.MagicMock,
        mock_parse_slurm_queue: mock.MagicMock,
        mock_cache_dict: mock.MagicMock,
        mock_load_cached_dict: mock.MagicMock,
        mock_asyncio_run: mock.MagicMock,
        mock_logger: mock.MagicMock,
        mock_upload_squeue_queue: mock.MagicMock,
    ):
        """Test when there are changes in the Slurm queue."""
        upload_squeue_queue()

        mock_subprocess_run.assert_called_once_with(
            [SETTINGS.SQUEUE_PATH, "-o", "%all"], stdout=subprocess.PIPE, text=True
        )
        mock_parse_slurm_queue.assert_called_once()
        mock_load_cached_dict.assert_called_once_with("slurm_queue.json")
        mock_upload_squeue_queue.assert_called_once_with(
            diff(mock_load_cached_dict.return_value, mock_parse_slurm_queue.return_value, marshal=True)
        )
        mock_logger.debug.assert_has_calls(
            calls=[
                mock.call("Getting Slurm's queue information"),
                mock.call("Parsing Slurm's queue"),
                mock.call("Loading cached Slurm's queue"),
                mock.call("Computing difference between cached and current queue"),
                mock.call("Detected changes in Slurm's configuration. Uploading to the API..."),
            ]
        )
        mock_cache_dict.assert_called_once_with(mock_parse_slurm_queue.return_value, "slurm_queue.json")
        assert mock_asyncio_run.call_count == 1

    def test_no_queue_changes(
        self,
        mock_subprocess_run: mock.MagicMock,
        mock_parse_slurm_queue: mock.MagicMock,
        mock_load_cached_dict: mock.MagicMock,
        mock_asyncio_run: mock.MagicMock,
        mock_logger: mock.MagicMock,
        mock_upload_squeue_queue: mock.MagicMock,
    ):
        """Test when there are no changes in the Slurm queue."""
        mock_parse_slurm_queue.return_value = mock_load_cached_dict.return_value

        upload_squeue_queue()

        mock_subprocess_run.assert_called_once_with(
            [SETTINGS.SQUEUE_PATH, "-o", "%all"],
            stdout=subprocess.PIPE,
            text=True,  # noqa
        )
        mock_parse_slurm_queue.assert_called_once()
        mock_load_cached_dict.assert_called_once_with("slurm_queue.json")
        mock_asyncio_run.assert_not_called()
        mock_upload_squeue_queue.assert_not_called()
        mock_logger.debug.assert_has_calls(
            calls=[
                mock.call("Getting Slurm's queue information"),
                mock.call("Parsing Slurm's queue"),
                mock.call("Loading cached Slurm's queue"),
                mock.call("Computing difference between cached and current queue"),
                mock.call("No changes detected in Slurm's queue."),
            ]
        )
