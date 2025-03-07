# ezmcp

Easy-to-use MCP server framework specialized for SSE.

## Overview

ezmcp is a lightweight framework that makes it easy to create MCP-compatible servers using a FastAPI-like syntax. It provides a simple decorator-based API for defining tools that can be called by MCP clients.

## Features

- FastAPI-style decorator API for defining MCP tools
- Automatic parameter validation and type conversion
- Automatic generation of tool schemas from function signatures
- Built-in support for SSE transport
- Easy integration with existing Starlette applications
- Interactive documentation page for exploring and testing tools

## Installation

```bash
pip install ezmcp
```

## Quick Start

```python
from ezmcp import ezmcp, TextContent

# Create an ezmcp application
app = ezmcp("my-app")

# Define a tool
@app.tool(description="Echo a message back to the user")
async def echo(message: str):
    """Echo a message back to the user."""
    return [TextContent(type="text", text=f"Echo: {message}")]

# Run the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

Once the server is running, you can:
- Access the interactive documentation at `http://localhost:8000/docs`
- Connect to the SSE endpoint at `http://localhost:8000/sse`

## Documentation

For more detailed documentation, see the [ezmcp/README.md](ezmcp/README.md) file.

## License

MIT

## commands

- install for test `pdm install -G test`
- install for dev `pdm install -G dev`
