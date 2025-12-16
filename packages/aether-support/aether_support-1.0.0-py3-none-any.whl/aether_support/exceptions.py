"""
Exception classes for Aether Support SDK.
"""

from typing import Any, Optional


class AetherError(Exception):
    """Base exception for Aether Support SDK errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
    
    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(AetherError):
    """Raised when authentication fails (invalid API key, etc.)."""
    
    def __init__(
        self,
        message: str = "Authentication failed. Please check your API key.",
        status_code: int = 401,
        response_data: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, response_data)


class AuthorizationError(AetherError):
    """Raised when access is denied (insufficient permissions)."""
    
    def __init__(
        self,
        message: str = "Access denied. You don't have permission to perform this action.",
        status_code: int = 403,
        response_data: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, response_data)


class NotFoundError(AetherError):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self,
        message: str = "The requested resource was not found.",
        status_code: int = 404,
        response_data: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, response_data)


class ValidationError(AetherError):
    """Raised when request validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed. Please check your request data.",
        status_code: int = 400,
        response_data: Optional[dict[str, Any]] = None,
        errors: Optional[list[dict[str, Any]]] = None,
    ):
        super().__init__(message, status_code, response_data)
        self.errors = errors or []


class RateLimitError(AetherError):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded. Please slow down your requests.",
        status_code: int = 429,
        response_data: Optional[dict[str, Any]] = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, status_code, response_data)
        self.retry_after = retry_after


class ServerError(AetherError):
    """Raised when the server returns an error."""
    
    def __init__(
        self,
        message: str = "An internal server error occurred. Please try again later.",
        status_code: int = 500,
        response_data: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, response_data)


class NetworkError(AetherError):
    """Raised when a network error occurs."""
    
    def __init__(
        self,
        message: str = "A network error occurred. Please check your connection.",
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.original_error = original_error


class TimeoutError(AetherError):
    """Raised when a request times out."""
    
    def __init__(
        self,
        message: str = "The request timed out. Please try again.",
        timeout: Optional[float] = None,
    ):
        super().__init__(message)
        self.timeout = timeout


def raise_for_status(status_code: int, response_data: dict[str, Any]) -> None:
    """Raise an appropriate exception based on the status code."""
    
    message = response_data.get("detail") or response_data.get("message") or "Unknown error"
    
    if status_code == 400:
        raise ValidationError(
            message=message,
            response_data=response_data,
            errors=response_data.get("errors"),
        )
    elif status_code == 401:
        raise AuthenticationError(message=message, response_data=response_data)
    elif status_code == 403:
        raise AuthorizationError(message=message, response_data=response_data)
    elif status_code == 404:
        raise NotFoundError(message=message, response_data=response_data)
    elif status_code == 429:
        raise RateLimitError(
            message=message,
            response_data=response_data,
            retry_after=response_data.get("retry_after"),
        )
    elif status_code >= 500:
        raise ServerError(
            message=message,
            status_code=status_code,
            response_data=response_data,
        )
    elif status_code >= 400:
        raise AetherError(
            message=message,
            status_code=status_code,
            response_data=response_data,
        )
