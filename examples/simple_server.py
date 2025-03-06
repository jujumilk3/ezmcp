"""
A simple example of using EzMCP to create a server with tools.
"""
import httpx

from ezmcp import EzMCP, ImageContent, TextContent

# Create an EzMCP application
app = EzMCP("simple-server", debug=True)


@app.tool(description="Echo a message back to the user")
async def echo(message: str):
    """Echo a message back to the user."""
    return [TextContent(type="text", text=f"Echo: {message}")]


@app.tool(description="Fetch a website and return its content")
async def fetch_website(url: str):
    """Fetch a website and return its content."""
    headers = {
        "User-Agent": "EzMCP Example (github.com/jujumilk3/ezmcp)"
    }
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


if __name__ == "__main__":
    print("Starting EzMCP server on http://localhost:8000")
    print("Available tools:")
    for name, tool_info in app.tools.items():
        print(f"  - {name}: {tool_info['schema'].description}")
    print("\nDocumentation available at: http://localhost:8000/docs")
    print("SSE endpoint available at: http://localhost:8000/sse")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the application
    app.run(host="0.0.0.0", port=8000) 