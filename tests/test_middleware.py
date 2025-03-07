import pytest
from starlette.requests import Request
from starlette.testclient import TestClient

from ezmcp import EzmcpHTTPMiddleware, TextContent, ezmcp


@pytest.fixture
def app():
    """Create a test ezmcp application."""
    return ezmcp("test-app")


def test_middleware_decorator():
    """Test that the middleware decorator works correctly."""
    app = ezmcp("test-app")

    # Define a middleware using the decorator
    @app.middleware
    async def add_custom_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Custom-Header"] = "Test"
        return response

    # Define a tool
    @app.tool(description="Test tool")
    async def test_tool():
        return [TextContent(type="text", text="Test")]

    # Create a test client
    client = TestClient(app.get_app())

    # Make a request to the docs endpoint
    response = client.get("/docs")

    # Check that the middleware was applied
    assert response.headers["X-Custom-Header"] == "Test"


def test_add_middleware():
    """Test that the add_middleware method works correctly."""
    app = ezmcp("test-app")

    # Define a custom middleware class
    class CustomHeaderMiddleware(EzmcpHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Custom-Header"] = "Test"
            return response

    # Add the middleware
    app.add_middleware(CustomHeaderMiddleware)

    # Define a tool
    @app.tool(description="Test tool")
    async def test_tool():
        return [TextContent(type="text", text="Test")]

    # Create a test client
    client = TestClient(app.get_app())

    # Make a request to the docs endpoint
    response = client.get("/docs")

    # Check that the middleware was applied
    assert response.headers["X-Custom-Header"] == "Test"


def test_middleware_order():
    """Test that middleware is executed in the correct order (last added runs first)."""
    app = ezmcp("test-app")

    # Define middleware using decorators
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

    # Define a tool
    @app.tool(description="Test tool")
    async def test_tool():
        return [TextContent(type="text", text="Test")]

    # Create a test client
    client = TestClient(app.get_app())

    # Make a request to the docs endpoint
    response = client.get("/docs")

    # Check that the middleware was applied in the correct order
    # Last added middleware runs first, so the order should be 3, 2, 1
    assert response.headers["X-Order"] == "321"


def test_middleware_with_add_middleware_method():
    """Test that middleware added with add_middleware method works correctly."""
    app = ezmcp("test-app")

    # Define custom middleware classes
    class FirstMiddleware(EzmcpHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Order"] = response.headers.get("X-Order", "") + "1"
            return response

    class SecondMiddleware(EzmcpHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Order"] = response.headers.get("X-Order", "") + "2"
            return response

    class ThirdMiddleware(EzmcpHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Order"] = response.headers.get("X-Order", "") + "3"
            return response

    # Add middleware in order
    app.add_middleware(FirstMiddleware)
    app.add_middleware(SecondMiddleware)
    app.add_middleware(ThirdMiddleware)

    # Define a tool
    @app.tool(description="Test tool")
    async def test_tool():
        return [TextContent(type="text", text="Test")]

    # Create a test client
    client = TestClient(app.get_app())

    # Make a request to the docs endpoint
    response = client.get("/docs")

    # Check that the middleware was applied in the correct order
    # Last added middleware runs first, so the order should be 3, 2, 1
    assert response.headers["X-Order"] == "321"


def test_mixed_middleware_methods():
    """Test that middleware added with both methods works correctly."""
    app = ezmcp("test-app")

    # Define a middleware using the decorator
    @app.middleware
    async def decorator_middleware(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Decorator"] = "True"
        return response

    # Define a custom middleware class
    class ClassMiddleware(EzmcpHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Class"] = "True"
            return response

    # Add the class middleware
    app.add_middleware(ClassMiddleware)

    # Define a tool
    @app.tool(description="Test tool")
    async def test_tool():
        return [TextContent(type="text", text="Test")]

    # Create a test client
    client = TestClient(app.get_app())

    # Make a request to the docs endpoint
    response = client.get("/docs")

    # Check that both middleware were applied
    assert response.headers["X-Decorator"] == "True"
    assert response.headers["X-Class"] == "True"
