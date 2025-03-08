from typing import (
    Any,
    Callable,
    List,
    Optional,
    Type,
    Union,
)

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

# Re-export MCP types
__all__ = [
    "TextContent",
    "ImageContent",
    "EmbeddedResource",
    "Tool",
    "Response",
]

# Type alias for response content.
# Because mcp python sdk's CallToolResult is limited to only below types:
# mcp.types.CallToolResult
Response = List[Union[TextContent, ImageContent, EmbeddedResource]]

# Type for tool function
ToolFunc = Callable[..., Response]


# Type for parameter info
class ParamInfo:
    def __init__(
        self,
        name: str,
        type_: Type,
        required: bool = True,
        description: Optional[str] = None,
        default: Any = None,
    ):
        self.name = name
        self.type = type_
        self.required = required
        self.description = description
        self.default = default
