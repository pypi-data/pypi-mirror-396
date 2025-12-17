"""
NC1709 Agent Module

Provides an agentic architecture similar to Claude Code with:
- Tool-based execution (Read, Write, Edit, Grep, Glob, Bash, etc.)
- Sub-agent spawning for complex tasks
- MCP integration for extended capabilities
- Permission system for tool execution
- Real-time visual feedback
"""

from .core import Agent, AgentConfig, create_agent
from .tools.base import Tool, ToolResult, ToolRegistry, ToolPermission, ToolParameter
from .permissions import PermissionManager, PermissionPolicy, PermissionConfig
from .mcp_bridge import MCPBridge, MCPTool, integrate_mcp_with_agent

__all__ = [
    # Core
    "Agent",
    "AgentConfig",
    "create_agent",
    # Tools
    "Tool",
    "ToolResult",
    "ToolRegistry",
    "ToolPermission",
    "ToolParameter",
    # Permissions
    "PermissionManager",
    "PermissionPolicy",
    "PermissionConfig",
    # MCP
    "MCPBridge",
    "MCPTool",
    "integrate_mcp_with_agent",
]
