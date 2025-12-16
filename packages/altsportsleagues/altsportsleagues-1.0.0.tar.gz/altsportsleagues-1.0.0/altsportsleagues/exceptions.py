"""
Custom exceptions for AltSportsLeagues SDK
"""


class AltSportsLeaguesError(Exception):
    """Base exception for all AltSportsLeagues SDK errors"""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        if self.status_code:
            return f"[HTTP {self.status_code}] {self.message}"
        return self.message


class AuthenticationError(AltSportsLeaguesError):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed. Please check your API key."):
        super().__init__(message, 401)


class ValidationError(AltSportsLeaguesError):
    """Raised when request validation fails"""

    def __init__(self, message: str = "Request validation failed."):
        super().__init__(message, 422)


class RateLimitError(AltSportsLeaguesError):
    """Raised when API rate limit is exceeded"""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later.", retry_after: int = None):
        super().__init__(message, 429)
        self.retry_after = retry_after

    def __str__(self):
        if self.retry_after:
            return f"{self.message} Retry after {self.retry_after} seconds."
        return self.message


class NotFoundError(AltSportsLeaguesError):
    """Raised when requested resource is not found"""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID '{resource_id}' not found."
        super().__init__(message, 404)
        self.resource_type = resource_type
        self.resource_id = resource_id


class PermissionError(AltSportsLeaguesError):
    """Raised when user doesn't have permission for an action"""

    def __init__(self, message: str = "Insufficient permissions for this action."):
        super().__init__(message, 403)


class ServerError(AltSportsLeaguesError):
    """Raised when server encounters an internal error"""

    def __init__(self, message: str = "Internal server error. Please try again later."):
        super().__init__(message, 500)


class NetworkError(AltSportsLeaguesError):
    """Raised when network connectivity issues occur"""

    def __init__(self, message: str = "Network error. Please check your internet connection."):
        super().__init__(message)


class ConfigurationError(AltSportsLeaguesError):
    """Raised when SDK is not properly configured"""

    def __init__(self, message: str = "SDK configuration error."):
        super().__init__(message)
