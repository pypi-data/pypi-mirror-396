"""Custom exceptions for API client."""


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize APIError.

        Args:
            message: Error message
            status_code: HTTP status code if available
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(APIError):
    """Resource not found (404)."""

    def __init__(self, message: str = "Resource not found") -> None:
        """Initialize NotFoundError.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=404)


class AuthenticationError(APIError):
    """Authentication failed (401)."""

    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialize AuthenticationError.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=401)


class ValidationError(APIError):
    """Validation error (422)."""

    def __init__(self, message: str = "Validation error") -> None:
        """Initialize ValidationError.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=422)


class ConflictError(APIError):
    """Resource conflict (409)."""

    def __init__(self, message: str = "Resource conflict") -> None:
        """Initialize ConflictError.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=409)
