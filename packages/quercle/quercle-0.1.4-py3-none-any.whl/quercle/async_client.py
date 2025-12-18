"""Asynchronous Quercle API client."""

from __future__ import annotations

from types import TracebackType

import httpx

from quercle._base import ENDPOINTS, BaseQuercleClient


class AsyncQuercleClient(BaseQuercleClient):
    """Asynchronous Quercle API client."""

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float | None = None,
    ):
        super().__init__(api_key=api_key, timeout=timeout)
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def fetch(self, url: str, prompt: str) -> str:
        """Fetch a URL and analyze with AI.

        Args:
            url: The URL to fetch and analyze
            prompt: Instructions for how to analyze the page content.
                   Be specific about what information you want to extract.

        Returns:
            AI-processed analysis of the page content
        """
        response = await self._client.post(
            f"{self.base_url}{ENDPOINTS['fetch']}",
            headers=self._build_headers(),
            json={"url": url, "prompt": prompt},
        )
        self._handle_response(response)
        result: str = response.json()["result"]
        return result

    async def search(
        self,
        query: str,
        *,
        allowed_domains: list[str] | None = None,
        blocked_domains: list[str] | None = None,
    ) -> str:
        """Search the web and get AI-synthesized answers.

        Args:
            query: The search query to find information about. Be specific.
            allowed_domains: Only include results from these domains
                            (e.g., ['example.com', '*.example.org'])
            blocked_domains: Exclude results from these domains
                            (e.g., ['example.com', '*.example.org'])

        Returns:
            AI-synthesized answer with source citations
        """
        body = self._build_search_body(query, allowed_domains, blocked_domains)
        response = await self._client.post(
            f"{self.base_url}{ENDPOINTS['search']}",
            headers=self._build_headers(),
            json=body,
        )
        self._handle_response(response)
        result: str = response.json()["result"]
        return result

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncQuercleClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()
