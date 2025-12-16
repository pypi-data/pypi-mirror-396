"""
Webfuse Python SDK

A Python client for automating browser sessions via the Webfuse RPC service.

Example:
    from webfuse import WebfuseClient

    client = WebfuseClient(api_key="rk_your_api_key")

    # Create a session
    session = client.create_session(space_id="1234")

    # Automate the browser
    session.goto("https://example.com")
    session.click("#login-button")
    session.type("#username", "user@example.com")

    # Take a screenshot
    screenshot = session.screenshot()

    # End the session
    session.end()
"""

from .client import WebfuseClient
from .session import Session
from .async_client import AsyncWebfuseClient
from .async_session import AsyncSession
from .exceptions import (
    WebfuseError,
    AuthenticationError,
    SessionError,
    AutomationError,
    TimeoutError,
)

__version__ = "0.1.0"
__all__ = [
    # Sync API
    "WebfuseClient",
    "Session",
    # Async API
    "AsyncWebfuseClient",
    "AsyncSession",
    # Exceptions
    "WebfuseError",
    "AuthenticationError",
    "SessionError",
    "AutomationError",
    "TimeoutError",
]
