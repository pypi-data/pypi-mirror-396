"""
MCP Manager
High-level manager for MCP server and client operations
"""
import asyncio
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path

from .server import MCPServer, ToolResult
from .client import MCPClient
from .protocol import MCPTool, MCPResource, MCPToolParameter


class MCPManager:
    """
    High-level manager for MCP functionality.

    Provides a unified interface for:
    - Running NC1709 as an MCP server
    - Connecting to external MCP servers as a client
    - Managing tools and resources across connections
    """

    def __init__(self, name: str = "nc1709", version: str = "1.0.0"):
        """Initialize the MCP manager

        Args:
            name: Name for the local MCP server
            version: Version for the local MCP server
        """
        self._server = MCPServer(name=name, version=version)
        self._client = MCPClient()
        self._running = False
        self._server_task: Optional[asyncio.Task] = None

    @property
    def server(self) -> MCPServer:
        """Get the local MCP server"""
        return self._server

    @property
    def client(self) -> MCPClient:
        """Get the MCP client"""
        return self._client

    @property
    def is_running(self) -> bool:
        """Check if the server is running"""
        return self._running

    # =========================================================================
    # Server Management
    # =========================================================================

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable,
        parameters: Optional[List[MCPToolParameter]] = None
    ) -> None:
        """Register a tool with the local server

        Args:
            name: Tool name
            description: Tool description
            handler: Tool handler function
            parameters: Tool parameters
        """
        self._server.register_tool(name, description, handler, parameters)

    def register_resource(
        self,
        uri: str,
        name: str,
        description: str = "",
        mime_type: Optional[str] = None
    ) -> None:
        """Register a resource with the local server

        Args:
            uri: Resource URI
            name: Resource name
            description: Resource description
            mime_type: MIME type
        """
        self._server.register_resource(uri, name, description, mime_type)

    def register_prompt(
        self,
        name: str,
        description: str,
        arguments: Optional[List[Dict]] = None
    ) -> None:
        """Register a prompt template

        Args:
            name: Prompt name
            description: Prompt description
            arguments: Prompt arguments
        """
        self._server.register_prompt(name, description, arguments)

    def setup_default_tools(self) -> None:
        """Set up default NC1709 tools on the server"""
        self._server.create_default_tools()

    async def start_server(self) -> None:
        """Start the MCP server"""
        if self._running:
            return

        self._running = True
        self._server_task = asyncio.create_task(self._server.run_stdio())

    async def stop_server(self) -> None:
        """Stop the MCP server"""
        if not self._running:
            return

        self._running = False
        if self._server_task:
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError:
                pass
            self._server_task = None

    # =========================================================================
    # Client Management
    # =========================================================================

    async def connect_server(
        self,
        name: str,
        command: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ) -> bool:
        """Connect to an external MCP server

        Args:
            name: Server name
            command: Command to start the server
            args: Command arguments
            env: Environment variables

        Returns:
            True if connected successfully
        """
        return await self._client.connect(name, command, args, env)

    async def disconnect_server(self, name: str) -> bool:
        """Disconnect from an external MCP server

        Args:
            name: Server name

        Returns:
            True if disconnected
        """
        return await self._client.disconnect(name)

    async def disconnect_all_servers(self) -> None:
        """Disconnect from all external servers"""
        await self._client.disconnect_all()

    async def auto_discover_servers(self, config_path: Optional[str] = None) -> int:
        """Auto-discover and connect to MCP servers from config

        Args:
            config_path: Path to MCP config file

        Returns:
            Number of servers connected
        """
        return await self._client.auto_discover(config_path)

    # =========================================================================
    # Tool Operations
    # =========================================================================

    def get_local_tools(self) -> List[MCPTool]:
        """Get tools registered on the local server

        Returns:
            List of local tools
        """
        return list(self._server._tools.values())

    def get_remote_tools(self, server_name: Optional[str] = None) -> List[MCPTool]:
        """Get tools from connected servers

        Args:
            server_name: Filter by server (None for all)

        Returns:
            List of remote tools
        """
        return self._client.get_tools(server_name)

    def get_all_tools(self) -> Dict[str, List[MCPTool]]:
        """Get all available tools (local and remote)

        Returns:
            Dict with 'local' and 'remote' tool lists
        """
        return {
            "local": self.get_local_tools(),
            "remote": self.get_remote_tools()
        }

    async def call_remote_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call a tool on a remote server

        Args:
            server_name: Server name
            tool_name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        return await self._client.call_tool(server_name, tool_name, arguments)

    async def call_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        server_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call a tool (local or remote)

        Args:
            tool_name: Tool name
            arguments: Tool arguments
            server_name: Server name (None for local)

        Returns:
            Tool result
        """
        if server_name:
            return await self.call_remote_tool(server_name, tool_name, arguments)

        # Call local tool
        if tool_name not in self._server._tools:
            return {"error": f"Tool not found: {tool_name}"}

        tool = self._server._tools[tool_name]
        if tool.handler is None:
            return {"error": f"Tool {tool_name} has no handler"}

        try:
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(**(arguments or {}))
            else:
                result = tool.handler(**(arguments or {}))

            if isinstance(result, ToolResult):
                return {
                    "content": result.content,
                    "isError": result.is_error
                }
            elif isinstance(result, str):
                return {
                    "content": [{"type": "text", "text": result}],
                    "isError": False
                }
            elif isinstance(result, dict):
                return result
            else:
                return {
                    "content": [{"type": "text", "text": str(result)}],
                    "isError": False
                }
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # Resource Operations
    # =========================================================================

    def get_local_resources(self) -> List[MCPResource]:
        """Get resources registered on the local server

        Returns:
            List of local resources
        """
        return list(self._server._resources.values())

    def get_remote_resources(self, server_name: Optional[str] = None) -> List[MCPResource]:
        """Get resources from connected servers

        Args:
            server_name: Filter by server (None for all)

        Returns:
            List of remote resources
        """
        return self._client.get_resources(server_name)

    def get_all_resources(self) -> Dict[str, List[MCPResource]]:
        """Get all available resources (local and remote)

        Returns:
            Dict with 'local' and 'remote' resource lists
        """
        return {
            "local": self.get_local_resources(),
            "remote": self.get_remote_resources()
        }

    async def read_remote_resource(
        self,
        server_name: str,
        uri: str
    ) -> Dict[str, Any]:
        """Read a resource from a remote server

        Args:
            server_name: Server name
            uri: Resource URI

        Returns:
            Resource contents
        """
        return await self._client.read_resource(server_name, uri)

    # =========================================================================
    # Status and Info
    # =========================================================================

    def list_connected_servers(self) -> List[Dict[str, Any]]:
        """List all connected external servers

        Returns:
            List of server info dicts
        """
        return self._client.list_servers()

    def get_status(self) -> Dict[str, Any]:
        """Get overall MCP status

        Returns:
            Status information
        """
        return {
            "server": {
                "name": self._server.name,
                "version": self._server.version,
                "running": self._running,
                "tools": len(self._server._tools),
                "resources": len(self._server._resources),
                "prompts": len(self._server._prompts)
            },
            "client": {
                "connected_servers": len(self._client._servers),
                "servers": self.list_connected_servers()
            }
        }

    # =========================================================================
    # Cleanup
    # =========================================================================

    async def shutdown(self) -> None:
        """Shutdown all MCP connections"""
        await self.stop_server()
        await self.disconnect_all_servers()

    async def __aenter__(self) -> "MCPManager":
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.shutdown()


# Convenience function to create a configured manager
def create_mcp_manager(
    name: str = "nc1709",
    version: str = "1.0.0",
    with_default_tools: bool = True
) -> MCPManager:
    """Create and configure an MCP manager

    Args:
        name: Server name
        version: Server version
        with_default_tools: Whether to register default tools

    Returns:
        Configured MCPManager instance
    """
    manager = MCPManager(name=name, version=version)

    if with_default_tools:
        manager.setup_default_tools()

    return manager
