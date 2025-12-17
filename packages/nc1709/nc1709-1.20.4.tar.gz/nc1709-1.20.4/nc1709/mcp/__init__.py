"""
NC1709 MCP (Model Context Protocol) Support
Enables integration with external tools via the MCP standard
"""

from .server import MCPServer
from .client import MCPClient
from .protocol import MCPMessage, MCPTool, MCPResource
from .manager import MCPManager

__all__ = [
    "MCPServer",
    "MCPClient",
    "MCPMessage",
    "MCPTool",
    "MCPResource",
    "MCPManager"
]
