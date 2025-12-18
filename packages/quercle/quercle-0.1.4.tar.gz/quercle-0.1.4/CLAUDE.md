# CLAUDE.md - Quercle Python SDK

## Project Overview

Official Python SDK for the Quercle API. Provides both **synchronous** and **asynchronous** clients for AI-powered web search and URL fetching.

This is the core library that framework integrations (LangChain, CrewAI, LlamaIndex, etc.) depend on.

## Development Guidelines

**IMPORTANT:**
- Always use the **latest stable versions** of all dependencies
- Use **`uv`** for Python package management (NOT pip)
- Use modern Python patterns, type hints, and async/await
- Check PyPI for current versions before specifying dependencies
- Keep sync and async implementations DRY (shared logic, thin wrappers)

## Quercle API

### Authentication
- Header: `X-API-Key: qk_...`
- Env var: `QUERCLE_API_KEY`
- Get API key at: https://quercle.dev

### Endpoints

**POST https://api.quercle.dev/v1/fetch**

Fetch a web page and analyze its content using AI. Provide a URL and a prompt describing what information you want to extract or how to analyze the content. The raw HTML is NOT returned - only the AI's analysis based on your prompt.

```json
// Request
{
  "url": "https://example.com",
  "prompt": "Summarize the main points of this page"
}
// Response
{"result": "AI-processed content..."}
```

**POST https://api.quercle.dev/v1/search**

Search the web and get an AI-synthesized answer with citations. The response includes the answer and source URLs that can be fetched for further investigation. Optionally filter by allowed or blocked domains.

```json
// Request
{
  "query": "What is TypeScript?",
  "allowed_domains": ["*.edu", "*.gov"],  // optional
  "blocked_domains": ["spam.com"]         // optional
}
// Response
{"result": "Synthesized answer with [1] citations...\n\nSources:\n[1] Title - URL"}
```

### Error Codes
- `400` - Invalid request (bad URL, empty prompt)
- `401` - Invalid or missing API key
- `402` - Insufficient credits
- `403` - Account inactive
- `404` - Resource not found
- `504` - Request timeout

## Package Structure

```
quercle/
├── __init__.py          # Exports QuercleClient, AsyncQuercleClient, QuercleError
├── client.py            # Sync client implementation
├── async_client.py      # Async client implementation
├── _base.py             # Shared logic (DRY - both clients use this)
├── types.py             # Type definitions, response models
├── exceptions.py        # QuercleError and specific exceptions
└── py.typed             # PEP 561 marker
tests/
├── test_client.py       # Sync client tests
├── test_async_client.py # Async client tests
└── conftest.py          # Shared fixtures
pyproject.toml
README.md
LICENSE                  # MIT
.github/
└── workflows/
    └── publish.yml      # Auto-publish to PyPI on merge to master
```

## Implementation Details

### Shared Base (DRY Pattern)

```python
# quercle/_base.py
from typing import Any

class BaseQuercleClient:
    """Shared logic for sync and async clients."""

    BASE_URL = "https://quercle.dev"
    DEFAULT_TIMEOUT = 120.0  # seconds

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float | None = None,
    ):
        self.api_key = api_key or os.environ.get("QUERCLE_API_KEY")
        if not self.api_key:
            raise QuercleError("API key required. Get one at https://quercle.dev", 401)
        self.base_url = self.BASE_URL
        self.timeout = timeout or self.DEFAULT_TIMEOUT

    def _build_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    def _handle_error(self, status_code: int, detail: str) -> None:
        """Raise appropriate exception based on status code."""
        # Shared error handling logic
        ...
```

### Sync Client

```python
# quercle/client.py
import httpx
from quercle._base import BaseQuercleClient

class QuercleClient(BaseQuercleClient):
    """Synchronous Quercle API client."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = httpx.Client(timeout=self.timeout)

    def fetch(self, url: str, prompt: str) -> str:
        """Fetch a URL and analyze with AI.

        Args:
            url: The URL to fetch and analyze
            prompt: Instructions for how to analyze the page content.
                   Be specific about what information you want to extract.

        Returns:
            AI-processed analysis of the page content
        """
        response = self._client.post(
            f"{self.base_url}/v1/fetch",
            headers=self._build_headers(),
            json={"url": url, "prompt": prompt},
        )
        self._handle_response(response)
        return response.json()["result"]

    def search(
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
        body = {"query": query}
        if allowed_domains:
            body["allowed_domains"] = allowed_domains
        if blocked_domains:
            body["blocked_domains"] = blocked_domains

        response = self._client.post(
            f"{self.base_url}/v1/search",
            headers=self._build_headers(),
            json=body,
        )
        self._handle_response(response)
        return response.json()["result"]

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
```

