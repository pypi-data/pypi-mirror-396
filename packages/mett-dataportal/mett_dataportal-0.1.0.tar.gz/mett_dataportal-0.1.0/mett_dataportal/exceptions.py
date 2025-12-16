"""Custom exception hierarchy for the METT Data Portal client."""

from __future__ import annotations


class DataPortalError(RuntimeError):
    """Base exception for the client."""


class ConfigurationError(DataPortalError):
    """Raised when configuration cannot be loaded or is invalid."""


class APIError(DataPortalError):
    """Raised when the API responds with an error status."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(APIError):
    """Raised when authentication fails (401/403)."""
