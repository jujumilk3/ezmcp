import inspect
from typing import (
    Annotated,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    get_type_hints,
)

import mcp.types as mcp_types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import HTMLResponse
from starlette.routing import Mount, Route

from ezmcp.middleware import Middleware, create_middleware_decorator
from ezmcp.templates import (
    DOCS_TEMPLATE,
    FORM_INPUT_TEMPLATE,
    PARAM_ROW_TEMPLATE,
    TOOL_CARD_TEMPLATE,
)
from ezmcp.types import ParamInfo, Response, Tool, ToolFunc


class ezmcp:
    """
    Easy-to-use MCP server framework specialized for SSE.

    Example:
    ```python
    from ezmcp import ezmcp, TextContent

    app = ezmcp("my-app")

    @app.tool("echo")
    async def echo(message: str):
        return [TextContent(type="text", text=f"Echo: {message}")]

    if __name__ == "__main__":
        app.run()
    ```
    """

    def __init__(
        self,
        name: str = "ezmcp-app",
        sse_path: str = "/messages/",
        sse_endpoint: str = "/sse",
        docs_url: str = "/docs",
        debug: bool = False,
    ):
        """
        Initialize the ezmcp application.

        Args:
            name: The name of the MCP server
            sse_path: The path for SSE messages
            sse_endpoint: The endpoint for SSE connections
            docs_url: The URL for the documentation page
            debug: Whether to enable debug mode
        """
        self.name = name
        self.sse_path = sse_path
        self.sse_endpoint = sse_endpoint
        self.docs_url = docs_url
        self.debug = debug

        # Initialize MCP components
        self.sse = SseServerTransport(self.sse_path)
        self.server = Server(self.name)

        # Store registered tools
        self.tools: Dict[str, Dict[str, Any]] = {}

        # Store middleware
        self.user_middleware: List[Middleware] = []

        # Create middleware decorator
        self.middleware = create_middleware_decorator(self)

        # Set up server handlers
        self._setup_server_handlers()

        # Create Starlette app
        self.starlette_app = None

    def add_middleware(
        self, middleware_class: Type[BaseHTTPMiddleware], *args: Any, **kwargs: Any
    ) -> None:
        """
        Add middleware to the application.

        Args:
            middleware_class: The middleware class to add
            *args: Positional arguments to pass to the middleware
            **kwargs: Keyword arguments to pass to the middleware
        """
        self.user_middleware.append(Middleware(middleware_class, *args, **kwargs))
        # Reset starlette_app to ensure middleware is applied
        self.starlette_app = None

    def _setup_server_handlers(self):
        """Set up the MCP server handlers."""

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> Response:
            if name not in self.tools:
                raise ValueError(f"Unknown tool: {name}")

            tool_info = self.tools[name]
            func = tool_info["func"]

            # Map arguments to function parameters
            kwargs = {}
            for param_name, param_info in tool_info["params"].items():
                if param_name in arguments:
                    kwargs[param_name] = arguments[param_name]
                elif param_info.required:
                    raise ValueError(
                        f"Missing required argument '{param_name}' for tool '{name}'"
                    )
                else:
                    kwargs[param_name] = param_info.default

            return await func(**kwargs)

        @self.server.list_tools()
        async def list_tools() -> List[mcp_types.Tool]:
            return [tool_info["schema"] for tool_info in self.tools.values()]

    async def _handle_sse(self, request):
        """Handle SSE connections."""
        async with self.sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await self.server.run(
                streams[0], streams[1], self.server.create_initialization_options()
            )

    async def _handle_docs(self, request):
        """Handle documentation page requests."""
        tools_html = ""

        # Sort tools by name for consistent display
        sorted_tools = sorted(self.tools.items(), key=lambda x: x[0])

        for name, tool_info in sorted_tools:
            schema = tool_info["schema"]
            params = tool_info["params"]

            # Generate parameter rows for the table
            params_rows = ""
            form_inputs = ""

            # Sort parameters to put required ones first
            sorted_params = sorted(
                params.items(), key=lambda x: (not x[1].required, x[0])
            )

            for param_name, param_info in sorted_params:
                # Determine parameter type for display
                if param_info.type in (str, Annotated[str, ...]):
                    type_name = "string"
                    input_type = "text"
                elif param_info.type in (int, Annotated[int, ...]):
                    type_name = "integer"
                    input_type = "number"
                elif param_info.type in (float, Annotated[float, ...]):
                    type_name = "number"
                    input_type = "number"
                elif param_info.type in (bool, Annotated[bool, ...]):
                    type_name = "boolean"
                    input_type = "checkbox"
                else:
                    type_name = "string"
                    input_type = "text"

                # Create parameter row
                required_class = "required" if param_info.required else "optional"
                required_text = "Yes" if param_info.required else "No"

                description = param_info.description or ""
                if not param_info.required and param_info.default is not None:
                    description += f" (Default: {param_info.default})"

                params_rows += PARAM_ROW_TEMPLATE.format(
                    name=param_name,
                    type=type_name,
                    required_class=required_class,
                    required_text=required_text,
                    description=description,
                )

                # Create form input
                required_mark = " *" if param_info.required else ""
                required_attr = "required" if param_info.required else ""

                form_inputs += FORM_INPUT_TEMPLATE.format(
                    name=param_name,
                    tool_name=name,
                    required_mark=required_mark,
                    required_attr=required_attr,
                    input_type=input_type,
                )

            # Create tool card
            tool_card = TOOL_CARD_TEMPLATE.format(
                name=name,
                description=schema.description,
                params_rows=params_rows,
                form_inputs=form_inputs,
            )

            tools_html += tool_card

        # Create documentation page
        html_content = DOCS_TEMPLATE.format(
            app_name=self.name,
            sse_endpoint=self.sse_endpoint,
            sse_path=self.sse_path,
            tools_html=tools_html,
        )

        return HTMLResponse(html_content)

    def _create_starlette_app(self):
        """Create the Starlette application."""
        if self.starlette_app is None:
            routes = [
                Route(self.sse_endpoint, endpoint=self._handle_sse),
                Mount(self.sse_path, app=self.sse.handle_post_message),
            ]

            # Add documentation page if enabled
            if self.docs_url:
                routes.append(Route(self.docs_url, endpoint=self._handle_docs))

            # Create middleware list for Starlette
            middleware = []
            for m in self.user_middleware:
                middleware.append(m)

            self.starlette_app = Starlette(
                debug=self.debug,
                routes=routes,
                middleware=middleware,
            )
        return self.starlette_app

    def _extract_param_info(self, func: Callable) -> Dict[str, ParamInfo]:
        """Extract parameter information from a function."""
        signature = inspect.signature(func)
        type_hints = get_type_hints(func, include_extras=True)

        params = {}
        for name, param in signature.parameters.items():
            # Skip self parameter for methods
            if name == "self":
                continue

            param_type = type_hints.get(name, Any)
            has_default = param.default is not inspect.Parameter.empty
            default_value = param.default if has_default else None

            # Extract description from Annotated type if available
            description = None
            original_type = param_type
            
            # get_type_hints with include_extras=True returns _AnnotatedAlias for Annotated types
            if hasattr(param_type, "__metadata__"):
                metadata = param_type.__metadata__
                if metadata and isinstance(metadata[0], str):
                    description = metadata[0]
                if hasattr(param_type, "__origin__"):
                    param_type = param_type.__origin__
            
            params[name] = ParamInfo(
                name=name,
                type_=original_type,  # 원본 타입 저장 (Annotated 포함)
                required=not has_default,
                description=description,
                default=default_value,
            )

        return params

    def _create_tool_schema(
        self, name: str, description: str, params: Dict[str, ParamInfo]
    ) -> Tool:
        """Create a Tool schema from parameter information."""
        properties = {}
        required = []

        for param_name, param_info in params.items():
            if param_info.required:
                required.append(param_name)

            # Map Python types to JSON Schema types
            if param_info.type in (str, Annotated[str, ...]):
                type_name = "string"
            elif param_info.type in (int, Annotated[int, ...]):
                type_name = "integer"
            elif param_info.type in (float, Annotated[float, ...]):
                type_name = "number"
            elif param_info.type in (bool, Annotated[bool, ...]):
                type_name = "boolean"
            elif param_info.type in (
                list,
                List,
                Annotated[list, ...],
                Annotated[List, ...],
            ):
                type_name = "array"
            elif param_info.type in (
                dict,
                Dict,
                Annotated[dict, ...],
                Annotated[Dict, ...],
            ):
                type_name = "object"
            else:
                type_name = "string"  # Default to string for unknown types

            property_schema = {
                "type": type_name,
            }

            # 파라미터 설명 추가
            if param_info.description:
                property_schema["description"] = param_info.description
            elif hasattr(param_info.type, "__metadata__"):
                # Annotated 타입에서 description 추출 시도
                metadata = param_info.type.__metadata__
                if metadata and isinstance(metadata[0], str):
                    property_schema["description"] = metadata[0]

            properties[param_name] = property_schema

        return Tool(
            name=name,
            description=description,
            inputSchema={
                "type": "object",
                "required": required,
                "properties": properties,
            },
        )

    def tool(self, name: Optional[str] = None, description: Optional[str] = None):
        """
        Decorator to register a function as a tool.

        Args:
            name: The name of the tool (defaults to function name)
            description: The description of the tool (defaults to function docstring)
        """

        def decorator(func: ToolFunc):
            nonlocal name, description

            # Use function name if name not provided
            if name is None:
                name = func.__name__

            # Use function docstring if description not provided
            if description is None:
                description = inspect.getdoc(func) or f"Tool: {name}"

            # Extract parameter information
            params = self._extract_param_info(func)

            # Create tool schema
            schema = self._create_tool_schema(name, description, params)

            # Register tool
            self.tools[name] = {
                "func": func,
                "params": params,
                "schema": schema,
            }

            return func

        return decorator

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run the application with uvicorn.

        Args:
            host: The host to bind to
            port: The port to bind to
        """
        import uvicorn

        app = self._create_starlette_app()
        print(f"Documentation available at: http://{host}:{port}{self.docs_url}")
        uvicorn.run(app, host=host, port=port)

    def get_app(self):
        """Get the Starlette application."""
        return self._create_starlette_app()
