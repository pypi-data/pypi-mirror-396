"""Tests for the asynchronous AsyncQuercleClient."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from quercle import BASE_URL, ENDPOINTS, AsyncQuercleClient
from quercle.exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    QuercleError,
    RateLimitError,
    TimeoutError,
)


class TestAsyncQuercleClientInit:
    """Tests for AsyncQuercleClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Client initializes with explicit API key."""
        client = AsyncQuercleClient(api_key="qk_test")
        assert client.api_key == "qk_test"

    def test_init_with_env_var(self, mock_env_api_key: None, api_key: str) -> None:
        """Client initializes with API key from environment."""
        client = AsyncQuercleClient()
        assert client.api_key == api_key

    def test_init_no_api_key_raises(self) -> None:
        """Client raises error when no API key provided."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(QuercleError) as exc_info:
                AsyncQuercleClient()
            assert exc_info.value.status_code == 401
            assert "API key required" in str(exc_info.value)

    def test_init_custom_timeout(self) -> None:
        """Client accepts custom timeout."""
        client = AsyncQuercleClient(api_key="qk_test", timeout=30.0)
        assert client.timeout == 30.0

    def test_default_values(self) -> None:
        """Client uses default values when not specified."""
        client = AsyncQuercleClient(api_key="qk_test")
        assert client.base_url == BASE_URL
        assert client.timeout == 120.0


class TestAsyncQuercleClientFetch:
    """Tests for AsyncQuercleClient.fetch method."""

    @pytest.mark.asyncio
    async def test_fetch_success(
        self, api_key: str, mock_fetch_response: httpx.Response
    ) -> None:
        """Fetch returns result on success."""
        client = AsyncQuercleClient(api_key=api_key)
        with patch.object(
            client._client, "post", AsyncMock(return_value=mock_fetch_response)
        ):
            result = await client.fetch("https://example.com", "Summarize this")
            assert result == "AI analysis of the page content"
        await client.close()

    @pytest.mark.asyncio
    async def test_fetch_sends_correct_request(self, api_key: str) -> None:
        """Fetch sends correct request body and headers."""
        client = AsyncQuercleClient(api_key=api_key)
        mock_post = AsyncMock(
            return_value=httpx.Response(200, json={"result": "test"}, request=MagicMock())
        )
        with patch.object(client._client, "post", mock_post):
            await client.fetch("https://example.com", "Test prompt")
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args
            assert call_kwargs[0][0] == f"{BASE_URL}{ENDPOINTS['fetch']}"
            assert call_kwargs[1]["json"] == {
                "url": "https://example.com",
                "prompt": "Test prompt",
            }
            assert call_kwargs[1]["headers"]["Authorization"] == f"Bearer {api_key}"
        await client.close()


class TestAsyncQuercleClientSearch:
    """Tests for AsyncQuercleClient.search method."""

    @pytest.mark.asyncio
    async def test_search_success(
        self, api_key: str, mock_search_response: httpx.Response
    ) -> None:
        """Search returns result on success."""
        client = AsyncQuercleClient(api_key=api_key)
        with patch.object(
            client._client, "post", AsyncMock(return_value=mock_search_response)
        ):
            result = await client.search("What is Python?")
            assert "citations" in result
        await client.close()

    @pytest.mark.asyncio
    async def test_search_with_allowed_domains(self, api_key: str) -> None:
        """Search includes allowed_domains in request."""
        client = AsyncQuercleClient(api_key=api_key)
        mock_post = AsyncMock(
            return_value=httpx.Response(200, json={"result": "test"}, request=MagicMock())
        )
        with patch.object(client._client, "post", mock_post):
            await client.search("query", allowed_domains=["example.com"])
            call_kwargs = mock_post.call_args
            assert call_kwargs[1]["json"]["allowed_domains"] == ["example.com"]
        await client.close()

    @pytest.mark.asyncio
    async def test_search_with_blocked_domains(self, api_key: str) -> None:
        """Search includes blocked_domains in request."""
        client = AsyncQuercleClient(api_key=api_key)
        mock_post = AsyncMock(
            return_value=httpx.Response(200, json={"result": "test"}, request=MagicMock())
        )
        with patch.object(client._client, "post", mock_post):
            await client.search("query", blocked_domains=["spam.com"])
            call_kwargs = mock_post.call_args
            assert call_kwargs[1]["json"]["blocked_domains"] == ["spam.com"]
        await client.close()


class TestAsyncQuercleClientErrors:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_401_raises_authentication_error(
        self, api_key: str, mock_error_401: httpx.Response
    ) -> None:
        """401 response raises AuthenticationError."""
        client = AsyncQuercleClient(api_key=api_key)
        with patch.object(
            client._client, "post", AsyncMock(return_value=mock_error_401)
        ):
            with pytest.raises(AuthenticationError) as exc_info:
                await client.fetch("https://example.com", "test")
            assert exc_info.value.status_code == 401
        await client.close()

    @pytest.mark.asyncio
    async def test_402_raises_insufficient_credits_error(
        self, api_key: str, mock_error_402: httpx.Response
    ) -> None:
        """402 response raises InsufficientCreditsError."""
        client = AsyncQuercleClient(api_key=api_key)
        with patch.object(
            client._client, "post", AsyncMock(return_value=mock_error_402)
        ):
            with pytest.raises(InsufficientCreditsError) as exc_info:
                await client.fetch("https://example.com", "test")
            assert exc_info.value.status_code == 402
        await client.close()

    @pytest.mark.asyncio
    async def test_429_raises_rate_limit_error(
        self, api_key: str, mock_error_429: httpx.Response
    ) -> None:
        """429 response raises RateLimitError."""
        client = AsyncQuercleClient(api_key=api_key)
        with patch.object(
            client._client, "post", AsyncMock(return_value=mock_error_429)
        ):
            with pytest.raises(RateLimitError) as exc_info:
                await client.fetch("https://example.com", "test")
            assert exc_info.value.status_code == 429
        await client.close()

    @pytest.mark.asyncio
    async def test_504_raises_timeout_error(
        self, api_key: str, mock_error_504: httpx.Response
    ) -> None:
        """504 response raises TimeoutError."""
        client = AsyncQuercleClient(api_key=api_key)
        with patch.object(
            client._client, "post", AsyncMock(return_value=mock_error_504)
        ):
            with pytest.raises(TimeoutError) as exc_info:
                await client.fetch("https://example.com", "test")
            assert exc_info.value.status_code == 504
        await client.close()


class TestAsyncQuercleClientContextManager:
    """Tests for async context manager support."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self, api_key: str) -> None:
        """Client works as async context manager."""
        async with AsyncQuercleClient(api_key=api_key) as client:
            assert client.api_key == api_key

    @pytest.mark.asyncio
    async def test_async_context_manager_closes_client(self, api_key: str) -> None:
        """Async context manager closes client on exit."""
        client = AsyncQuercleClient(api_key=api_key)
        with patch.object(client, "close", AsyncMock()) as mock_close:
            async with client:
                pass
            mock_close.assert_called_once()
