"""Exception classes for the Quercle API client."""


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
