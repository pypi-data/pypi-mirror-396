"""Core module for testing the vantage_agent/logicals/vantage_api.py module."""

from textwrap import dedent
from typing import Generator
from unittest import mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from respx.router import MockRouter

from vantage_agent.logicals.vantage_api import (
    clean_slurm_nodes,
    clean_slurm_partitions,
    upload_slurm_config,
    upload_slurm_nodes,
    upload_slurm_partitions,
    upload_slurm_queue,
)
from vantage_agent.vantage_api_client import backend_client


@pytest.fixture
def mock_logger(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the logger."""
    mock_logger = mock.Mock()
    monkeypatch.setattr("vantage_agent.logicals.vantage_api.logger", mock_logger)
    return mock_logger


@pytest.fixture
def mock_settings(monkeypatch: MonkeyPatch) -> Generator[mock.MagicMock, None, None]:
    """Mock the settings."""
    mock_settings = mock.Mock()
    monkeypatch.setattr("vantage_agent.logicals.vantage_api.SETTINGS", mock_settings)
    return mock_settings


@pytest.mark.respx(base_url=backend_client.base_url)
@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "client_id, slurm_config",
    [
        ("madrid", {"bangkok": "bali"}),
        ("barcelona", {"cancun": "nairobi"}),
        ("valencia", {"helsinki": "copenhagen"}),
    ],
)
async def test_upload_slurm_config(
    client_id: str,
    slurm_config: dict[str, str],
    respx_mock: MockRouter,
    mock_settings: mock.MagicMock,
    mock_logger: mock.MagicMock,
):
    """Test if the upload_slurm_config send the proper GraphQL query to the Vantage API."""
    mock_settings.OIDC_CLIENT_ID = client_id
    mock_settings.BASE_API_URL = backend_client.base_url

    response_payload = {
        "data": {"UploadSlurmConfigSuccess": {"message": "Slurm config uploaded successfully"}}
    }

    query = dedent(
        """
        mutation($config: JSONScalar!, $clientId: String!) {
            uploadSlurmConfig(config: $config, clientId: $clientId) {
                ... on UploadSlurmConfigSuccess {
                    message
                }
            }
        }
        """
    )
    body = {"query": query, "variables": {"config": slurm_config, "clientId": client_id}}

    respx_mock.post("/cluster/graphql", json=body).respond(status_code=200, json=response_payload)

    await upload_slurm_config(slurm_config)

    mock_logger.debug.assert_any_call(
        f"Response from Vantage API while uploading Slurm's configurations: {response_payload}"
    )


@pytest.mark.respx(base_url=backend_client.base_url)
@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "client_id, slurm_nodes",
    [
        ("tokyo", {"berlin": "frankfurt"}),
        ("istanbul", {"cape town": "cairo"}),
        ("mumbai", {"santiago": "paris"}),
    ],
)
async def test_upload_slurm_nodes(
    client_id: str,
    slurm_nodes: dict[str, str],
    respx_mock: MockRouter,
    mock_settings: mock.MagicMock,
    mock_logger: mock.MagicMock,
):
    """Test if the upload_slurm_nodes send the proper GraphQL query to the Vantage API."""
    mock_settings.OIDC_CLIENT_ID = client_id
    mock_settings.BASE_API_URL = backend_client.base_url

    response_payload = {"data": {"UploadSlurmNodesSuccess": {"message": "Slurm nodes uploaded successfully"}}}

    query = dedent(
        """
        mutation($nodes: JSONScalar!, $clientId: String!) {
            uploadSlurmNodes(nodes: $nodes, clientId: $clientId) {
                ... on UploadSlurmNodesSuccess {
                    message
                }
            }
        }
        """
    )
    body = {"query": query, "variables": {"nodes": slurm_nodes, "clientId": client_id}}

    respx_mock.post("/cluster/graphql", json=body).respond(status_code=200, json=response_payload)

    await upload_slurm_nodes(slurm_nodes)

    mock_logger.debug.assert_any_call(f"Response from Vantage API while uploading nodes: {response_payload}")


@pytest.mark.respx(base_url=backend_client.base_url)
@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "client_id, slurm_partitions",
    [
        ("amsterdam", {"stockholm": "jakarta"}),
        ("lagos", {"new delhi": "seoul"}),
        ("lima", {"los angeles": "kolkata"}),
    ],
)
async def test_upload_slurm_partitions(
    client_id: str,
    slurm_partitions: dict[str, str],
    respx_mock: MockRouter,
    mock_settings: mock.MagicMock,
    mock_logger: mock.MagicMock,
):
    """Test if the upload_slurm_partitions send the proper GraphQL query to the Vantage API."""
    mock_settings.OIDC_CLIENT_ID = client_id
    mock_settings.BASE_API_URL = backend_client.base_url

    response_payload = {"data": {"uploadSlurmPartitions": {"message": "Slurm config uploaded successfully"}}}

    query = dedent(
        """
        mutation($partitions: JSONScalar!, $clientId: String!) {
            uploadSlurmPartitions(partitions: $partitions, clientId: $clientId) {
                ... on UploadSlurmPartitionsSuccess {
                    message
                }
            }
        }
        """
    )
    body = {"query": query, "variables": {"partitions": slurm_partitions, "clientId": client_id}}

    respx_mock.post("/cluster/graphql", json=body).respond(status_code=200, json=response_payload)

    await upload_slurm_partitions(slurm_partitions)

    mock_logger.debug.assert_any_call(
        f"Response from Vantage API while uploading partitions: {response_payload}"
    )


@pytest.mark.respx(base_url=backend_client.base_url)
@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "client_id, slurm_partitions",
    [
        ("ancara", ["partition1", "partition2"]),
        ("manaus", ["partition3"]),
    ],
)
async def test_clean_slurm_partitions(
    client_id: str,
    slurm_partitions: list[str],
    respx_mock: MockRouter,
    mock_settings: mock.MagicMock,
    mock_logger: mock.MagicMock,
):
    """Test if clean_slurm_partitions sends the proper GraphQL query."""
    mock_settings.OIDC_CLIENT_ID = client_id
    mock_settings.BASE_API_URL = backend_client.base_url

    response_payload = {
        "data": {"CleanSlurmPartitionsSuccess": {"message": "Slurm partitions cleaned successfully"}}
    }

    query = dedent(
        """
        mutation($partitions: [String!]!, $clientId: String!) {
            cleanSlurmPartitions(partitions: $partitions, clientId: $clientId) {
                ... on CleanSlurmPartitionsSuccess {
                    message
                }
            }
        }
        """
    )
    body = {"query": query, "variables": {"partitions": slurm_partitions, "clientId": client_id}}

    respx_mock.post("/cluster/graphql", json=body).respond(status_code=200, json=response_payload)

    await clean_slurm_partitions(slurm_partitions)

    mock_logger.debug.assert_any_call(
        f"Response from Vantage API while cleaning partitions: {response_payload}"
    )


@pytest.mark.respx(base_url=backend_client.base_url)
@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "client_id, slurm_nodes",
    [
        ("quito", ["node1", "node2"]),
        ("caracas", ["node3"]),
    ],
)
async def test_clean_slurm_nodes(
    client_id: str,
    slurm_nodes: list[str],
    respx_mock: MockRouter,
    mock_settings: mock.MagicMock,
    mock_logger: mock.MagicMock,
):
    """Test if clean_slurm_nodes sends the proper GraphQL query."""
    mock_settings.OIDC_CLIENT_ID = client_id
    mock_settings.BASE_API_URL = backend_client.base_url

    response_payload = {"data": {"CleanSlurmNodesSuccess": {"message": "Slurm nodes cleaned successfully"}}}

    query = dedent(
        """
        mutation($nodes: [String!]!, $clientId: String!) {
            cleanSlurmNodes(nodes: $nodes, clientId: $clientId) {
                ... on CleanSlurmNodesSuccess {
                    message
                }
            }
        }
        """
    )
    body = {"query": query, "variables": {"nodes": slurm_nodes, "clientId": client_id}}

    respx_mock.post("/cluster/graphql", json=body).respond(status_code=200, json=response_payload)

    await clean_slurm_nodes(slurm_nodes)

    mock_logger.debug.assert_any_call(f"Response from Vantage API while cleaning nodes: {response_payload}")


@pytest.mark.respx(base_url=backend_client.base_url)
@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "client_id, slurm_queue",
    [
        (
            "clusterA-39bb8c7a-f882-4374-93ad-762d65ed06a1",
            [{"name": "job-test", "state": "CONFIGURING"}, {"name": "job1", "state": "RUNNING"}],
        ),
        ("clusterB-39bb8c7a-f882-4374-93ad-762d65ed06a1", [{"name": "second-job", "state": "PENDING"}]),
    ],
)
async def test_upload_slurm_queue(
    client_id: str,
    slurm_queue: list[dict[str, str]],
    respx_mock: MockRouter,
    mock_settings: mock.MagicMock,
    mock_logger: mock.MagicMock,
):
    """Test if the upload_slurm_queue send the proper GraphQL query to the Vantage API."""
    mock_settings.OIDC_CLIENT_ID = client_id
    mock_settings.BASE_API_URL = backend_client.base_url

    response_payload = {"data": {"uploadSlurmQueue": {"message": "Slurm queue uploaded successfully"}}}

    query = dedent(
        """
        mutation($queue: JSONScalar!, $clientId: String!) {
            uploadSlurmQueue(queue: $queue, clientId: $clientId) {
                ... on UploadSlurmQueueSuccess {
                    message
                }
            }
        }
        """
    )
    body = {"query": query, "variables": {"queue": slurm_queue, "clientId": client_id}}

    respx_mock.post("/cluster/graphql", json=body).respond(status_code=200, json=response_payload)

    await upload_slurm_queue(slurm_queue)

    mock_logger.debug.assert_any_call(f"Response from Vantage API while uploading queue: {response_payload}")
