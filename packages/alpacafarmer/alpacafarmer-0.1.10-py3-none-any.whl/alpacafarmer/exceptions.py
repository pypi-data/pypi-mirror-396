"""Custom exceptions for AlpacaFarmer API wrapper."""

from __future__ import annotations


class AlpacaError(Exception):
    """Base exception for all Alpaca API errors."""

    def __init__(self, message: str = "An error occurred with the Alpaca API") -> None:
        self.message = message
        super().__init__(self.message)


class APIError(AlpacaError):
    """HTTP API error with status code and response details."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: dict | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body or {}
        super().__init__(message)

    def __str__(self) -> str:
        return f"[{self.status_code}] {self.message}"


class AuthenticationError(AlpacaError):
    """Invalid or missing API credentials."""

    def __init__(
        self, message: str = "Authentication failed. Check your API credentials."
    ) -> None:
        super().__init__(message)


class RateLimitError(AlpacaError):
    """API rate limit exceeded."""

    def __init__(
        self,
        message: str = "API rate limit exceeded. Please retry later.",
        retry_after: int | None = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message)


class ValidationError(AlpacaError):
    """Request validation failed."""

    def __init__(
        self,
        message: str = "Request validation failed.",
        errors: list[dict] | None = None,
    ) -> None:
        self.errors = errors or []
        super().__init__(message)