### Async Client

```python
# quercle/async_client.py
import httpx
from quercle._base import BaseQuercleClient

class AsyncQuercleClient(BaseQuercleClient):
    """Asynchronous Quercle API client."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def fetch(self, url: str, prompt: str) -> str:
        """Fetch a URL and analyze with AI (async)."""
        response = await self._client.post(
            f"{self.base_url}/v1/fetch",
            headers=self._build_headers(),
            json={"url": url, "prompt": prompt},
        )
        self._handle_response(response)
        return response.json()["result"]

    async def search(
        self,
        query: str,
        *,
        allowed_domains: list[str] | None = None,
        blocked_domains: list[str] | None = None,
    ) -> str:
        """Search the web and get AI-synthesized answers (async)."""
        body = {"query": query}
        if allowed_domains:
            body["allowed_domains"] = allowed_domains
        if blocked_domains:
            body["blocked_domains"] = blocked_domains

        response = await self._client.post(
            f"{self.base_url}/v1/search",
            headers=self._build_headers(),
            json=body,
        )
        self._handle_response(response)
        return response.json()["result"]

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
```

### Exceptions

```python
# quercle/exceptions.py
class QuercleError(Exception):
    """Base exception for Quercle API errors."""

    def __init__(self, message: str, status_code: int, detail: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail

class AuthenticationError(QuercleError):
    """Invalid or missing API key (401)."""
    pass

class InsufficientCreditsError(QuercleError):
    """Not enough credits (402)."""
    pass

class RateLimitError(QuercleError):
    """Too many requests (429)."""
    pass

class TimeoutError(QuercleError):
    """Request timed out (504)."""
    pass
```

## Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=quercle

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy quercle

# Build package
uv build

# Publish to PyPI (manual)
uv publish
```

## Dependencies

- Python 3.10+
- httpx (HTTP client with async support)
- pydantic (optional, for response validation)

## pyproject.toml

```toml
[project]
name = "quercle"
version = "0.1.0"
description = "Official Python SDK for the Quercle API - AI-powered web search and fetching"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.10"
authors = [{ name = "Quercle", email = "support@quercle.dev" }]
keywords = ["quercle", "api", "ai", "search", "web", "fetch"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Typing :: Typed",
]
dependencies = [
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.4.0",
    "mypy>=1.10.0",
]

[project.urls]
Homepage = "https://quercle.dev"
Documentation = "https://quercle.dev/docs"
Repository = "https://github.com/quercledev/quercle-python"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Usage Examples

### Sync Client

```python
from quercle import QuercleClient

# Using environment variable QUERCLE_API_KEY
client = QuercleClient()

# Or explicit API key
client = QuercleClient(api_key="qk_...")

# Fetch and analyze a URL
result = client.fetch(
    url="https://example.com/article",
    prompt="Summarize the main points in bullet points"
)
print(result)

# Search the web
result = client.search("What is TypeScript?")
print(result)

# Search with domain filtering
result = client.search(
    "Python best practices",
    allowed_domains=["*.python.org", "realpython.com"]
)

# Context manager
with QuercleClient() as client:
    result = client.fetch("https://example.com", "Extract the title")
```

### Async Client

```python
import asyncio
from quercle import AsyncQuercleClient

async def main():
    async with AsyncQuercleClient() as client:
        # Fetch
        result = await client.fetch(
            url="https://example.com",
            prompt="Summarize this page"
        )
        print(result)

        # Search
        result = await client.search("Latest AI news")
        print(result)

        # Parallel requests
        results = await asyncio.gather(
            client.search("Python tutorials"),
            client.search("TypeScript tutorials"),
        )
        for r in results:
            print(r)

asyncio.run(main())
```

## CI/CD - Auto-publish to PyPI

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    branches: [master]
    paths:
      - 'quercle/**'
      - 'pyproject.toml'

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for trusted publishing

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run tests
        run: uv run pytest

      - name: Run lints
        run: |
          uv run ruff check .
          uv run mypy quercle

      - name: Build package
        run: uv build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # Uses trusted publishing - configure in PyPI project settings
```

## Publishing Setup

1. Create PyPI account at https://pypi.org
2. Create project `quercle`
3. Go to project settings → "Publishing" → "Add a new pending publisher"
4. Configure:
   - Owner: `quercledev`
   - Repository: `quercle-python`
   - Workflow: `publish.yml`
   - Environment: (leave blank)

Package name on PyPI: `quercle`
