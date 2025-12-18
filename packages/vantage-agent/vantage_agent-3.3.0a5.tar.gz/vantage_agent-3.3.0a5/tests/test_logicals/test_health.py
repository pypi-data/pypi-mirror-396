"""Core module for testing the vantage_agent/logicals/health.py module.

Copied and adjusted from https://github.com/omnivector-solutions/jobbergate/blob/main/jobbergate-agent/tests/jobbergate/test_report_health.py.
"""

from textwrap import dedent
from unittest import mock

import pytest
from respx.router import MockRouter

from vantage_agent.exceptions import VantageApiError
from vantage_agent.logicals.health import report_health_status
from vantage_agent.vantage_api_client import backend_client


@pytest.mark.respx(base_url=str(backend_client.base_url))
@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "client_id, interval",
    [
        ("test-client-id", 352),
        ("another-test-client-id", 127),
    ],
)
@mock.patch("vantage_agent.logicals.health.SETTINGS")
async def test_report_health_status__success(
    mock_settings: mock.MagicMock, client_id: str, interval: int, respx_mock: MockRouter
):
    """Test that the report_health_status function works as expected."""
    mock_settings.OIDC_CLIENT_ID = client_id
    mock_settings.TASK_JOBS_INTERVAL_SECONDS = interval
    mock_settings.BASE_API_URL = backend_client.base_url

    query = dedent(
        """\
        mutation ($clientId: String!, $interval: Int!) {
            reportAgentHealth(clientId: $clientId, interval: $interval)
        }"""
    )
    body = {"query": query, "variables": {"clientId": client_id, "interval": interval}}

    respx_mock.post("/cluster/graphql", json=body).respond(status_code=200)

    await report_health_status()


@pytest.mark.respx(base_url=str(backend_client.base_url))
@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "client_id, interval",
    [
        ("test-client-id", 981),
        ("another-test-client-id", 7469),
    ],
)
@mock.patch("vantage_agent.logicals.health.SETTINGS")
async def test_report_health_status__failure(
    mock_settings: mock.MagicMock, client_id: str, interval: int, respx_mock: MockRouter
):
    """Test that the report_health_status function raises an exception when the API returns an error."""
    mock_settings.OIDC_CLIENT_ID = client_id
    mock_settings.TASK_JOBS_INTERVAL_SECONDS = interval
    mock_settings.BASE_API_URL = backend_client.base_url

    query = dedent(
        """\
        mutation ($clientId: String!, $interval: Int!) {
            reportAgentHealth(clientId: $clientId, interval: $interval)
        }"""
    )
    body = {"query": query, "variables": {"clientId": client_id, "interval": interval}}

    respx_mock.post("/cluster/graphql", json=body).respond(status_code=500)

    with pytest.raises(VantageApiError):
        await report_health_status()
