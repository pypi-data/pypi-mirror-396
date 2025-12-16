"""
Custom exceptions for JustStorage SDK.
"""

from typing import Optional


class JustStorageError(Exception):
    """Base exception for all JustStorage errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class JustStorageAPIError(JustStorageError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: Optional[str] = None,
        details: Optional[str] = None,
    ):
        super().__init__(message, status_code)
        self.error_code = error_code
        self.details = details


class JustStorageNotFoundError(JustStorageAPIError):
    """Raised when a requested object is not found (404)."""

    def __init__(self, message: str = "Object not found", details: Optional[str] = None):
        super().__init__(message, 404, "NOT_FOUND", details)


class JustStorageUnauthorizedError(JustStorageAPIError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401, "UNAUTHORIZED")


class JustStorageConflictError(JustStorageAPIError):
    """Raised when there's a conflict (e.g., duplicate key) (409)."""

    def __init__(self, message: str = "Conflict", details: Optional[str] = None):
        super().__init__(message, 409, "CONFLICT", details)


class JustStorageBadRequestError(JustStorageAPIError):
    """Raised when the request is invalid (400)."""

    def __init__(self, message: str = "Bad request", details: Optional[str] = None):
        super().__init__(message, 400, "BAD_REQUEST", details)
