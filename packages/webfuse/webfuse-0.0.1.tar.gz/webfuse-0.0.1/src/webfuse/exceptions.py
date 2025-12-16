"""
Webfuse SDK Exceptions
"""


class WebfuseError(Exception):
    """Base exception for all Webfuse SDK errors."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(WebfuseError):
    """Raised when authentication fails."""

    pass


class SessionError(WebfuseError):
    """Raised when session operations fail."""

    pass


class AutomationError(WebfuseError):
    """Raised when automation commands fail."""

    pass


class TimeoutError(WebfuseError):
    """Raised when an operation times out."""

    pass
