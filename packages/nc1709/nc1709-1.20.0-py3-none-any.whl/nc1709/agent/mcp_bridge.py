"""
MCP Bridge

Integrates MCP (Model Context Protocol) servers into the agent's tool registry.
Allows the agent to use tools from external MCP servers.
"""

import asyncio
from typing import Any, Dict, List, Optional

from .tools.base import Tool, ToolResult, ToolParameter, ToolPermission, ToolRegistry


class MCPTool(Tool):
    """
    A tool that wraps an MCP server tool.

    Allows MCP tools to be used seamlessly alongside built-in tools.
    """

    category = "mcp"
    permission = ToolPermission.ASK  # Ask before using MCP tools

    def __init__(
        self,
        name: str,
        description: str,
        parameters: List[ToolParameter],
        mcp_manager,
        server_name: str,
    ):
        """Initialize MCP tool wrapper

        Args:
            name: Tool name
            description: Tool description
            parameters: Tool parameters
            mcp_manager: MCP manager for executing calls
            server_name: Name of the MCP server providing this tool
        """
        super().__init__()
        self.name = name
        self.description = description
        self.parameters = parameters
        self._mcp_manager = mcp_manager
        self._server_name = server_name

    def execute(self, **kwargs) -> ToolResult:
        """Execute the MCP tool"""
        try:
            # Run async MCP call synchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self._mcp_manager.call_tool(self.name, kwargs)
                )
            finally:
                loop.close()

            # Parse MCP result
            if "error" in result:
                return ToolResult(
                    success=False,
                    output="",
                    error=result["error"],
                    target=str(kwargs)[:30],
                )

            # Extract content
            output = ""
            if "content" in result:
                for item in result["content"]:
                    if item.get("type") == "text":
                        output += item.get("text", "")

            return ToolResult(
                success=True,
                output=output or str(result),
                target=str(kwargs)[:30],
                data=result,
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"MCP tool error: {e}",
                target=str(kwargs)[:30],
            )


class MCPBridge:
    """
    Bridge between MCP servers and the agent tool registry.

    Discovers tools from MCP servers and registers them as agent tools.
    """

    def __init__(self, registry: ToolRegistry = None):
        """Initialize the MCP bridge

        Args:
            registry: Tool registry to add MCP tools to
        """
        self.registry = registry or ToolRegistry()
        self._mcp_manager = None
        self._registered_tools: Dict[str, MCPTool] = {}

    def connect_mcp_manager(self, mcp_manager) -> None:
        """Connect to an MCP manager

        Args:
            mcp_manager: MCPManager instance
        """
        self._mcp_manager = mcp_manager

    def discover_and_register_tools(self) -> int:
        """Discover tools from MCP servers and register them

        Returns:
            Number of tools registered
        """
        if not self._mcp_manager:
            return 0

        count = 0

        try:
            # Get all tools from MCP manager
            all_tools = self._mcp_manager.get_all_tools()

            # Register local tools
            for tool in all_tools.get("local", []):
                mcp_tool = self._create_mcp_tool(tool, "local")
                if mcp_tool:
                    self.registry.register(mcp_tool)
                    self._registered_tools[mcp_tool.name] = mcp_tool
                    count += 1

            # Register remote tools
            for tool in all_tools.get("remote", []):
                mcp_tool = self._create_mcp_tool(tool, "remote")
                if mcp_tool:
                    self.registry.register(mcp_tool)
                    self._registered_tools[mcp_tool.name] = mcp_tool
                    count += 1

        except Exception as e:
            print(f"Error discovering MCP tools: {e}")

        return count

    def _create_mcp_tool(self, mcp_tool_def, server_name: str) -> Optional[MCPTool]:
        """Create an MCPTool from an MCP tool definition

        Args:
            mcp_tool_def: MCP tool definition object
            server_name: Name of providing server

        Returns:
            MCPTool instance or None
        """
        try:
            # Extract tool info
            name = mcp_tool_def.name
            description = mcp_tool_def.description or f"MCP tool: {name}"

            # Convert parameters
            parameters = []
            if hasattr(mcp_tool_def, 'parameters') and mcp_tool_def.parameters:
                for param in mcp_tool_def.parameters:
                    parameters.append(ToolParameter(
                        name=param.name,
                        description=param.description or param.name,
                        type=self._map_type(param.type) if hasattr(param, 'type') else "string",
                        required=getattr(param, 'required', True),
                    ))

            # Prefix MCP tool names to avoid conflicts
            prefixed_name = f"mcp_{name}"

            return MCPTool(
                name=prefixed_name,
                description=description,
                parameters=parameters,
                mcp_manager=self._mcp_manager,
                server_name=server_name,
            )

        except Exception as e:
            print(f"Error creating MCP tool: {e}")
            return None

    def _map_type(self, mcp_type: str) -> str:
        """Map MCP type to tool parameter type"""
        type_map = {
            "string": "string",
            "str": "string",
            "int": "integer",
            "integer": "integer",
            "float": "number",
            "number": "number",
            "bool": "boolean",
            "boolean": "boolean",
            "list": "array",
            "array": "array",
            "dict": "object",
            "object": "object",
        }
        return type_map.get(mcp_type.lower(), "string")

    def get_registered_tools(self) -> List[str]:
        """Get list of registered MCP tool names"""
        return list(self._registered_tools.keys())

    def unregister_all(self) -> int:
        """Unregister all MCP tools

        Returns:
            Number of tools unregistered
        """
        count = 0
        for name in list(self._registered_tools.keys()):
            if self.registry.unregister(name):
                count += 1
            del self._registered_tools[name]
        return count


def integrate_mcp_with_agent(agent, mcp_manager) -> MCPBridge:
    """Integrate MCP tools with an agent

    Args:
        agent: Agent instance
        mcp_manager: MCPManager instance

    Returns:
        MCPBridge instance
    """
    bridge = MCPBridge(agent.registry)
    bridge.connect_mcp_manager(mcp_manager)
    count = bridge.discover_and_register_tools()
    print(f"Registered {count} MCP tools with agent")
    return bridge
