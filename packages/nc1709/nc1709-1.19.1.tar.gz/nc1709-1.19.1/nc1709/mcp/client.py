"""
MCP Client Implementation
Connects to external MCP servers to access their tools
"""
import asyncio
import json
import subprocess
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path

from .protocol import MCPMessage, MCPTool, MCPResource, MCPErrorCode


@dataclass
class MCPServerConnection:
    """Represents a connection to an MCP server"""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    process: Optional[subprocess.Popen] = None
    tools: List[MCPTool] = field(default_factory=list)
    resources: List[MCPResource] = field(default_factory=list)
    connected: bool = False


class MCPClient:
    """
    MCP Client for NC1709.

    Connects to external MCP servers and makes their tools
    available within NC1709.
    """

    def __init__(self):
        """Initialize the MCP client"""
        self._servers: Dict[str, MCPServerConnection] = {}
        self._request_id = 0
        self._pending_requests: Dict[int, asyncio.Future] = {}

    def _next_id(self) -> int:
        """Get next request ID"""
        self._request_id += 1
        return self._request_id

    async def connect(
        self,
        name: str,
        command: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ) -> bool:
        """Connect to an MCP server

        Args:
            name: Server name
            command: Command to start the server
            args: Command arguments
            env: Environment variables

        Returns:
            True if connected successfully
        """
        if name in self._servers and self._servers[name].connected:
            return True

        args = args or []
        env = env or {}

        try:
            # Start the server process
            full_env = {**dict(subprocess.os.environ), **env}
            process = subprocess.Popen(
                [command] + args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=full_env
            )

            connection = MCPServerConnection(
                name=name,
                command=command,
                args=args,
                env=env,
                process=process
            )

            self._servers[name] = connection

            # Initialize the connection
            init_response = await self._send_request(
                name,
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {
                        "name": "nc1709",
                        "version": "1.0.0"
                    },
                    "capabilities": {}
                }
            )

            if init_response and "error" not in init_response:
                connection.connected = True

                # Fetch available tools
                tools_response = await self._send_request(name, "tools/list", {})
                if tools_response and "tools" in tools_response:
                    connection.tools = [
                        MCPTool(
                            name=t["name"],
                            description=t.get("description", ""),
                            parameters=[]  # Parse inputSchema if needed
                        )
                        for t in tools_response["tools"]
                    ]

                # Fetch available resources
                resources_response = await self._send_request(name, "resources/list", {})
                if resources_response and "resources" in resources_response:
                    connection.resources = [
                        MCPResource(
                            uri=r["uri"],
                            name=r["name"],
                            description=r.get("description", "")
                        )
                        for r in resources_response["resources"]
                    ]

                return True

            return False

        except Exception as e:
            print(f"Failed to connect to MCP server {name}: {e}")
            return False

    async def disconnect(self, name: str) -> bool:
        """Disconnect from an MCP server

        Args:
            name: Server name

        Returns:
            True if disconnected
        """
        if name not in self._servers:
            return False

        connection = self._servers[name]

        if connection.process:
            connection.process.terminate()
            try:
                connection.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                connection.process.kill()

        connection.connected = False
        del self._servers[name]
        return True

    async def disconnect_all(self) -> None:
        """Disconnect from all servers"""
        for name in list(self._servers.keys()):
            await self.disconnect(name)

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call a tool on an MCP server

        Args:
            server_name: Server name
            tool_name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        if server_name not in self._servers:
            return {"error": f"Server not connected: {server_name}"}

        connection = self._servers[server_name]
        if not connection.connected:
            return {"error": f"Server not connected: {server_name}"}

        response = await self._send_request(
            server_name,
            "tools/call",
            {
                "name": tool_name,
                "arguments": arguments or {}
            }
        )

        return response or {"error": "No response from server"}

    async def read_resource(
        self,
        server_name: str,
        uri: str
    ) -> Dict[str, Any]:
        """Read a resource from an MCP server

        Args:
            server_name: Server name
            uri: Resource URI

        Returns:
            Resource contents
        """
        if server_name not in self._servers:
            return {"error": f"Server not connected: {server_name}"}

        response = await self._send_request(
            server_name,
            "resources/read",
            {"uri": uri}
        )

        return response or {"error": "No response from server"}

    def list_servers(self) -> List[Dict[str, Any]]:
        """List connected servers

        Returns:
            List of server info dicts
        """
        return [
            {
                "name": name,
                "connected": conn.connected,
                "tools": len(conn.tools),
                "resources": len(conn.resources)
            }
            for name, conn in self._servers.items()
        ]

    def get_tools(self, server_name: Optional[str] = None) -> List[MCPTool]:
        """Get available tools

        Args:
            server_name: Filter by server (None for all)

        Returns:
            List of tools
        """
        if server_name:
            if server_name in self._servers:
                return self._servers[server_name].tools
            return []

        all_tools = []
        for conn in self._servers.values():
            all_tools.extend(conn.tools)
        return all_tools

    def get_resources(self, server_name: Optional[str] = None) -> List[MCPResource]:
        """Get available resources

        Args:
            server_name: Filter by server (None for all)

        Returns:
            List of resources
        """
        if server_name:
            if server_name in self._servers:
                return self._servers[server_name].resources
            return []

        all_resources = []
        for conn in self._servers.values():
            all_resources.extend(conn.resources)
        return all_resources

    async def _send_request(
        self,
        server_name: str,
        method: str,
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Send a request to an MCP server

        Args:
            server_name: Server name
            method: Method name
            params: Request parameters

        Returns:
            Response data or None
        """
        if server_name not in self._servers:
            return None

        connection = self._servers[server_name]
        if not connection.process:
            return None

        request_id = self._next_id()
        request = MCPMessage.request(request_id, method, params)

        try:
            # Send request
            request_json = request.to_json() + "\n"
            connection.process.stdin.write(request_json.encode())
            connection.process.stdin.flush()

            # Read response (with timeout)
            # Note: This is a simplified sync implementation
            # A production version would use proper async I/O
            response_line = connection.process.stdout.readline()
            if response_line:
                response = MCPMessage.from_json(response_line.decode())
                if response.error:
                    return {"error": response.error}
                return response.result

        except Exception as e:
            print(f"Error communicating with MCP server {server_name}: {e}")

        return None

    async def auto_discover(self, config_path: Optional[str] = None) -> int:
        """Auto-discover MCP servers from configuration

        Args:
            config_path: Path to MCP config file

        Returns:
            Number of servers discovered
        """
        if config_path is None:
            # Look for standard config locations
            config_paths = [
                Path.home() / ".nc1709" / "mcp.json",
                Path.cwd() / ".nc1709" / "mcp.json",
                Path.cwd() / "mcp.json"
            ]
        else:
            config_paths = [Path(config_path)]

        count = 0

        for path in config_paths:
            if path.exists():
                try:
                    config = json.loads(path.read_text())
                    servers = config.get("mcpServers", {})

                    for name, server_config in servers.items():
                        command = server_config.get("command")
                        args = server_config.get("args", [])
                        env = server_config.get("env", {})

                        if command:
                            if await self.connect(name, command, args, env):
                                count += 1

                except Exception as e:
                    print(f"Error loading MCP config from {path}: {e}")

        return count
