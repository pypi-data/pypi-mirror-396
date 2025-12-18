"""Pytest configuration file."""

from datetime import datetime, timezone
from typing import AsyncGenerator

import pytest
import respx
from jose.jwt import encode

from vantage_agent.settings import SETTINGS


@pytest.fixture()
def token_content() -> str:
    """Generate a dummy token content."""
    one_minute_from_now = int(datetime.now(tz=timezone.utc).timestamp()) + 60
    return encode(dict(exp=one_minute_from_now), key="dummy-key", algorithm="HS256")


@pytest.fixture()
async def mock_access_token(token_content) -> AsyncGenerator[None, None]:
    """Fixture to mock the access token."""
    async with respx.mock:
        respx.post(f"https://{SETTINGS.OIDC_DOMAIN}/protocol/openid-connect/token").respond(
            status_code=200,
            json=dict(access_token=token_content),
        )
        yield
