"""
A simple example of using ezmcp to create a server with tools.
"""

import base64
import json

import httpx

from ezmcp import ImageContent, TextContent, ezmcp

# Create an ezmcp application
app = ezmcp("simple-server", debug=True)


@app.tool(description="Echo a message back to the user")
async def echo(message: str):
    """Echo a message back to the user."""
    return [TextContent(type="text", text=f"Echo: {message}")]


@app.tool(description="Return user information as JSON")
async def user_info(name: str, age: int, is_active: bool = True):
    """Return user information as JSON."""
    user_data = {
        "name": name,
        "age": age,
        "is_active": is_active,
        "status": "active" if is_active else "inactive",
    }
    return [TextContent(type="text", text=json.dumps(user_data, indent=2))]


@app.tool(description="Fetch a website and return its content")
async def fetch_website(url: str):
    """Fetch a website and return its content."""
    headers = {"User-Agent": "ezmcp Example (github.com/jujumilk3/ezmcp)"}
    async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return [TextContent(type="text", text=response.text)]


@app.tool(description="Add two numbers together")
async def add(a: int, b: int = 0):
    """Add two numbers together."""
    result = a + b
    return [TextContent(type="text", text=f"Result: {result}")]


@app.tool(description="Get a greeting with the user's name")
async def greet(name: str = "World"):
    """Get a greeting with the user's name."""
    return [TextContent(type="text", text=f"Hello, {name}!")]


@app.tool(description="Fetch a sample image")
async def fetch_image():
    """Fetch a sample image."""
    downloaded_image = httpx.get("https://placehold.co/600x400")
    as_binary = downloaded_image.content
    as_base64 = base64.b64encode(as_binary).decode("utf-8")
    return [ImageContent(type="image", data=as_base64, mimeType="image/png")]


if __name__ == "__main__":
    print("Starting ezmcp server on http://localhost:8000")
    print("Available tools:")
    for name, tool_info in app.tools.items():
        print(f"  - {name}: {tool_info['schema'].description}")
    print("\nDocumentation available at: http://localhost:8000/docs")
    print("SSE endpoint available at: http://localhost:8000/sse")
    print("\nPress Ctrl+C to stop the server")

    # Run the application
    app.run(host="0.0.0.0", port=8000)
