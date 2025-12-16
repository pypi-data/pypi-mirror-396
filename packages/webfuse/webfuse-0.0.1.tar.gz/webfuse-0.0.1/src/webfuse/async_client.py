"""
Webfuse Async Client

Async version of the Webfuse client for use with asyncio.
"""

import httpx
from typing import Optional, Dict, Any, List

from .async_session import AsyncSession
from .exceptions import WebfuseError, AuthenticationError, SessionError


DEFAULT_RPC_URL = "https://rpc.webfuse.com"
DEFAULT_TIMEOUT = 30.0


class AsyncWebfuseClient:
    """
    Async client for interacting with the Webfuse RPC service.

    Args:
        api_key: Your Webfuse API key (starts with 'rk_' or 'ck_')
        rpc_url: URL of the RPC service (default: https://rpc.webfuse.com)
        timeout: Default timeout for requests in seconds (default: 30)

    Example:
        async with AsyncWebfuseClient(api_key="rk_your_api_key") as client:
            session = await client.create_session(space_id="1234")
            await session.goto("https://example.com")
    """

    def __init__(
        self,
        api_key: str,
        rpc_url: str = DEFAULT_RPC_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        if not api_key:
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.rpc_url = rpc_url.rstrip("/")
        self.timeout = timeout

        self._http_client = httpx.AsyncClient(
            base_url=self.rpc_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self._http_client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        json: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make an async HTTP request to the RPC service."""
        try:
            response = await self._http_client.request(
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

    async def health(self) -> Dict[str, Any]:
        """
        Check the health of the RPC service.

        Returns:
            Health status information
        """
        return await self._request("GET", "/health")

    async def create_session(
        self,
        space_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AsyncSession:
        """
        Create a new browser session.

        Args:
            space_id: The Webfuse space ID to create the session in
            metadata: Optional metadata to attach to the session

        Returns:
            An AsyncSession object for automating the browser

        Example:
            session = await client.create_session(space_id="1234")
            await session.goto("https://example.com")
        """
        response = await self._request(
            "POST",
            "/api/v1/sessions",
            json={
                "space_id": space_id,
                "metadata": metadata or {},
            },
        )

        session_id = response.get("session_id")
        if not session_id:
            raise SessionError("Failed to create session", response)

        return AsyncSession(
            client=self,
            session_id=session_id,
            space_id=space_id,
        )

    async def get_session(self, session_id: str, space_id: str) -> AsyncSession:
        """
        Get an existing session by ID.

        Args:
            session_id: The session ID
            space_id: The space ID the session belongs to

        Returns:
            An AsyncSession object for automating the browser
        """
        # Verify the session exists
        await self._request("GET", f"/api/v1/sessions/{session_id}")

        return AsyncSession(
            client=self,
            session_id=session_id,
            space_id=space_id,
        )

    async def list_sessions(self, space_id: Optional[str] = None) -> List[Dict[str, Any]]:
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

        response = await self._request("GET", "/api/v1/sessions", params=params)
        return response.get("sessions", [])
