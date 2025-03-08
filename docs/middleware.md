# Middleware in ezmcp

ezmcp supports middleware similar to FastAPI, allowing you to add behavior that is applied across your entire application.

## Using Middleware

There are two ways to add middleware to your ezmcp application:

### 1. Using the `@app.middleware` decorator

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

### 2. Using the `app.add_middleware()` method

```python
from starlette.requests import Request

from ezmcp import EzmcpHTTPMiddleware, TextContent, ezmcp

app = ezmcp("my-app")

class CustomHeaderMiddleware(EzmcpHTTPMiddleware):
    """Add a custom header to the response."""
    
    async def dispatch(self, request: Request, call_next):
        """Add a custom header to the response."""
        response = await call_next(request)
        response.headers["X-Custom-Header"] = "Hello from middleware!"
        return response

app.add_middleware(CustomHeaderMiddleware)

@app.tool(description="Echo a message back to the user")
async def echo(message: str):
    """Echo a message back to the user."""
    return [TextContent(type="text", text=f"Echo: {message}")]
```

## Middleware Order

Middleware is executed in the order it's added, with the last added middleware running first. This means that the middleware added first will be closest to the endpoint, and the middleware added last will be closest to the client.

For example:

```python
@app.middleware
async def first_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Order"] = response.headers.get("X-Order", "") + "1"
    return response

@app.middleware
async def second_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Order"] = response.headers.get("X-Order", "") + "2"
    return response

@app.middleware
async def third_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Order"] = response.headers.get("X-Order", "") + "3"
    return response
```

In this example, the middleware execution order would be:

1. `third_middleware`
2. `second_middleware`
3. `first_middleware`

And the resulting `X-Order` header would be `"321"`.

## Creating Custom Middleware

You can create custom middleware by either:

1. Using the `@app.middleware` decorator with an async function
2. Creating a class that inherits from `EzmcpHTTPMiddleware` and overriding the `dispatch` method

### Using the Decorator

```python
@app.middleware
async def custom_middleware(request: Request, call_next):
    # Do something before the request is processed
    response = await call_next(request)
    # Do something after the request is processed
    return response
```

### Creating a Middleware Class

```python
from ezmcp import EzmcpHTTPMiddleware

class CustomMiddleware(EzmcpHTTPMiddleware):
    def __init__(self, app, custom_arg: str = "default"):
        super().__init__(app)
        self.custom_arg = custom_arg
    
    async def dispatch(self, request: Request, call_next):
        # Do something before the request is processed
        response = await call_next(request)
        # Do something after the request is processed
        return response

app.add_middleware(CustomMiddleware, custom_arg="custom value")
```

## Examples

See the [middleware_example.py](../examples/middleware_example.py) file for a complete example of using middleware with ezmcp.
