"""Core module for testing the vantage_agent/tasks.py module."""

from unittest import mock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from vantage_agent.tasks import (
    cluster_config_task,
    cluster_node_task,
    cluster_partition_task,
    cluster_queue_actions_task,
    cluster_queue_task,
    report_health_status,
    self_update_agent,
    self_update_task,
    status_report_task,
    sync_cluster_partitions,
    sync_cluster_partitions_task,
    upload_scontrol_config,
    upload_scontrol_node,
    upload_scontrol_partition,
    upload_squeue_queue,
)


@pytest.fixture
def mock_scheduler() -> mock.MagicMock:
    """Mock the BaseScheduler class."""
    mock_scheduler = mock.Mock(spec=["add_job"])
    return mock_scheduler


@pytest.fixture
def mock_settings(monkeypatch: MonkeyPatch) -> mock.MagicMock:
    """Mock the settings module."""
    mock_settings = mock.Mock()
    monkeypatch.setattr("vantage_agent.tasks.SETTINGS", mock_settings)
    return mock_settings


class TestSchedulerTasks:
    """Test the task scheduling functions."""

    @pytest.mark.parametrize("interval", [30, 60, 100])
    def test_cluster_config_task(
        self, interval: int | None, mock_scheduler: mock.MagicMock, mock_settings: mock.MagicMock
    ):
        """Test the cluster_config_task function."""
        mock_settings.TASK_JOBS_INTERVAL_SECONDS = interval
        job = cluster_config_task(mock_scheduler)
        mock_scheduler.add_job.assert_called_once_with(upload_scontrol_config, "interval", seconds=interval)
        assert isinstance(job, mock.Mock)

    @pytest.mark.parametrize("interval", [30, 60, 100])
    def test_cluster_partition_task(
        self, interval: int | None, mock_scheduler: mock.MagicMock, mock_settings: mock.MagicMock
    ):
        """Test the cluster_partition_task function."""
        mock_settings.TASK_JOBS_INTERVAL_SECONDS = interval
        job = cluster_partition_task(mock_scheduler)
        mock_scheduler.add_job.assert_called_once_with(
            upload_scontrol_partition, "interval", seconds=interval
        )
        assert isinstance(job, mock.Mock)

    @pytest.mark.parametrize("interval", [30, 60, 100])
    def test_cluster_queue_task(
        self, interval: int | None, mock_scheduler: mock.MagicMock, mock_settings: mock.MagicMock
    ):
        """Test the cluster_queue_task function."""
        mock_settings.TASK_JOBS_INTERVAL_SECONDS = interval
        job = cluster_queue_task(mock_scheduler)
        mock_scheduler.add_job.assert_called_once_with(upload_squeue_queue, "interval", seconds=interval)
        assert isinstance(job, mock.Mock)

    @pytest.mark.parametrize("interval", [30, 60, 100])
    def test_cluster_node_task(
        self, interval: int | None, mock_scheduler: mock.MagicMock, mock_settings: mock.MagicMock
    ):
        """Test the cluster_node_task function."""
        mock_settings.TASK_JOBS_INTERVAL_SECONDS = interval
        job = cluster_node_task(mock_scheduler)
        mock_scheduler.add_job.assert_called_once_with(upload_scontrol_node, "interval", seconds=interval)
        assert isinstance(job, mock.Mock)

    @pytest.mark.parametrize("interval", [30, 60, 100])
    def test_self_update_task_enabled(
        self, interval: int | None, mock_scheduler: mock.MagicMock, mock_settings: mock.MagicMock
    ):
        """Test the self_update_task function with a valid interval."""
        mock_settings.TASK_SELF_UPDATE_INTERVAL_SECONDS = interval
        job = self_update_task(mock_scheduler)
        mock_scheduler.add_job.assert_called_once_with(self_update_agent, "interval", seconds=interval)
        assert isinstance(job, mock.Mock)

    def test_self_update_task_disabled(self, mock_scheduler: mock.MagicMock, mock_settings: mock.MagicMock):
        """Test the self_update_task function with a None interval."""
        mock_settings.TASK_SELF_UPDATE_INTERVAL_SECONDS = None
        job = self_update_task(mock_scheduler)
        mock_scheduler.add_job.assert_not_called()
        assert job is None

    @pytest.mark.parametrize("interval", [30, 60, 100])
    def test_status_report_task(
        self, interval: int, mock_scheduler: mock.MagicMock, mock_settings: mock.MagicMock
    ):
        """Test the status_report_task function."""
        mock_settings.TASK_JOBS_INTERVAL_SECONDS = interval
        job = status_report_task(mock_scheduler)
        mock_scheduler.add_job.assert_called_once_with(report_health_status, "interval", seconds=interval)
        assert isinstance(job, mock.Mock)

    @pytest.mark.parametrize("interval", [30, 60, 100])
    def test_sync_slurm_partitions_task(
        self, interval: int, mock_scheduler: mock.MagicMock, mock_settings: mock.MagicMock
    ):
        """Test the sync_cluster_partitions_task function."""
        mock_settings.TASK_JOBS_INTERVAL_SECONDS = interval
        job = sync_cluster_partitions_task(mock_scheduler)
        mock_scheduler.add_job.assert_called_once_with(sync_cluster_partitions, "interval", seconds=interval)
        assert isinstance(job, mock.Mock)

    def test_sync_slurm_partitions_task_disabled(
        self, mock_scheduler: mock.MagicMock, mock_settings: mock.MagicMock
    ):
        """Test if the `sync_cluster_partitions` task is not scheduled for on-premises clusters."""
        mock_settings.IS_CLOUD_CLUSTER = False
        job = sync_cluster_partitions_task(mock_scheduler)
        mock_scheduler.add_job.assert_not_called()
        assert job is None

    @pytest.mark.parametrize("interval", [30, 60, 100])
    def test_cluster_queue_actions_task(
        self, interval: int | None, mock_scheduler: mock.MagicMock, mock_settings: mock.MagicMock
    ):
        """Test the cluster_queue_actions_task function."""
        mock_settings.TASK_JOBS_INTERVAL_SECONDS = interval
        from vantage_agent.logicals.queue_actions import process_cluster_queue_actions

        job = cluster_queue_actions_task(mock_scheduler)
        mock_scheduler.add_job.assert_called_once_with(
            process_cluster_queue_actions, "interval", seconds=interval
        )
        assert isinstance(job, mock.Mock)
