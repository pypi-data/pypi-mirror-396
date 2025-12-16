# Webfuse Python SDK

A Python client for automating browser sessions via the Webfuse RPC service.

## Installation

```bash
pip install webfuse
```

## Quick Start

```python
from webfuse import WebfuseClient

# Initialize the client with your API key
client = WebfuseClient(api_key="rk_your_api_key")

# Create a browser session
session = client.create_session(space_id="1234")

# Automate the browser
session.goto("https://example.com")
session.click("#login-button")
session.type("#username", "user@example.com")
session.type("#password", "secret123")
session.click("#submit")

# Take a screenshot
screenshot = session.screenshot()
with open("result.png", "wb") as f:
    f.write(screenshot)

# End the session when done
session.end()

# Don't forget to close the client
client.close()
```

## Using Context Managers

```python
from webfuse import WebfuseClient

with WebfuseClient(api_key="rk_your_api_key") as client:
    session = client.create_session(space_id="1234")
    session.goto("https://example.com")
    session.click("button.submit")
    session.end()
```

## Async Support

```python
import asyncio
from webfuse import AsyncWebfuseClient

async def main():
    async with AsyncWebfuseClient(api_key="rk_your_api_key") as client:
        session = await client.create_session(space_id="1234")

        await session.goto("https://example.com")
        await session.click("#button")
        await session.type("#input", "Hello World")

        screenshot = await session.screenshot()

        await session.end()

asyncio.run(main())
```

## Available Methods

### Navigation

- `session.goto(url, new_tab=False)` - Navigate to a URL
- `session.open_tab(url)` - Open a new browser tab

### Mouse Actions

- `session.click(selector)` - Left-click an element
- `session.right_click(selector)` - Right-click an element
- `session.middle_click(selector)` - Middle-click an element
- `session.hover(selector)` - Move mouse to element
- `session.scroll(selector, amount, direction="vertical")` - Scroll an element

### Keyboard Actions

- `session.type(selector, text)` - Type text into an input
- `session.press(selector, key, modifiers=None)` - Press a keyboard key

### Screenshots & DOM

- `session.screenshot()` - Take a screenshot (returns PNG bytes)
- `session.dom_snapshot()` - Get text representation of the DOM

### Utilities

- `session.wait(ms)` - Wait for specified milliseconds
- `session.get_functions()` - List available automation functions

### Session Management

- `session.end()` - End the session
- `session.is_active` - Check if session is still active

## Configuration

```python
client = WebfuseClient(
    api_key="rk_your_api_key",
    rpc_url="https://rpc.webfuse.com",  # Custom RPC URL
    timeout=60.0,  # Request timeout in seconds
)
```

## Error Handling

```python
from webfuse import WebfuseClient, WebfuseError, AuthenticationError, AutomationError

try:
    with WebfuseClient(api_key="rk_your_api_key") as client:
        session = client.create_session(space_id="1234")
        session.click("#nonexistent-element")
except AuthenticationError:
    print("Invalid API key")
except AutomationError as e:
    print(f"Automation failed: {e.message}")
except WebfuseError as e:
    print(f"Error: {e.message}")
```

## License

MIT
