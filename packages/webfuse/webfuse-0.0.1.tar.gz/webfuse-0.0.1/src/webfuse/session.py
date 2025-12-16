"""
Webfuse Session

Represents a browser session and provides automation methods.
"""

from typing import Optional, Dict, Any, List, Union, TYPE_CHECKING
import base64

from .exceptions import SessionError, AutomationError, TimeoutError

if TYPE_CHECKING:
    from .client import WebfuseClient


class Session:
    """
    Represents an active browser session.

    Provides methods for automating browser interactions like clicking,
    typing, taking screenshots, and navigating.

    Note: Do not instantiate directly. Use WebfuseClient.create_session()
    or WebfuseClient.get_session() instead.
    """

    def __init__(
        self,
        client: "WebfuseClient",
        session_id: str,
        space_id: str,
        link: str = None,
    ):
        self._client = client
        self.session_id = session_id
        self.space_id = space_id
        self.link = link
        self._ended = False

    def __repr__(self) -> str:
        status = "ended" if self._ended else "active"
        return f"<Session {self.session_id} ({status})>"

    def _ensure_active(self):
        """Ensure the session is still active."""
        if self._ended:
            raise SessionError("Session has been ended")

    def _call_rpc(
        self,
        method: str,
        parameters: Dict[str, Any] = None,
        timeout: int = 30000,
    ) -> Dict[str, Any]:
        """
        Call an RPC method on this session.

        Args:
            method: The method name to call
            parameters: Method parameters
            timeout: Timeout in milliseconds

        Returns:
            The RPC response
        """
        self._ensure_active()

        response = self._client._request(
            "POST",
            f"/rpc/{self.session_id}/call",
            json={
                "method": method,
                "parameters": parameters or {},
                "timeout": timeout,
            },
        )

        status = response.get("status")
        if status == "error":
            raise AutomationError(
                response.get("error", "Unknown error"),
                {"method": method, "response": response},
            )
        elif status == "timeout":
            raise TimeoutError(
                f"RPC call '{method}' timed out",
                {"method": method, "timeout": timeout},
            )

        return response.get("result", {})

    # Navigation methods

    def goto(self, url: str, new_tab: bool = False) -> Dict[str, Any]:
        """
        Navigate to a URL.

        Args:
            url: The URL to navigate to
            new_tab: If True, open in a new tab instead of current tab

        Returns:
            Result of the navigation

        Example:
            session.goto("https://example.com")
            session.goto("https://other.com", new_tab=True)
        """
        return self._call_rpc("relocate", {"url": url, "newTab": new_tab})

    def open_tab(self, url: str) -> Dict[str, Any]:
        """
        Open a new browser tab with the specified URL.

        Args:
            url: The URL to open in the new tab

        Returns:
            Result of opening the tab
        """
        return self._call_rpc("open_tab", {"url": url})

    # Mouse methods

    def click(
        self,
        target: str,
        move_mouse: bool = True,
    ) -> Dict[str, Any]:
        """
        Click on an element.

        Args:
            target: CSS selector of the element to click (e.g., "#button", ".submit")
            move_mouse: If True, move virtual mouse pointer to target before clicking

        Returns:
            Result of the click action

        Example:
            session.click("#login-button")
            session.click("button.primary")
        """
        return self._call_rpc("left_click", {"target": target, "moveMouse": move_mouse})

    def right_click(
        self,
        target: str,
        move_mouse: bool = True,
    ) -> Dict[str, Any]:
        """
        Right-click on an element (opens context menu).

        Args:
            target: CSS selector of the element
            move_mouse: If True, move virtual mouse pointer to target

        Returns:
            Result of the right-click action
        """
        return self._call_rpc("right_click", {"target": target, "moveMouse": move_mouse})

    def middle_click(
        self,
        target: str,
        move_mouse: bool = True,
    ) -> Dict[str, Any]:
        """
        Middle-click on an element (often opens links in new tab).

        Args:
            target: CSS selector of the element
            move_mouse: If True, move virtual mouse pointer to target

        Returns:
            Result of the middle-click action
        """
        return self._call_rpc("middle_click", {"target": target, "moveMouse": move_mouse})

    def hover(
        self,
        target: str,
        persistent: bool = False,
    ) -> Dict[str, Any]:
        """
        Move the mouse pointer to an element (hover).

        Args:
            target: CSS selector of the element
            persistent: If True, keep mouse pointer visible on screen

        Returns:
            Result of the hover action

        Example:
            session.hover("#dropdown-menu")
        """
        return self._call_rpc("mouse_move", {"target": target, "persistent": persistent})

    def scroll(
        self,
        target: str,
        amount: int,
        direction: str = "vertical",
    ) -> Dict[str, Any]:
        """
        Scroll an element.

        Args:
            target: CSS selector of the scrollable element
            amount: Pixels to scroll (positive = down/right, negative = up/left)
            direction: "vertical" or "horizontal"

        Returns:
            Result of the scroll action

        Example:
            session.scroll("body", 500)  # Scroll down 500px
            session.scroll("#content", -200)  # Scroll up 200px
        """
        return self._call_rpc("scroll", {
            "target": target,
            "amount": amount,
            "direction": direction,
        })

    # Keyboard methods

    def type(
        self,
        target: str,
        text: str,
        overwrite: bool = False,
        move_mouse: bool = True,
        delay: int = 100,
    ) -> Dict[str, Any]:
        """
        Type text into an input field.

        Args:
            target: CSS selector of the input element
            text: The text to type
            overwrite: If True, clear existing content before typing
            move_mouse: If True, move virtual mouse pointer to target
            delay: Milliseconds between keystrokes (default: 100)

        Returns:
            Result of the type action

        Example:
            session.type("#email", "user@example.com")
            session.type("#search", "new query", overwrite=True)
        """
        return self._call_rpc("type", {
            "target": target,
            "text": text,
            "overwrite": overwrite,
            "moveMouse": move_mouse,
            "timePerChar": delay,
        })

    def press(
        self,
        target: str,
        key: str,
        modifiers: Dict[str, bool] = None,
    ) -> Dict[str, Any]:
        """
        Press a keyboard key.

        Args:
            target: CSS selector of the element to receive the key press
            key: Key to press (e.g., "Enter", "Escape", "Tab", "a", "ArrowDown")
            modifiers: Modifier keys dict with keys: altKey, ctrlKey, metaKey, shiftKey

        Returns:
            Result of the key press

        Example:
            session.press("#input", "Enter")
            session.press("#editor", "s", {"ctrlKey": True})  # Ctrl+S
        """
        params = {"target": target, "key": key}
        if modifiers:
            params["options"] = modifiers
        return self._call_rpc("key_press", params)

    # Snapshot methods

    def screenshot(self, options: Dict[str, Any] = None) -> bytes:
        """
        Take a screenshot of the current page.

        Args:
            options: Optional screenshot options

        Returns:
            Screenshot image as bytes (PNG format)

        Example:
            image_bytes = session.screenshot()
            with open("screenshot.png", "wb") as f:
                f.write(image_bytes)
        """
        result = self._call_rpc("take_gui_snapshot", {"options": options or {}})

        # Result may be None if screenshot not supported
        if result is None:
            raise AutomationError("Screenshot not available", {"method": "take_gui_snapshot"})

        # Result should contain base64-encoded image
        if isinstance(result, dict):
            image_data = result.get("image") or result.get("data") or result.get("snapshot")
        elif isinstance(result, str):
            image_data = result
        else:
            image_data = None

        if image_data:
            # Handle base64 with or without data URL prefix
            if "," in image_data:
                image_data = image_data.split(",", 1)[1]
            return base64.b64decode(image_data)

        # Return raw result if no image found
        return result

    def dom_snapshot(
        self,
        root_selector: str = None,
        crossframe: bool = False,
        modifier: str = "downsample",
    ) -> str:
        """
        Get a text representation of the page DOM.

        Useful for understanding page structure and finding CSS selectors.

        Args:
            root_selector: Optional CSS selector to scope the snapshot
            crossframe: If True, include content from iframes
            modifier: Snapshot modifier ("downsample", "full", or custom)

        Returns:
            Text representation of the DOM

        Example:
            dom = session.dom_snapshot()
            print(dom)  # Understand page structure
        """
        options = {"modifier": modifier}
        if root_selector:
            options["rootSelector"] = root_selector
        if crossframe:
            options["crossframe"] = True

        result = self._call_rpc("take_dom_snapshot", {"options": options})
        # Result may be a string directly or a dict with snapshot/dom key
        if isinstance(result, str):
            return result
        return result.get("snapshot") or result.get("dom") or str(result)

    # Utility methods

    def wait(self, ms: int) -> None:
        """
        Wait for a specified amount of time.

        Args:
            ms: Milliseconds to wait

        Example:
            session.click("#submit")
            session.wait(2000)  # Wait 2 seconds for page to load
            session.screenshot()
        """
        self._call_rpc("wait", {"ms": ms})

    def get_functions(self) -> List[Dict[str, Any]]:
        """
        Get list of available automation functions.

        Returns:
            List of function definitions with names, descriptions, and parameters
        """
        self._ensure_active()
        response = self._client._request("GET", f"/rpc/{self.session_id}/functions")
        return response.get("functions", [])

    # Session management

    def end(self) -> bool:
        """
        End this session.

        After calling this method, no further automation is possible.

        Returns:
            True if session was ended successfully
        """
        if self._ended:
            return True

        try:
            self._client._request(
                "POST",
                f"/api/v1/sessions/{self.session_id}/end",
            )
            self._ended = True
            return True
        except Exception as e:
            raise SessionError(f"Failed to end session: {e}")

    @property
    def is_active(self) -> bool:
        """Check if the session is still active."""
        return not self._ended
