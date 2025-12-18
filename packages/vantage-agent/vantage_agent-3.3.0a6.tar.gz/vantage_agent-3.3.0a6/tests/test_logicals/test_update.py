"""Tests for the vantage_agent/logicals/update module.

Copied and adjusted from https://github.com/omnivector-solutions/jobbergate/blob/main/jobbergate-agent/tests/internals/test_update.py.
"""

from unittest import mock

import httpx
import pytest
import respx

from vantage_agent.logicals.update import (
    _fetch_upstream_version_info,
    _need_update,
    _update_package,
    self_update_agent,
)
from vantage_agent.settings import SETTINGS


@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize("upstream_version", ["1.0.0", "1.0.1", "1.1.0", "2.0.0"])
async def test__fetch_upstream_version_info__success(upstream_version: str):
    """Test that _fetch_upstream_version_info returns the expected result."""
    respx.get(f"{SETTINGS.BASE_API_URL}/cluster/openapi.json").respond(
        status_code=200, json={"info": {"version": upstream_version}}
    )

    assert await _fetch_upstream_version_info() == upstream_version


@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize("http_code", [404, 500])
async def test__fetch_upstream_version_info__check_http_error(http_code: int):
    """Test that _fetch_upstream_version_info raises error on HTTP error."""
    with pytest.raises(httpx.HTTPStatusError):
        respx.get(f"{SETTINGS.BASE_API_URL}/cluster/openapi.json").respond(status_code=http_code)

        await _fetch_upstream_version_info()


@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "current_version, upstream_version, expected_result",
    [
        ("1.0.0", "1.0.0", False),  # Same version
        ("1.0.0", "2.0.0", False),  # Different major version
        ("1.0.9a1", "2.1.0", False),  # Different major not allowed even for alpha updates
        ("1.0.0", "1.1.0", True),  # Minor version update available
        ("1.0.0", "1.0.1", True),  # Patch version update available
        ("2.0.0", "1.0.0", False),  # Major version rollback
        ("1.2.0", "1.1.0", True),  # Minor version rollback
        ("1.0.1", "1.0.0", True),  # Patch version rollback
        ("1.0.9a1", "1.0.9a2", True),  # Alpha version available
        ("1.0.9a1", "1.0.9", True),  # Alpha version update to stable
        ("1.0.9a1", "1.1.0", True),  # Alpha version update to stable
        ("1.0.9a1", "1.0.8", False),  # Alpha rollback not allowed
        ("1.0.9a1", "1.1.0a1", False),  # Alpha to alpha not allowed if minor is different
        ("1.0.9a1", "1.1.0-alpha.1", False),  # Alpha to alpha not allowed if minor is different
        ("2.3.9a1", "2.3.9-alpha.2", True),  # Check other format
        ("1.2.10a1", "1.2.10-alpha2", True),  # Other upstream format
        ("1.2.10-alpha.6", "1.2.10a5", False),  # Current in another format
    ],
)
def test_need_update(current_version: str, upstream_version: str, expected_result: bool):
    """Test that _need_update returns the expected result."""
    assert _need_update(current_version, upstream_version) is expected_result


@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "current_version, upstream_version",
    [
        ("1.0", "1.0.1"),  # Improperly formatted current version
        ("1.0.0", "1.0"),  # Improperly formatted upstream version
        ("1", "2"),  # Major version with no minor/patch
        ("1.0.1a", "1.1.0"),  # Pre-release improperly formatted
        ("1.0.1", "1.0.10b"),  # Pre-release improperly formatted
        ("1.1.1", "1.1.1alpha2"),  # Upstream alpha improperly formatted
    ],
)
def test_need_update__check_improperly_formatted_versions(
    current_version: str,
    upstream_version: str,
):
    """Test that _need_update raises error on improperly formatted versions."""
    with pytest.raises(ValueError):
        _need_update(current_version, upstream_version)


