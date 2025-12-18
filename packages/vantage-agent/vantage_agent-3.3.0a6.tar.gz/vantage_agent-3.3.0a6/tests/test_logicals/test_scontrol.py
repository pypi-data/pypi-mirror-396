"""Core module for testing the vantage_agent/logicals/scontrol.py module."""

import asyncio
import subprocess
from typing import Generator
from unittest import mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from jsondiff import diff

from vantage_agent.logicals.scontrol import (
    SETTINGS,
    upload_scontrol_config,
    upload_scontrol_node,
    upload_scontrol_partition,
)


@pytest.fixture
def mock_upload_scontrol_config(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the upload_slurm_config function."""
    mock_upload = mock.AsyncMock()
    monkeypatch.setattr("vantage_agent.logicals.scontrol.upload_slurm_config", mock_upload)
    return mock_upload


@pytest.fixture
def mock_upload_scontrol_node(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the upload_slurm_nodes function."""
    mock_upload = mock.AsyncMock()
    monkeypatch.setattr("vantage_agent.logicals.scontrol.upload_slurm_nodes", mock_upload)
    return mock_upload


@pytest.fixture
def mock_upload_scontrol_partition(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the upload_slurm_partitions function."""
    mock_upload = mock.AsyncMock()
    monkeypatch.setattr("vantage_agent.logicals.scontrol.upload_slurm_partitions", mock_upload)
    return mock_upload


@pytest.fixture
def mock_subprocess_run(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the subprocess.run function."""
    mock_run = mock.Mock()
    mock_run.return_value.stdout = "Sample scontrol config output"
    monkeypatch.setattr(subprocess, "run", mock_run)
    yield mock_run


@pytest.fixture
def mock_parse_slurm_config(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the parse_slurm_config function."""
    mock_parse = mock.Mock()
    mock_parse.return_value = {"venice": "rome"}
    monkeypatch.setattr("vantage_agent.logicals.scontrol.parse_slurm_config", mock_parse)
    return mock_parse


@pytest.fixture
def mock_load_cached_dict(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the load_cached_dict function."""
    mock_load = mock.Mock()
    mock_load.return_value = {"sydney": "perth"}
    monkeypatch.setattr("vantage_agent.logicals.scontrol.load_cached_dict", mock_load)
    return mock_load


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
    monkeypatch.setattr("vantage_agent.logicals.scontrol.logger", mock_logger)
    return mock_logger


@pytest.fixture
def mock_parse_slurm_partitions(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the parse_slurm_partitions function."""
    mock_parse = mock.Mock()
    mock_parse.return_value = {"partition1": {"State": "UP"}}
    monkeypatch.setattr("vantage_agent.logicals.scontrol.parse_slurm_partitions", mock_parse)
    return mock_parse


@pytest.fixture
def mock_parse_slurm_nodes(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the parse_slurm_nodes function."""
    mock_parse = mock.Mock()
    mock_parse.return_value = {"node1": {"State": "IDLE"}}
    monkeypatch.setattr("vantage_agent.logicals.scontrol.parse_slurm_nodes", mock_parse)
    return mock_parse


class TestUploadScontrolConfig:
    """Test cases for the upload_scontrol_config function."""

    def test_config_changes_detected(
        self,
        mock_subprocess_run: mock.MagicMock,
        mock_parse_slurm_config: mock.MagicMock,
        mock_load_cached_dict: mock.MagicMock,
        mock_asyncio_run: mock.MagicMock,
        mock_logger: mock.MagicMock,
        mock_upload_scontrol_config: mock.MagicMock,
    ):
        """Test when there are changes in the Slurm configuration."""
        upload_scontrol_config()

        mock_subprocess_run.assert_called_once_with(
            [SETTINGS.SCONTROL_PATH, "show", "config"], stdout=subprocess.PIPE, text=True
        )
        mock_parse_slurm_config.assert_called_once()
        mock_load_cached_dict.assert_called_once_with("slurm_config.json")
        mock_asyncio_run.assert_called_once()
        mock_upload_scontrol_config.assert_called_once_with(
            diff(mock_load_cached_dict.return_value, mock_parse_slurm_config.return_value, marshal=True)
        )
        mock_logger.debug.assert_any_call(
            "Detected changes in Slurm's configuration. Uploading to the API..."
        )

    def test_no_config_changes(
        self,
        mock_subprocess_run: mock.MagicMock,
        mock_parse_slurm_config: mock.MagicMock,
        mock_load_cached_dict: mock.MagicMock,
        mock_asyncio_run: mock.MagicMock,
        mock_logger: mock.MagicMock,
        mock_upload_scontrol_config: mock.MagicMock,
    ):
        """Test when there are no changes in the Slurm configuration."""
        mock_load_cached_dict.return_value = mock_parse_slurm_config.return_value
        upload_scontrol_config()

        mock_subprocess_run.assert_called_once_with(
            [SETTINGS.SCONTROL_PATH, "show", "config"], stdout=subprocess.PIPE, text=True
        )
        mock_parse_slurm_config.assert_called_once()
        mock_load_cached_dict.assert_called_once_with("slurm_config.json")
        mock_asyncio_run.assert_not_called()
        mock_upload_scontrol_config.assert_not_called()
        mock_logger.debug.assert_any_call("No changes detected in Slurm's configuration.")


class TestUploadScontrolPartition:
    """Test cases for the upload_scontrol_partition function."""

    def test_partition_changes_detected(
        self,
        mock_subprocess_run: mock.MagicMock,
        mock_parse_slurm_partitions: mock.MagicMock,
        mock_load_cached_dict: mock.MagicMock,
        mock_asyncio_run: mock.MagicMock,
        mock_logger: mock.MagicMock,
        mock_upload_scontrol_partition: mock.MagicMock,
    ):
        """Test when there are changes in the Slurm partitions."""
        upload_scontrol_partition()

        mock_subprocess_run.assert_called_once_with(
            [SETTINGS.SCONTROL_PATH, "show", "partition"], stdout=subprocess.PIPE, text=True
        )
        mock_parse_slurm_partitions.assert_called_once()
        mock_load_cached_dict.assert_called_once_with("slurm_partitions.json")
        mock_upload_scontrol_partition.assert_called_once_with(
            diff(mock_load_cached_dict.return_value, mock_parse_slurm_partitions.return_value, marshal=True)
        )
        mock_logger.debug.assert_has_calls(
            calls=[
                mock.call("Getting Slurm's partition information"),
                mock.call("Parsing Slurm's partitions"),
                mock.call("Loading cached Slurm's partitions"),
                mock.call("Computing difference between cached and current partitions"),
                mock.call("Detected changes in Slurm's configuration. Uploading to the API..."),
            ]
        )
        assert mock_asyncio_run.call_count == 1

    def test_no_partition_changes(
        self,
        mock_subprocess_run: mock.MagicMock,
        mock_parse_slurm_partitions: mock.MagicMock,
        mock_load_cached_dict: mock.MagicMock,
        mock_asyncio_run: mock.MagicMock,
        mock_logger: mock.MagicMock,
        mock_upload_scontrol_partition: mock.MagicMock,
    ):
        """Test when there are no changes in the Slurm partitions."""
        mock_parse_slurm_partitions.return_value = mock_load_cached_dict.return_value

        upload_scontrol_partition()

        mock_subprocess_run.assert_called_once_with(
            [SETTINGS.SCONTROL_PATH, "show", "partition"], stdout=subprocess.PIPE, text=True
        )
        mock_parse_slurm_partitions.assert_called_once()
        mock_load_cached_dict.assert_called_once_with("slurm_partitions.json")
        mock_asyncio_run.assert_not_called()
        mock_upload_scontrol_partition.assert_not_called()
        mock_logger.debug.assert_has_calls(
            calls=[
                mock.call("Getting Slurm's partition information"),
                mock.call("Parsing Slurm's partitions"),
                mock.call("Loading cached Slurm's partitions"),
                mock.call("Computing difference between cached and current partitions"),
                mock.call("No changes detected in Slurm's partitions."),
            ]
        )


class TestUploadScontrolNode:
    """Test cases for the upload_scontrol_node function."""

    def test_node_changes_detected(
        self,
        mock_subprocess_run: mock.MagicMock,
        mock_parse_slurm_nodes: mock.MagicMock,
        mock_load_cached_dict: mock.MagicMock,
        mock_asyncio_run: mock.MagicMock,
        mock_logger: mock.MagicMock,
        mock_upload_scontrol_node: mock.MagicMock,
    ):
        """Test when there are changes in the Slurm nodes."""
        upload_scontrol_node()

        mock_subprocess_run.assert_called_once_with(
            [SETTINGS.SCONTROL_PATH, "show", "node"], stdout=subprocess.PIPE, text=True
        )
        mock_parse_slurm_nodes.assert_called_once()
        mock_load_cached_dict.assert_called_once_with("slurm_nodes.json")
        mock_upload_scontrol_node.assert_called_once_with(
            diff(mock_load_cached_dict.return_value, mock_parse_slurm_nodes.return_value, marshal=True)
        )
        assert mock_asyncio_run.call_count == 1
        mock_logger.debug.assert_has_calls(
            calls=[
                mock.call("Getting Slurm's node information"),
                mock.call("Parsing Slurm's nodes"),
                mock.call("Loading cached Slurm's nodes"),
                mock.call("Computing difference between cached and current nodes"),
                mock.call("Detected changes in Slurm's nodes. Uploading to the API..."),
            ]
        )

    def test_no_node_changes(
        self,
        mock_subprocess_run: mock.MagicMock,
        mock_parse_slurm_nodes: mock.MagicMock,
        mock_load_cached_dict: mock.MagicMock,
        mock_asyncio_run: mock.MagicMock,
        mock_logger: mock.MagicMock,
        mock_upload_scontrol_node: mock.MagicMock,
    ):
        """Test when there are no changes in the Slurm nodes."""
        mock_parse_slurm_nodes.return_value = mock_load_cached_dict.return_value

        upload_scontrol_node()

        mock_subprocess_run.assert_called_once_with(
            [SETTINGS.SCONTROL_PATH, "show", "node"], stdout=subprocess.PIPE, text=True
        )
        mock_parse_slurm_nodes.assert_called_once()
        mock_load_cached_dict.assert_called_once_with("slurm_nodes.json")
        mock_asyncio_run.assert_not_called()
        mock_upload_scontrol_node.assert_not_called()
        mock_logger.debug.assert_has_calls(
            calls=[
                mock.call("Getting Slurm's node information"),
                mock.call("Parsing Slurm's nodes"),
                mock.call("Loading cached Slurm's nodes"),
                mock.call("Computing difference between cached and current nodes"),
                mock.call("No changes detected in Slurm's nodes."),
            ]
        )
