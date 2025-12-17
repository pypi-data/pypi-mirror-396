"""
MCP Server Implementation
Exposes NC1709 capabilities as an MCP server
"""
import asyncio
import json
import sys
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass

from .protocol import (
    MCPMessage, MCPTool, MCPResource, MCPPrompt,
    MCPServerInfo, MCPErrorCode, MCPToolParameter
)


@dataclass
class ToolResult:
    """Result from tool execution"""
    content: List[Dict[str, Any]]
    is_error: bool = False


class MCPServer:
    """
    MCP Server for NC1709.

    Exposes NC1709's capabilities through the Model Context Protocol,
    allowing external AI applications to use NC1709 as a tool provider.
    """

    def __init__(self, name: str = "nc1709", version: str = "1.0.0"):
        """Initialize the MCP server

        Args:
            name: Server name
            version: Server version
        """
        self.name = name
        self.version = version
        self._tools: Dict[str, MCPTool] = {}
        self._resources: Dict[str, MCPResource] = {}
        self._prompts: Dict[str, MCPPrompt] = {}
        self._request_id = 0
        self._initialized = False

    @property
    def server_info(self) -> MCPServerInfo:
        """Get server information"""
        return MCPServerInfo(
            name=self.name,
            version=self.version,
            capabilities={
                "tools": {"listChanged": True},
                "resources": {"subscribe": False, "listChanged": True},
                "prompts": {"listChanged": True}
            }
        )

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable,
        parameters: Optional[List[MCPToolParameter]] = None
    ) -> None:
        """Register a tool with the server

        Args:
            name: Tool name
            description: Tool description
            handler: Function to handle tool calls
            parameters: Tool parameters
        """
        tool = MCPTool(
            name=name,
            description=description,
            parameters=parameters or [],
            handler=handler
        )
        self._tools[name] = tool

    def register_resource(
        self,
        uri: str,
        name: str,
        description: str = "",
        mime_type: Optional[str] = None
    ) -> None:
        """Register a resource

        Args:
            uri: Resource URI
            name: Resource name
            description: Resource description
            mime_type: MIME type
        """
        resource = MCPResource(
            uri=uri,
            name=name,
            description=description,
            mimeType=mime_type
        )
        self._resources[uri] = resource

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
        prompt = MCPPrompt(
            name=name,
            description=description,
            arguments=arguments or []
        )
        self._prompts[name] = prompt

    async def handle_message(self, message: MCPMessage) -> MCPMessage:
        """Handle an incoming MCP message

        Args:
            message: Incoming message

        Returns:
            Response message
        """
        method = message.method
        params = message.params or {}
        msg_id = message.id

        try:
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "tools/list":
                result = self._handle_list_tools()
            elif method == "tools/call":
                result = await self._handle_call_tool(params)
            elif method == "resources/list":
                result = self._handle_list_resources()
            elif method == "resources/read":
                result = await self._handle_read_resource(params)
            elif method == "prompts/list":
                result = self._handle_list_prompts()
            elif method == "prompts/get":
                result = self._handle_get_prompt(params)
            else:
                return MCPMessage.error_response(
                    msg_id,
                    MCPErrorCode.METHOD_NOT_FOUND,
                    f"Unknown method: {method}"
                )

            return MCPMessage.response(msg_id, result)

        except Exception as e:
            return MCPMessage.error_response(
                msg_id,
                MCPErrorCode.INTERNAL_ERROR,
                str(e)
            )

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request"""
        self._initialized = True
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": self.server_info.to_dict(),
            "capabilities": self.server_info.capabilities
        }

    def _handle_list_tools(self) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "tools": [tool.to_dict() for tool in self._tools.values()]
        }

    async def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self._tools:
            raise ValueError(f"Tool not found: {tool_name}")

        tool = self._tools[tool_name]

        if tool.handler is None:
            raise ValueError(f"Tool {tool_name} has no handler")

        # Call the handler
        if asyncio.iscoroutinefunction(tool.handler):
            result = await tool.handler(**arguments)
        else:
            result = tool.handler(**arguments)

        # Format result
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
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                "isError": False
            }
        else:
            return {
                "content": [{"type": "text", "text": str(result)}],
                "isError": False
            }

    def _handle_list_resources(self) -> Dict[str, Any]:
        """Handle resources/list request"""
        return {
            "resources": [res.to_dict() for res in self._resources.values()]
        }

    async def _handle_read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")

        if uri not in self._resources:
            raise ValueError(f"Resource not found: {uri}")

        # Read resource content based on URI scheme
        resource = self._resources[uri]

        if uri.startswith("file://"):
            file_path = uri[7:]
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                return {
                    "contents": [{
                        "uri": uri,
                        "mimeType": resource.mimeType or "text/plain",
                        "text": content
                    }]
                }
            except Exception as e:
                raise ValueError(f"Could not read file: {e}")

        raise ValueError(f"Unsupported URI scheme: {uri}")

    def _handle_list_prompts(self) -> Dict[str, Any]:
        """Handle prompts/list request"""
        return {
            "prompts": [prompt.to_dict() for prompt in self._prompts.values()]
        }

    def _handle_get_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/get request"""
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name not in self._prompts:
            raise ValueError(f"Prompt not found: {name}")

        prompt = self._prompts[name]

        # Generate prompt messages based on template
        # This is a simple implementation - could be enhanced
        return {
            "description": prompt.description,
            "messages": [{
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Prompt: {name}"
                }
            }]
        }

    async def run_stdio(self) -> None:
        """Run the server using stdio transport"""
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)

        await asyncio.get_event_loop().connect_read_pipe(
            lambda: protocol, sys.stdin
        )

        writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout
        )
        writer = asyncio.StreamWriter(
            writer_transport, writer_protocol, reader, asyncio.get_event_loop()
        )

        while True:
            try:
                line = await reader.readline()
                if not line:
                    break

                message = MCPMessage.from_json(line.decode())
                response = await self.handle_message(message)

                writer.write((response.to_json() + "\n").encode())
                await writer.drain()

            except Exception as e:
                error_response = MCPMessage.error_response(
                    None,
                    MCPErrorCode.PARSE_ERROR,
                    str(e)
                )
                writer.write((error_response.to_json() + "\n").encode())
                await writer.drain()

    def create_default_tools(self) -> None:
        """Register default NC1709 tools"""

        # File read tool
        self.register_tool(
            name="read_file",
            description="Read contents of a file",
            handler=self._tool_read_file,
            parameters=[
                MCPToolParameter(
                    name="path",
                    type="string",
                    description="Path to the file to read",
                    required=True
                )
            ]
        )

        # File write tool
        self.register_tool(
            name="write_file",
            description="Write contents to a file",
            handler=self._tool_write_file,
            parameters=[
                MCPToolParameter(
                    name="path",
                    type="string",
                    description="Path to the file to write",
                    required=True
                ),
                MCPToolParameter(
                    name="content",
                    type="string",
                    description="Content to write",
                    required=True
                )
            ]
        )

        # Execute command tool
        self.register_tool(
            name="execute_command",
            description="Execute a shell command",
            handler=self._tool_execute_command,
            parameters=[
                MCPToolParameter(
                    name="command",
                    type="string",
                    description="Command to execute",
                    required=True
                )
            ]
        )

        # Search code tool
        self.register_tool(
            name="search_code",
            description="Search for code patterns in the project",
            handler=self._tool_search_code,
            parameters=[
                MCPToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True
                ),
                MCPToolParameter(
                    name="file_pattern",
                    type="string",
                    description="File pattern to search (e.g., *.py)",
                    required=False
                )
            ]
        )

    async def _tool_read_file(self, path: str) -> str:
        """Read file contents"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return ToolResult(
                content=[{"type": "text", "text": f"Error reading file: {e}"}],
                is_error=True
            )

    async def _tool_write_file(self, path: str, content: str) -> str:
        """Write file contents"""
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return ToolResult(
                content=[{"type": "text", "text": f"Error writing file: {e}"}],
                is_error=True
            )

    async def _tool_execute_command(self, command: str) -> str:
        """Execute a command"""
        import subprocess

        # Security check - block dangerous commands
        dangerous = ["rm -rf", "sudo", "mkfs", "dd if=", "> /dev/"]
        for d in dangerous:
            if d in command:
                return ToolResult(
                    content=[{"type": "text", "text": f"Command blocked for safety: contains '{d}'"}],
                    is_error=True
                )

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
            return output if output else "Command completed with no output"
        except subprocess.TimeoutExpired:
            return ToolResult(
                content=[{"type": "text", "text": "Command timed out"}],
                is_error=True
            )
        except Exception as e:
            return ToolResult(
                content=[{"type": "text", "text": f"Error executing command: {e}"}],
                is_error=True
            )

    async def _tool_search_code(self, query: str, file_pattern: str = "*") -> str:
        """Search for code"""
        import subprocess

        try:
            # Use grep for searching
            cmd = f"grep -r -n '{query}' --include='{file_pattern}' ."
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout if result.stdout else "No matches found"
        except Exception as e:
            return f"Search error: {e}"
