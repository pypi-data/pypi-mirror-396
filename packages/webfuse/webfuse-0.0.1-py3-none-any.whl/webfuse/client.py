"""
Webfuse Client

Main entry point for the Webfuse SDK.
"""

import httpx
from typing import Optional, Dict, Any, List

from .session import Session
from .exceptions import WebfuseError, AuthenticationError, SessionError


DEFAULT_RPC_URL = "https://rpc.webfuse.com"
DEFAULT_TIMEOUT = 30.0


class WebfuseClient:
    """
    Client for interacting with the Webfuse RPC service.

    Args:
        api_key: Your Webfuse API key (starts with 'rk_' or 'ck_')
        space_id: Your Webfuse space ID (required for session operations)
        rpc_url: URL of the RPC service (default: https://rpc.webfuse.com)
        timeout: Default timeout for requests in seconds (default: 30)

    Example:
        client = WebfuseClient(api_key="rk_your_api_key", space_id="1234")
        session = client.create_session()
    """

    def __init__(
        self,
        api_key: str,
        space_id: str = None,
        rpc_url: str = DEFAULT_RPC_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        if not api_key:
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.space_id = space_id
        self.rpc_url = rpc_url.rstrip("/")
        self.timeout = timeout

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if space_id:
            headers["X-Space-ID"] = space_id

        self._http_client = httpx.Client(
            base_url=self.rpc_url,
            headers=headers,
            timeout=timeout,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._http_client.close()

    def _request(
        self,
        method: str,
        path: str,
        json: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the RPC service."""
        try:
            response = self._http_client.request(
                method=method,
                url=path,
                json=json,
                params=params,
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 404:
                raise SessionError("Resource not found", {"path": path})
            elif response.status_code >= 400:
                error_detail = response.text
                try:
                    error_detail = response.json()
                except Exception:
                    pass
                raise WebfuseError(
                    f"Request failed with status {response.status_code}",
                    {"status": response.status_code, "detail": error_detail},
                )

            return response.json()

        except httpx.TimeoutException:
            from .exceptions import TimeoutError
            raise TimeoutError(f"Request timed out after {self.timeout}s")
        except httpx.RequestError as e:
            raise WebfuseError(f"Request failed: {str(e)}")

    def health(self) -> Dict[str, Any]:
        """
        Check the health of the RPC service.

        Returns:
            Health status information
        """
        return self._request("GET", "/health")

    def create_session(
        self,
        space_id: str = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """
        Create a new browser session.

        Args:
            space_id: The Webfuse space ID (uses client's space_id if not provided)
            metadata: Optional metadata to attach to the session

        Returns:
            A Session object for automating the browser

        Example:
            client = WebfuseClient(api_key="rk_...", space_id="1234")
            session = client.create_session()
            session.goto("https://example.com")
        """
        space_id = space_id or self.space_id
        if not space_id:
            raise SessionError("space_id is required. Provide it to create_session() or WebfuseClient()")

        response = self._request(
            "POST",
            "/api/v1/sessions",
            json={
                "metadata": metadata or {},
            },
        )

        session_id = response.get("session_id")
        if not session_id:
            raise SessionError("Failed to create session", response)

        return Session(
            client=self,
            session_id=session_id,
            space_id=space_id,
            link=response.get("link"),
        )

    def get_session(self, session_id: str, space_id: str) -> Session:
        """
        Get an existing session by ID.

        Args:
            session_id: The session ID
            space_id: The space ID the session belongs to

        Returns:
            A Session object for automating the browser
        """
        # Verify the session exists
        response = self._request("GET", f"/api/v1/sessions/{session_id}")

        return Session(
            client=self,
            session_id=session_id,
            space_id=space_id,
        )

    def list_sessions(self, space_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List active sessions.

        Args:
            space_id: Optional space ID to filter by

        Returns:
            List of session information dictionaries
        """
        params = {}
        if space_id:
            params["space_id"] = space_id

        response = self._request("GET", "/api/v1/sessions", params=params)
        return response.get("sessions", [])
