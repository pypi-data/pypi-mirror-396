"""Test the plugin module.

Copied and adapted from https://github.com/omnivector-solutions/jobbergate/blob/main/jobbergate-agent/tests/utils.py/test_plugin.py.
"""

from unittest import mock

import pytest

from vantage_agent.plugin import load_plugins
from vantage_agent.tasks import (
    cluster_config_task,
    cluster_node_task,
    cluster_partition_task,
    cluster_queue_actions_task,
    cluster_queue_task,
    self_update_task,
    status_report_task,
    sync_cluster_partitions_task,
)


def test_discover_tasks__success():
    """Test that discover_tasks returns the expected result."""
    expected_result = {
        "cluster-config": cluster_config_task,
        "cluster-partition": cluster_partition_task,
        "cluster-queue": cluster_queue_task,
        "cluster-queue-actions": cluster_queue_actions_task,
        "cluster-node": cluster_node_task,
        "partitions-sync": sync_cluster_partitions_task,
        "self-update": self_update_task,
        "status-report": status_report_task,
    }
    actual_result = load_plugins("tasks")

    assert actual_result == expected_result


@mock.patch("vantage_agent.plugin.entry_points")
def test_discover__fail_to_load(mocked_entry_points):
    """Test that discover_tasks raises RuntimeError when fails to load."""
    mocked_pluging = mock.Mock()
    mocked_pluging.load.side_effect = Exception("Test")
    mocked_entry_points.return_value = [mocked_pluging]

    with pytest.raises(RuntimeError, match="^Failed to load plugin"):
        load_plugins("non-existent-plugin")
