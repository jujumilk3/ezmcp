"""
An example of using middleware with ezmcp.
"""

import asyncio
import random
import time

from starlette.requests import Request

from ezmcp import EzmcpHTTPMiddleware, TextContent, ezmcp

# Create an ezmcp application
app = ezmcp("middleware-example", debug=True)


# Define a middleware using the decorator
@app.middleware
async def process_time_middleware(request: Request, call_next):
    print(1)
    print("process_time_middleware called")
    """Add a header with the processing time."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"process_time: {process_time}")
    return response


# Define a custom middleware class
class CustomHeaderMiddleware(EzmcpHTTPMiddleware):
    """Add a custom header to the response."""

    async def dispatch(self, request: Request, call_next):
        print(2)
        print("CustomHeaderMiddleware called")
        """Add a custom header to the response."""
        response = await call_next(request)
        response.headers["X-Custom-Header"] = "Hello from middleware!"
        return response


class CustomSleepMiddleware(EzmcpHTTPMiddleware):
    """Sleep for a random amount of time."""

    async def dispatch(self, request: Request, call_next):
        print(3)
        print("CustomSleepMiddleware called")
        """Sleep for a random amount of time."""
        await asyncio.sleep(random.randint(0, 10))
        return await call_next(request)


# Add the custom middleware
app.add_middleware(CustomHeaderMiddleware)
app.add_middleware(CustomSleepMiddleware)


@app.middleware
async def custom_middleware(request: Request, call_next):
    print(4)
    print("custom_middleware called")
    return await call_next(request)


# Define a tool
@app.tool(description="Echo a message back to the user")
async def echo(message: str):
    """Echo a message back to the user."""
    return [TextContent(type="text", text=f"Echo: {message}")]


# Run the application
if __name__ == "__main__":
    print("Try accessing the docs at http://localhost:8000/docs")
    print("Check the response headers to see the middleware in action")
    app.run(host="0.0.0.0", port=8000)
