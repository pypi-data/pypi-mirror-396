"""Quercle Python SDK - AI-powered web search and fetching."""

from quercle._base import BASE_URL, ENDPOINTS
from quercle.async_client import AsyncQuercleClient
from quercle.client import QuercleClient
from quercle.descriptions import (
    FETCH_PROMPT_DESCRIPTION,
    FETCH_TOOL_DESCRIPTION,
    FETCH_URL_DESCRIPTION,
    SEARCH_ALLOWED_DOMAINS_DESCRIPTION,
    SEARCH_BLOCKED_DOMAINS_DESCRIPTION,
    SEARCH_QUERY_DESCRIPTION,
    SEARCH_TOOL_DESCRIPTION,
)
from quercle.exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    QuercleError,
    RateLimitError,
    TimeoutError,
)

__all__ = [
    # Constants
    "BASE_URL",
    "ENDPOINTS",
    # Clients
    "QuercleClient",
    "AsyncQuercleClient",
    # Exceptions
    "QuercleError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "RateLimitError",
    "TimeoutError",
    # Descriptions
    "FETCH_TOOL_DESCRIPTION",
    "FETCH_URL_DESCRIPTION",
    "FETCH_PROMPT_DESCRIPTION",
    "SEARCH_TOOL_DESCRIPTION",
    "SEARCH_QUERY_DESCRIPTION",
    "SEARCH_ALLOWED_DOMAINS_DESCRIPTION",
    "SEARCH_BLOCKED_DOMAINS_DESCRIPTION",
]