@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "version, executable",
    [
        ("1.0.0", "/dummy/foo"),
        ("1.0.1", "/dummy/bar"),
        ("1.1.0", "/dummy/baz"),
        ("2.0.0", "/dummy/qux"),
    ],
)
@mock.patch("vantage_agent.logicals.update.subprocess")
@mock.patch("vantage_agent.logicals.update.sys")
def test_update_package(
    mocked_sys: mock.MagicMock, mocked_subprocess: mock.MagicMock, version: str, executable: str
):
    """Test that _update_package runs without error."""
    mocked_subprocess.check_call.return_value = None
    mocked_sys.executable = executable

    _update_package(version)

    mocked_subprocess.check_call.assert_called_once_with(
        [executable, "-m", "pip", "install", "--upgrade", f"vantage_agent=={version}"]
    )


@pytest.mark.usefixtures("mock_access_token")
@pytest.mark.parametrize(
    "current_version, upstream_version, is_update_available",
    [
        ("1.0.0", "1.0.0", False),  # Same version
        ("1.0.0", "2.0.0", False),  # Different major version
        ("1.0.0", "1.1.0", True),  # Minor version update available
        ("1.0.0", "1.0.1", True),  # Patch version update available
        ("2.0.0", "1.0.0", False),  # Major version rollback
        ("1.2.0", "1.1.0", True),  # Minor version rollback
        ("1.0.1", "1.0.0", True),  # Patch version rollback
    ],
)
@mock.patch("vantage_agent.logicals.update._fetch_upstream_version_info", new_callable=mock.AsyncMock)
@mock.patch("vantage_agent.logicals.update._update_package")
@mock.patch("vantage_agent.logicals.update.version")
@mock.patch("vantage_agent.logicals.update._need_update")
@mock.patch("vantage_agent.logicals.update.scheduler")
@mock.patch("vantage_agent.logicals.update.schedule_tasks")
async def test_self_update_agent(
    mocked_schedule_tasks: mock.MagicMock,
    mocked_scheduler: mock.MagicMock,
    mocked_need_update: mock.MagicMock,
    mocked_version: mock.MagicMock,
    mocked_update_package: mock.MagicMock,
    mocked_fetch_upstream_version_info: mock.AsyncMock,
    current_version: str,
    upstream_version: str,
    is_update_available: bool,
):
    """Test that self_update_agent runs without error the expected logic.

    If an update is available, it is expected that the scheduler is shutdown
    and then restarted with the new version after the package update is done.
    """
    mocked_version.return_value = current_version
    mocked_fetch_upstream_version_info.return_value = upstream_version
    mocked_need_update.return_value = is_update_available

    mocked_job = mock.Mock()
    mocked_job.remove = mock.Mock()
    mocked_scheduler.pause = mock.Mock()
    mocked_scheduler.resume = mock.Mock()
    mocked_scheduler.get_jobs = mock.Mock()
    mocked_scheduler.get_jobs.return_value = [mocked_job]

    await self_update_agent()

    mocked_version.assert_called_once_with("vantage_agent")
    mocked_fetch_upstream_version_info.assert_called_once_with()
    mocked_need_update.assert_called_once_with(current_version, upstream_version)
    if is_update_available:
        mocked_scheduler.pause.assert_called_once_with()
        mocked_scheduler.resume.assert_called_once_with()
        mocked_scheduler.get_jobs.assert_called_once_with()
        mocked_update_package.assert_called_once_with(upstream_version)
        mocked_schedule_tasks.assert_called_once_with(mocked_scheduler)
        mocked_job.remove.assert_called_once_with()
    else:
        mocked_scheduler.pause.assert_not_called()
        mocked_scheduler.resume.assert_not_called()
        mocked_scheduler.get_jobs.assert_not_called()
        mocked_update_package.assert_not_called()
        mocked_schedule_tasks.assert_not_called()
        mocked_job.remove.assert_not_called()
