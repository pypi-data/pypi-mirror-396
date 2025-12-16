"""
Custom exceptions for gravi CLI.
"""


class GraviError(Exception):
    """Base exception for all gravi CLI errors."""
    pass


class NotAuthenticatedError(GraviError):
    """Raised when user is not authenticated or token is expired."""
    pass


class APIError(GraviError):
    """Raised when mom API returns an error."""
    def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)


class InvalidTokenError(APIError):
    """Raised when a token is invalid or has been revoked."""
    pass


class PermissionDeniedError(APIError):
    """Raised when user doesn't have permission to access a resource."""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    pass


class ConfigError(GraviError):
    """Raised when there's an issue with the config file."""
    pass
