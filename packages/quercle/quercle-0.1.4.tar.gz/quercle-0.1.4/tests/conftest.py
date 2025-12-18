"""Shared pytest fixtures for Quercle client tests."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import patch

import httpx
import pytest

from quercle import BASE_URL


@pytest.fixture
def api_key() -> str:
    """Test API key."""
    return "qk_test_key_123"


@pytest.fixture
def mock_env_api_key(api_key: str) -> Generator[None, None, None]:
    """Mock QUERCLE_API_KEY environment variable."""
    with patch.dict("os.environ", {"QUERCLE_API_KEY": api_key}):
        yield


def create_mock_response(
    status_code: int = 200,
    json_data: dict[str, Any] | None = None,
    text: str = "",
) -> httpx.Response:
    """Create a mock httpx.Response."""
    if json_data is None:
        json_data = {"result": "Test result"}

    request = httpx.Request("POST", f"{BASE_URL}/v1/test")
    response = httpx.Response(
        status_code=status_code,
        json=json_data,
        request=request,
    )
    return response


@pytest.fixture
def mock_fetch_response() -> httpx.Response:
    """Mock successful fetch response."""
    return create_mock_response(json_data={"result": "AI analysis of the page content"})


@pytest.fixture
def mock_search_response() -> httpx.Response:
    """Mock successful search response."""
    return create_mock_response(
        json_data={"result": "Search results with [1] citations.\n\nSources:\n[1] Example - URL"}
    )


@pytest.fixture
def mock_error_401() -> httpx.Response:
    """Mock 401 authentication error response."""
    return create_mock_response(
        status_code=401,
        json_data={"detail": "Invalid API key"},
    )


@pytest.fixture
def mock_error_402() -> httpx.Response:
    """Mock 402 insufficient credits response."""
    return create_mock_response(
        status_code=402,
        json_data={"detail": "Insufficient credits"},
    )


@pytest.fixture
def mock_error_429() -> httpx.Response:
    """Mock 429 rate limit response."""
    return create_mock_response(
        status_code=429,
        json_data={"detail": "Rate limit exceeded"},
    )


@pytest.fixture
def mock_error_504() -> httpx.Response:
    """Mock 504 timeout response."""
    return create_mock_response(
        status_code=504,
        json_data={"detail": "Request timed out"},
    )
