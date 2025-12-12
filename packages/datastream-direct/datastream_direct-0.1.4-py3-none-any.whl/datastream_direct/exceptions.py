"""
Exception classes for the DataStream Direct Python client.
"""

from typing import Optional
from .models import HttpStatus


class DataStreamDirectError(Exception):
    """
    Base exception class for all DataStream Direct errors.

    All exceptions raised by the DataStream Direct client inherit from this class.

    Args:
        message: Human-readable error description
        error_code: Optional error code from the API

    Attributes:
        message: The error message
        error_code: Optional error code if provided
    """

    def __init__(self, message: str, error_code: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class AuthenticationError(DataStreamDirectError):
    """
    Raised when authentication fails.

    This exception is raised when the provided credentials are invalid or
    when the authentication process fails for any reason.

    Args:
        message: Human-readable error description
        error_code: Optional error code from the API
    """

    pass


class ConnectionError(DataStreamDirectError):
    """
    Raised when connection to the API fails.

    This exception is raised when there are network issues, the service is
    unavailable, or when attempting to use a closed connection.

    Args:
        message: Human-readable error description
        error_code: Optional error code from the API
    """

    pass


class QueryError(DataStreamDirectError):
    """
    Raised when query execution fails.

    This exception is raised when a SQL query fails to execute, either due to
    syntax errors, permission issues, or other query-related problems.

    Args:
        message: Human-readable error description
        error_code: Optional error code from the API
    """

    pass


class APIError(DataStreamDirectError):
    """
    Raised when the API returns an error response.

    This exception is raised for general API errors that don't fall into
    other specific error categories.

    Args:
        message: Human-readable error description
        status_code: HTTP status code from the API response
        error_code: Optional error code from the API

    Attributes:
        message: The error message
        status_code: HTTP status code if available
        error_code: Optional error code if provided
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[HttpStatus] = None,
        error_code: Optional[str] = None,
    ) -> None:
        super().__init__(message, error_code)
        self.status_code = status_code
