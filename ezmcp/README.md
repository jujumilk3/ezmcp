# EzMCP

A FastAPI-style framework for using MCP (Model Context Protocol) with Server-Sent Events (SSE).

## Installation

```bash
pip install ezmcp
```

## Quick Start

```python
from ezmcp import EzMCP, TextContent

# Create an EzMCP application
app = EzMCP("my-app")

# Define a tool
@app.tool(description="Echo a message back to the user")
async def echo(message: str):
    """Echo a message back to the user."""
    return [TextContent(type="text", text=f"Echo: {message}")]

# Run the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

## Features

- FastAPI-style decorator API for defining MCP tools
- Automatic parameter validation and type conversion
- Automatic generation of tool schemas from function signatures
- Built-in support for SSE transport
- Easy integration with existing Starlette applications

## API Reference

### EzMCP

The main application class.

```python
app = EzMCP(
    name="my-app",                # Name of the MCP server
    sse_path="/messages",        # Path for SSE messages
    sse_endpoint="/sse",          # Endpoint for SSE connections
    debug=False                   # Whether to enable debug mode
)
```

### @app.tool

Decorator to register a function as a tool.

```python
@app.tool(
    name="my-tool",               # Name of the tool (defaults to function name)
    description="My tool"         # Description of the tool (defaults to function docstring)
)
async def my_tool(param1: str, param2: int = 0):
    # Tool implementation
    return [TextContent(type="text", text="Result")]
```

### app.run

Run the application with uvicorn.

```python
app.run(
    host="0.0.0.0",               # Host to bind to
    port=8000                     # Port to bind to
)
```

### app.get_app

Get the Starlette application for integration with other frameworks.

```python
starlette_app = app.get_app()
```

## Response Types

EzMCP supports the following response types:

- `TextContent`: Text content
- `ImageContent`: Image content
- `EmbeddedResource`: Embedded resource

Example:

```python
from ezmcp import TextContent, ImageContent, EmbeddedResource

# Text content
text = TextContent(type="text", text="Hello, world!")

# Image content
image = ImageContent(type="image", url="https://example.com/image.png")

# Embedded resource
resource = EmbeddedResource(type="embedded", url="https://example.com/resource")
```

## Advanced Usage

### Integration with Existing Starlette Applications

```python
from starlette.applications import Starlette
from starlette.routing import Mount

# Create an EzMCP application
app = EzMCP("my-app")

# Define tools
@app.tool()
async def echo(message: str):
    return [TextContent(type="text", text=f"Echo: {message}")]

# Get the Starlette application
starlette_app = app.get_app()

# Create a new Starlette application with additional routes
main_app = Starlette(
    routes=[
        Mount("/mcp", app=starlette_app),
        # Add other routes here
    ]
)
```

## License

MIT 