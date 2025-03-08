# ezmcp

Easy-to-use MCP server framework specialized for SSE.

## Overview

ezmcp is a lightweight framework that makes it easy to create MCP-compatible servers using a FastAPI-like syntax. It provides a simple decorator-based API for defining tools that can be called by MCP clients.

## Features

- FastAPI-style decorator API for defining MCP tools
- Automatic parameter validation and type conversion
- Automatic generation of tool schemas from function signatures
- Built-in support for SSE transport
- FastAPI-style middleware support
- Easy integration with existing Starlette applications
- Interactive documentation page for exploring and testing tools

![docs_image](./docs/images/docs.png)

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

## Middleware

ezmcp supports middleware similar to FastAPI, allowing you to add behavior that is applied across your entire application.

```python
from starlette.requests import Request

from ezmcp import TextContent, ezmcp

app = ezmcp("my-app")

@app.middleware
async def process_time_middleware(request: Request, call_next):
    """Add a header with the processing time."""
    import time
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.tool(description="Echo a message back to the user")
async def echo(message: str):
    """Echo a message back to the user."""
    return [TextContent(type="text", text=f"Echo: {message}")]
```

For more information on middleware, see the [middleware documentation](docs/middleware.md).

## Documentation

For more detailed documentation, see the [ezmcp/README.md](ezmcp/README.md) file.

## License

MIT

## commands

- install for test `pdm install -G test`
- install for dev `pdm install -G dev`
