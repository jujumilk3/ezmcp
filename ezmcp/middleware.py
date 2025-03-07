from typing import Any, Awaitable, Callable, Iterator, List, Optional, Type, Union

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send


class Middleware:
    """
    A class for storing middleware configuration.

    This is similar to Starlette's Middleware class but adapted for ezmcp.
    """

    def __init__(
        self, cls: Type[BaseHTTPMiddleware], *args: Any, **kwargs: Any
    ) -> None:
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def __iter__(self) -> Iterator[Any]:
        as_tuple = (self.cls, self.args, self.kwargs)
        return iter(as_tuple)


class EzmcpHTTPMiddleware(BaseHTTPMiddleware):
    """
    Base class for HTTP middleware in ezmcp.

    This class is a wrapper around Starlette's BaseHTTPMiddleware.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Override this method to implement custom middleware.

        Args:
            request: The incoming request
            call_next: A function that calls the next middleware or endpoint

        Returns:
            The response from the next middleware or endpoint
        """
        return await call_next(request)


def create_middleware_decorator(app: Any) -> Callable:
    """
    Create a middleware decorator for the given app.

    Args:
        app: The ezmcp application

    Returns:
        A decorator function for adding middleware
    """

    def middleware(func: Callable) -> Callable:
        """
        Decorator for adding middleware to the application.

        Args:
            func: The middleware function

        Returns:
            The middleware function
        """

        class CustomMiddleware(EzmcpHTTPMiddleware):
            async def dispatch(
                self,
                request: Request,
                call_next: Callable[[Request], Awaitable[Response]],
            ) -> Response:
                return await func(request, call_next)

        # Add middleware to the app's middleware list
        app.add_middleware(CustomMiddleware)

        return func

    return middleware
