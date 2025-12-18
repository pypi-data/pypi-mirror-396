"""Shared base class for sync and async Quercle clients."""

from __future__ import annotations

import os
from typing import Any

import httpx

from quercle.exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    QuercleError,
    RateLimitError,
    TimeoutError,
)

BASE_URL = "https://api.quercle.dev"
ENDPOINTS = {
    "fetch": "/v1/fetch",
    "search": "/v1/search",
}


class BaseQuercleClient:
    """Shared logic for sync and async clients."""

    DEFAULT_TIMEOUT = 120.0  # seconds

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float | None = None,
    ):
        self.api_key = api_key or os.environ.get("QUERCLE_API_KEY")
        if not self.api_key:
            raise QuercleError("API key required. Get one at https://quercle.dev", 401)
        self.base_url = BASE_URL
        self.timeout = timeout or self.DEFAULT_TIMEOUT

    def _build_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _handle_response(self, response: httpx.Response) -> None:
        """Check response status and raise appropriate exception if needed."""
        if response.is_success:
            return

        status_code = response.status_code
        try:
            data = response.json()
            detail = data.get("detail", data.get("message", response.text))
        except Exception:
            detail = response.text

        if status_code == 401:
            raise AuthenticationError(
                "Invalid or missing API key", status_code=status_code, detail=detail
            )
        elif status_code == 402:
            raise InsufficientCreditsError(
                "Insufficient credits", status_code=status_code, detail=detail
            )
        elif status_code == 429:
            raise RateLimitError("Rate limit exceeded", status_code=status_code, detail=detail)
        elif status_code == 504:
            raise TimeoutError("Request timed out", status_code=status_code, detail=detail)
        else:
            raise QuercleError(
                f"Request failed with status {status_code}",
                status_code=status_code,
                detail=detail,
            )

    def _build_search_body(
        self,
        query: str,
        allowed_domains: list[str] | None,
        blocked_domains: list[str] | None,
    ) -> dict[str, Any]:
        """Build request body for search endpoint."""
        body: dict[str, Any] = {"query": query}
        if allowed_domains:
            body["allowed_domains"] = allowed_domains
        if blocked_domains:
            body["blocked_domains"] = blocked_domains
        return body
