"""Tests for the queue actions logical module."""

import asyncio
import subprocess
from string import Template
from textwrap import dedent
from typing import Generator
from unittest import mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from respx.router import MockRouter

from vantage_agent.logicals.queue_actions import (
    _process_cluster_queue_actions_async,
    execute_scancel,
    extract_job_id_from_queue_info,
    fetch_cluster_queue_actions,
    process_cluster_queue_actions,
    remove_queue_action,
)
from vantage_agent.vantage_api_client import backend_client


@pytest.fixture
def mock_logger(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the logger."""
    mock_logger = mock.Mock()
    monkeypatch.setattr("vantage_agent.logicals.queue_actions.logger", mock_logger)
    return mock_logger


@pytest.fixture
def mock_settings(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the settings."""
    mock_settings = mock.Mock()
    monkeypatch.setattr("vantage_agent.logicals.queue_actions.SETTINGS", mock_settings)
    return mock_settings


@pytest.fixture
def mock_subprocess_run(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the subprocess.run function."""
    mock_run = mock.Mock()
    monkeypatch.setattr(subprocess, "run", mock_run)
    return mock_run


@pytest.fixture
def mock_asyncio_run(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the asyncio.run function."""
    mock_run = mock.Mock()
    monkeypatch.setattr(asyncio, "run", mock_run)
    return mock_run


@pytest.fixture
def mock_async_backend_client(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the AsyncBackendClient."""
    mock_client = mock.AsyncMock()
    mock_client_class = mock.Mock(return_value=mock_client)
    mock_client.__aenter__ = mock.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mock.AsyncMock(return_value=None)
    monkeypatch.setattr("vantage_agent.logicals.queue_actions.AsyncBackendClient", mock_client_class)
    return mock_client


class TestFetchClusterQueueActions:
    """Test cases for the fetch_cluster_queue_actions function."""

    @pytest.mark.respx(base_url=backend_client.base_url)
    @pytest.mark.usefixtures("mock_access_token")
    async def test_fetch_success(
        self,
        respx_mock: MockRouter,
        mock_settings: mock.MagicMock,
    ):
        """Test successful fetching of cluster queue actions."""
        mock_settings.CLUSTER_NAME = "test-cluster"

        response_payload = {
            "data": {
                "clusterQueueActions": {
                    "edges": [
                        {
                            "node": {
                                "id": 1,
                                "clusterName": "test-cluster",
                                "queueId": 123,
                                "action": "cancel",
                                "queue": {
                                    "id": 123,
                                    "name": "test_queue",
                                    "info": {"jobid": "456", "name": "test_job"},
                                },
                            }
                        }
                    ],
                    "total": 1,
                }
            }
        }

        expected_query = dedent(
            Template("""
        query clusterQueueActions {
            clusterQueueActions(
                first: 100
                filters: {
                    clusterName: {
                        eq: "$clusterName"
                    }
                }
            ) {
                edges {
                    node {
                        id
                        clusterName
                        queueId
                        action
                        queue {
                            id
                            name
                            info
                        }
                    }
                }
                total
            }
        }
        """).substitute(clusterName="test-cluster")
        )
        expected_json = {"query": expected_query}
        respx_mock.post("/cluster/graphql", json=expected_json).respond(
            status_code=200, json=response_payload
        )

        actions = await fetch_cluster_queue_actions()

        assert len(actions) == 1
        assert actions[0]["node"]["id"] == 1

    @pytest.mark.respx(base_url=backend_client.base_url)
    @pytest.mark.usefixtures("mock_access_token")
    async def test_fetch_with_errors(
        self,
        respx_mock: MockRouter,
        mock_settings: mock.MagicMock,
        mock_logger: mock.MagicMock,
    ):
        """Test fetching queue actions when API returns errors."""
        mock_settings.CLUSTER_NAME = "test-cluster"

        response_payload = {"errors": ["Some API error"]}

        expected_query = dedent(
            Template("""
        query clusterQueueActions {
            clusterQueueActions(
                first: 100
                filters: {
                    clusterName: {
                        eq: "$clusterName"
                    }
                }
            ) {
                edges {
                    node {
                        id
                        clusterName
                        queueId
                        action
                        queue {
                            id
                            name
                            info
                        }
                    }
                }
                total
            }
        }
        """).substitute(clusterName="test-cluster")
        )
        expected_json = {"query": expected_query}
        respx_mock.post("/cluster/graphql", json=expected_json).respond(
            status_code=200, json=response_payload
        )
        actions = await fetch_cluster_queue_actions()
        assert len(actions) == 0
        mock_logger.error.assert_called_once()


class TestRemoveQueueAction:
    """Test cases for the remove_queue_action function."""

    @pytest.mark.respx(base_url=backend_client.base_url)
    @pytest.mark.usefixtures("mock_access_token")
    async def test_remove_success(
        self,
        respx_mock: MockRouter,
    ):
        """Test successful removal of a queue action."""
        response_payload = {
            "data": {
                "removeQueueAction": {
                    "__typename": "RemoveQueueActionSuccess",
                    "message": "Queue action removed successfully",
                }
            }
        }

        respx_mock.post("/cluster/graphql").respond(status_code=200, json=response_payload)

        result = await remove_queue_action(123)

        assert result is True

    @pytest.mark.respx(base_url=backend_client.base_url)
    @pytest.mark.usefixtures("mock_access_token")
    async def test_remove_not_found(
        self,
        respx_mock: MockRouter,
    ):
        """Test removal of a queue action that doesn't exist."""
        response_payload = {
            "data": {"removeQueueAction": {"__typename": "InvalidInput", "message": "Queue action not found"}}
        }
        expected_query = dedent("""
        mutation removeQueueAction($id: Int!) {
            removeQueueAction(id: $id) {
                __typename
                ... on RemoveQueueActionSuccess {
                    message
                }
                ... on InvalidInput {
                    message
                }
            }
        }
        """)
        expected_json = {"query": expected_query, "variables": {"id": 999}}
        respx_mock.post("/cluster/graphql", json=expected_json).respond(
            status_code=200, json=response_payload
        )
        result = await remove_queue_action(999)
        assert result is True

    @pytest.mark.respx(base_url=backend_client.base_url)
    @pytest.mark.usefixtures("mock_access_token")
    async def test_remove_with_errors(
        self,
        respx_mock: MockRouter,
        mock_logger: mock.MagicMock,
    ):
        """Test removal when API returns errors."""
        response_payload = {"errors": ["Some API error"]}

        expected_query = dedent("""
        mutation removeQueueAction($id: Int!) {
            removeQueueAction(id: $id) {
                __typename
                ... on RemoveQueueActionSuccess {
                    message
                }
                ... on InvalidInput {
                    message
                }
            }
        }
        """)
        expected_json = {"query": expected_query, "variables": {"id": 123}}
        respx_mock.post("/cluster/graphql", json=expected_json).respond(
            status_code=200, json=response_payload
        )
        result = await remove_queue_action(123)
        assert result is False
        mock_logger.error.assert_called_once()

    @pytest.mark.respx(base_url=backend_client.base_url)
    @pytest.mark.usefixtures("mock_access_token")
    async def test_remove_unexpected_typename(
        self,
        respx_mock: MockRouter,
        mock_logger: mock.MagicMock,
    ):
        """Test removal when API returns an unexpected __typename."""
        response_payload = {
            "data": {"removeQueueAction": {"__typename": "SomeOtherType", "message": "Weird error"}}
        }
        expected_query = dedent("""
        mutation removeQueueAction($id: Int!) {
            removeQueueAction(id: $id) {
                __typename
                ... on RemoveQueueActionSuccess {
                    message
                }
                ... on InvalidInput {
                    message
                }
            }
        }
        """)
        expected_json = {"query": expected_query, "variables": {"id": 123}}
        respx_mock.post("/cluster/graphql", json=expected_json).respond(
            status_code=200, json=response_payload
        )
        result = await remove_queue_action(123)
        assert result is False
        mock_logger.error.assert_called_once_with(
            (
                "Unexpected response when removing queue action 123: "
                "{'__typename': 'SomeOtherType', 'message': 'Weird error'}"
            )
        )


class TestExecuteScancel:
    """Test cases for the execute_scancel function."""

    @pytest.mark.parametrize(
        "job_id, scancel_path",
        [
            ("123", "/usr/bin/scancel"),
            ("456", "/opt/slurm/bin/scancel"),
            ("789", "/usr/local/bin/scancel"),
        ],
    )
    def test_execute_success(
        self,
        job_id: str,
        scancel_path: str,
        mock_settings: mock.MagicMock,
        mock_subprocess_run: mock.MagicMock,
    ):
        """Test successful execution of scancel command."""
        mock_settings.SCANCEL_PATH = scancel_path
        mock_subprocess_run.return_value = mock.MagicMock(returncode=0, stderr="", stdout="")

        result = execute_scancel(job_id)

        assert result is True
        mock_subprocess_run.assert_called_once_with(
            [scancel_path, job_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2
        )

    def test_execute_job_not_found(
        self,
        mock_settings: mock.MagicMock,
        mock_subprocess_run: mock.MagicMock,
        mock_logger: mock.MagicMock,
    ):
        """Test scancel when job doesn't exist."""
        mock_settings.SCANCEL_PATH = "/usr/bin/scancel"
        mock_subprocess_run.return_value = mock.MagicMock(
            returncode=1, stderr="scancel: error: Invalid job id 123", stdout=""
        )

        result = execute_scancel("123")

        assert result is True

    def test_execute_failure(
        self,
        mock_settings: mock.MagicMock,
        mock_subprocess_run: mock.MagicMock,
    ):
        """Test scancel command failure."""
        mock_settings.SCANCEL_PATH = "/usr/bin/scancel"
        mock_subprocess_run.return_value = mock.MagicMock(
            returncode=1, stderr="scancel: error: Some other error", stdout=""
        )

        result = execute_scancel("123")

        assert result is False

    def test_execute_timeout(
        self,
        mock_settings: mock.MagicMock,
        mock_subprocess_run: mock.MagicMock,
    ):
        """Test scancel command timeout."""
        mock_settings.SCANCEL_PATH = "/usr/bin/scancel"
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired("/usr/bin/scancel", 2)

        result = execute_scancel("123")

        assert result is False

    def test_execute_exception(
        self,
        mock_settings: mock.MagicMock,
        mock_subprocess_run: mock.MagicMock,
    ):
        """Test scancel command with general exception."""
        mock_settings.SCANCEL_PATH = "/usr/bin/scancel"
        mock_subprocess_run.side_effect = Exception("Some error")

        result = execute_scancel("123")

        assert result is False


class TestExtractJobIdFromQueueInfo:
    """Test cases for the extract_job_id_from_queue_info function."""

    @pytest.mark.parametrize(
        "queue_info, expected_job_id",
        [
            ({"jobid": "123", "name": "test_job"}, "123"),
            ({"jobid": "456"}, "456"),
            ({"jobid": 789}, "789"),
            ({}, None),
            (None, None),
            ({"no_jobid": "value"}, None),
        ],
    )
    def test_extract_job_id(self, queue_info: dict, expected_job_id: str):
        """Test extracting job ID from various queue info formats."""
        result = extract_job_id_from_queue_info(queue_info)
        assert result == expected_job_id


class TestProcessClusterQueueActions:
    """Test cases for the process_cluster_queue_actions function."""

    def test_process_calls_asyncio_run(
        self,
        mock_asyncio_run: mock.MagicMock,
    ):
        """Test that process_cluster_queue_actions calls asyncio.run with the async function."""
        process_cluster_queue_actions()

        mock_asyncio_run.assert_called_once()
        # Verify the function passed to asyncio.run is the async implementation
        called_args = mock_asyncio_run.call_args[0]
        assert len(called_args) == 1
        # We can't easily check the exact function, but we can verify asyncio.run was called


class TestProcessClusterQueueActionsAsync:
    """Test cases for the _process_cluster_queue_actions_async function."""

    @pytest.fixture
    def mock_fetch_cluster_queue_actions(
        self, monkeypatch: MonkeyPatch
    ) -> Generator[mock.MagicMock, None, None]:
        """Mock the fetch_cluster_queue_actions function."""
        mock_fetch = mock.AsyncMock()
        monkeypatch.setattr("vantage_agent.logicals.queue_actions.fetch_cluster_queue_actions", mock_fetch)
        return mock_fetch

    @pytest.fixture
    def mock_extract_job_id_from_queue_info(
        self, monkeypatch: MonkeyPatch
    ) -> Generator[mock.MagicMock, None, None]:
        """Mock the extract_job_id_from_queue_info function."""
        mock_extract = mock.Mock()
        monkeypatch.setattr(
            "vantage_agent.logicals.queue_actions.extract_job_id_from_queue_info", mock_extract
        )
        return mock_extract

    @pytest.fixture
    def mock_execute_scancel(self, monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
        """Mock the execute_scancel function."""
        mock_execute = mock.Mock()
        monkeypatch.setattr("vantage_agent.logicals.queue_actions.execute_scancel", mock_execute)
        return mock_execute

    @pytest.fixture
    def mock_remove_queue_action(self, monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
        """Mock the remove_queue_action function."""
        mock_remove = mock.AsyncMock()
        monkeypatch.setattr("vantage_agent.logicals.queue_actions.remove_queue_action", mock_remove)
        return mock_remove

    async def test_process_success(
        self,
        mock_fetch_cluster_queue_actions: mock.MagicMock,
        mock_extract_job_id_from_queue_info: mock.MagicMock,
        mock_execute_scancel: mock.MagicMock,
        mock_remove_queue_action: mock.MagicMock,
    ):
        """Test successful processing of cluster queue actions."""
        # Setup mock data
        mock_actions = [
            {
                "node": {
                    "id": 1,
                    "action": "cancel",
                    "queue": {"info": {"jobid": "456"}},
                }
            }
        ]
        mock_fetch_cluster_queue_actions.return_value = mock_actions
        mock_extract_job_id_from_queue_info.return_value = "456"
        mock_execute_scancel.return_value = True

        await _process_cluster_queue_actions_async()

        # Verify function calls
        mock_fetch_cluster_queue_actions.assert_called_once()
        mock_extract_job_id_from_queue_info.assert_called_once_with({"jobid": "456"})
        mock_execute_scancel.assert_called_once_with("456")
        mock_remove_queue_action.assert_not_called()

    async def test_process_no_actions(
        self,
        mock_logger: mock.MagicMock,
        mock_fetch_cluster_queue_actions: mock.MagicMock,
        mock_extract_job_id_from_queue_info: mock.MagicMock,
        mock_execute_scancel: mock.MagicMock,
        mock_remove_queue_action: mock.MagicMock,
    ):
        """Test processing when no actions exist."""
        mock_fetch_cluster_queue_actions.return_value = []

        await _process_cluster_queue_actions_async()

        mock_fetch_cluster_queue_actions.assert_called_once()
        mock_extract_job_id_from_queue_info.assert_not_called()
        mock_execute_scancel.assert_not_called()
        mock_remove_queue_action.assert_not_called()

    async def test_process_unsupported_action(
        self,
        mock_fetch_cluster_queue_actions: mock.MagicMock,
        mock_extract_job_id_from_queue_info: mock.MagicMock,
        mock_execute_scancel: mock.MagicMock,
        mock_remove_queue_action: mock.MagicMock,
    ):
        """Test processing with unsupported action type."""
        mock_actions = [
            {
                "node": {
                    "id": 1,
                    "action": "pause",
                    "queue": {"info": {"jobid": "456"}},
                }
            }
        ]
        mock_fetch_cluster_queue_actions.return_value = mock_actions

        await _process_cluster_queue_actions_async()

        mock_fetch_cluster_queue_actions.assert_called_once()
        mock_extract_job_id_from_queue_info.assert_not_called()
        mock_execute_scancel.assert_not_called()
        mock_remove_queue_action.assert_not_called()

    async def test_process_no_job_id(
        self,
        mock_fetch_cluster_queue_actions: mock.MagicMock,
        mock_extract_job_id_from_queue_info: mock.MagicMock,
        mock_execute_scancel: mock.MagicMock,
        mock_remove_queue_action: mock.MagicMock,
    ):
        """Test processing when job ID cannot be extracted."""
        mock_actions = [
            {
                "node": {
                    "id": 1,
                    "action": "cancel",
                    "queue": {"info": {}},
                }
            }
        ]
        mock_fetch_cluster_queue_actions.return_value = mock_actions
        mock_extract_job_id_from_queue_info.return_value = None

        await _process_cluster_queue_actions_async()

        mock_fetch_cluster_queue_actions.assert_called_once()
        mock_extract_job_id_from_queue_info.assert_called_once_with({})
        mock_execute_scancel.assert_not_called()
        mock_remove_queue_action.assert_called_once_with(1)

    async def test_process_scancel_failure(
        self,
        mock_fetch_cluster_queue_actions: mock.MagicMock,
        mock_extract_job_id_from_queue_info: mock.MagicMock,
        mock_execute_scancel: mock.MagicMock,
        mock_remove_queue_action: mock.MagicMock,
    ):
        """Test processing when scancel fails."""
        mock_actions = [
            {
                "node": {
                    "id": 1,
                    "action": "cancel",
                    "queue": {"info": {"jobid": "456"}},
                }
            }
        ]
        mock_fetch_cluster_queue_actions.return_value = mock_actions
        mock_extract_job_id_from_queue_info.return_value = "456"
        mock_execute_scancel.return_value = False

        await _process_cluster_queue_actions_async()

        mock_fetch_cluster_queue_actions.assert_called_once()
        mock_extract_job_id_from_queue_info.assert_called_once_with({"jobid": "456"})
        mock_execute_scancel.assert_called_once_with("456")
        mock_remove_queue_action.assert_not_called()
