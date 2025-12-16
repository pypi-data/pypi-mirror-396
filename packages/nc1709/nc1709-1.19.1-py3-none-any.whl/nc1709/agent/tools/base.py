"""
Tool Base Classes and Registry

Provides the foundation for the agentic tool system:
- Tool: Base class for all tools
- ToolResult: Standard result format
- ToolRegistry: Central tool management
- ToolPermission: Permission levels for tools
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union
import time


class ToolPermission(Enum):
    """Permission levels for tool execution"""
    AUTO = "auto"           # Execute without asking
    ASK = "ask"             # Ask user before executing
    DENY = "deny"           # Never allow execution
    ASK_ONCE = "ask_once"   # Ask once per session, then auto


@dataclass
class ToolParameter:
    """Definition of a tool parameter"""
    name: str
    description: str
    type: str = "string"  # string, integer, number, boolean, array, object
    required: bool = True
    default: Any = None
    enum: Optional[List[str]] = None

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format for LLM tool calling"""
        schema = {
            "type": self.type,
            "description": self.description,
        }
        if self.enum:
            schema["enum"] = self.enum
        if self.default is not None:
            schema["default"] = self.default
        return schema


@dataclass
class ToolResult:
    """Standard result format for tool execution"""
    success: bool
    output: str
    error: Optional[str] = None
    data: Any = None
    duration_ms: float = 0
    tool_name: str = ""
    target: str = ""

    def to_message(self) -> str:
        """Convert to a message suitable for LLM context"""
        if self.success:
            return self.output
        else:
            return f"Error: {self.error or 'Unknown error'}\n{self.output}"

    def __str__(self) -> str:
        if self.success:
            return f"✓ {self.tool_name}({self.target}) - {len(self.output)} chars"
        else:
            return f"✗ {self.tool_name}({self.target}) - {self.error}"


class Tool(ABC):
    """
    Base class for all agent tools.

    To create a new tool:
    1. Inherit from Tool
    2. Set name, description, parameters
    3. Implement execute() method

    Example:
        class ReadTool(Tool):
            name = "Read"
            description = "Read contents of a file"
            parameters = [
                ToolParameter("file_path", "Path to file", required=True),
                ToolParameter("limit", "Max lines to read", type="integer", required=False),
            ]

            def execute(self, file_path: str, limit: int = None) -> ToolResult:
                # Implementation here
                pass
    """

    # Class attributes to be overridden by subclasses
    name: str = "BaseTool"
    description: str = "Base tool class"
    parameters: List[ToolParameter] = []
    permission: ToolPermission = ToolPermission.ASK
    category: str = "general"

    def __init__(self):
        """Initialize the tool"""
        self._approved_once = False

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult with success status and output
        """
        pass

    def validate_params(self, **kwargs) -> Optional[str]:
        """
        Validate parameters before execution.

        Args:
            **kwargs: Parameters to validate

        Returns:
            Error message if validation fails, None if OK
        """
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                return f"Missing required parameter: {param.name}"

            if param.name in kwargs:
                value = kwargs[param.name]
                # Type validation
                if param.type == "integer" and not isinstance(value, int):
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        return f"Parameter '{param.name}' must be an integer"
                elif param.type == "number" and not isinstance(value, (int, float)):
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        return f"Parameter '{param.name}' must be a number"
                elif param.type == "boolean" and not isinstance(value, bool):
                    return f"Parameter '{param.name}' must be a boolean"

                # Enum validation
                if param.enum and value not in param.enum:
                    return f"Parameter '{param.name}' must be one of: {param.enum}"

        return None

    def run(self, **kwargs) -> ToolResult:
        """
        Run the tool with validation and timing.

        Args:
            **kwargs: Tool parameters

        Returns:
            ToolResult with timing information
        """
        # Validate parameters
        error = self.validate_params(**kwargs)
        if error:
            return ToolResult(
                success=False,
                output="",
                error=error,
                tool_name=self.name,
                target=self._get_target(**kwargs),
            )

        # Execute with timing
        start_time = time.time()
        try:
            result = self.execute(**kwargs)
            result.duration_ms = (time.time() - start_time) * 1000
            result.tool_name = self.name
            result.target = result.target or self._get_target(**kwargs)
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
                tool_name=self.name,
                target=self._get_target(**kwargs),
            )

    def _get_target(self, **kwargs) -> str:
        """Get a short target description for display"""
        # Use first required parameter as target
        for param in self.parameters:
            if param.required and param.name in kwargs:
                value = str(kwargs[param.name])
                if len(value) > 40:
                    value = value[:37] + "..."
                return value
        return ""

    def to_function_schema(self) -> Dict[str, Any]:
        """
        Convert tool to OpenAI-style function schema for LLM tool calling.

        Returns:
            Dict suitable for LLM function calling API
        """
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        }

    def get_help(self) -> str:
        """Get help text for this tool"""
        lines = [
            f"Tool: {self.name}",
            f"Description: {self.description}",
            f"Permission: {self.permission.value}",
            "",
            "Parameters:",
        ]
        for param in self.parameters:
            req = "(required)" if param.required else "(optional)"
            lines.append(f"  {param.name} [{param.type}] {req}")
            lines.append(f"    {param.description}")
            if param.default is not None:
                lines.append(f"    Default: {param.default}")
            if param.enum:
                lines.append(f"    Options: {', '.join(param.enum)}")

        return "\n".join(lines)


class ToolRegistry:
    """
    Central registry for all available tools.

    Manages tool registration, lookup, and permission checking.
    """

    def __init__(self):
        """Initialize the registry"""
        self._tools: Dict[str, Tool] = {}
        self._permission_overrides: Dict[str, ToolPermission] = {}
        self._session_approvals: set = set()  # Tools approved for this session

    def register(self, tool: Tool) -> None:
        """
        Register a tool.

        Args:
            tool: Tool instance to register
        """
        self._tools[tool.name] = tool

    def register_class(self, tool_class: Type[Tool]) -> None:
        """
        Register a tool class (will be instantiated).

        Args:
            tool_class: Tool class to register
        """
        tool = tool_class()
        self.register(tool)

    def unregister(self, name: str) -> bool:
        """
        Unregister a tool by name.

        Args:
            name: Tool name

        Returns:
            True if tool was removed, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None
        """
        return self._tools.get(name)

    def get_all(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self._tools.values())

    def get_by_category(self, category: str) -> List[Tool]:
        """Get all tools in a category"""
        return [t for t in self._tools.values() if t.category == category]

    def list_names(self) -> List[str]:
        """Get list of all tool names"""
        return list(self._tools.keys())

    def set_permission(self, tool_name: str, permission: ToolPermission) -> None:
        """
        Override permission for a specific tool.

        Args:
            tool_name: Name of tool
            permission: New permission level
        """
        self._permission_overrides[tool_name] = permission

    def get_permission(self, tool_name: str) -> ToolPermission:
        """
        Get effective permission for a tool.

        Args:
            tool_name: Name of tool

        Returns:
            Effective permission level
        """
        # Check overrides first
        if tool_name in self._permission_overrides:
            return self._permission_overrides[tool_name]

        # Check tool's default
        tool = self.get(tool_name)
        if tool:
            return tool.permission

        return ToolPermission.DENY

    def needs_approval(self, tool_name: str) -> bool:
        """
        Check if a tool needs user approval to run.

        Args:
            tool_name: Name of tool

        Returns:
            True if approval is needed
        """
        # Check session approvals first - if user said "always", skip approval
        if tool_name in self._session_approvals:
            return False

        permission = self.get_permission(tool_name)

        if permission == ToolPermission.AUTO:
            return False
        elif permission == ToolPermission.DENY:
            return True  # Will be denied anyway
        else:  # ASK or ASK_ONCE
            return True

    def approve_for_session(self, tool_name: str) -> None:
        """Mark a tool as approved for this session"""
        self._session_approvals.add(tool_name)

    def clear_session_approvals(self) -> None:
        """Clear all session approvals"""
        self._session_approvals.clear()

    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """
        Get all tools as OpenAI-style function schemas.

        Returns:
            List of function schemas for LLM tool calling
        """
        return [tool.to_function_schema() for tool in self._tools.values()]

    def get_tools_prompt(self) -> str:
        """
        Generate a tools description for LLMs that don't support function calling.

        Returns:
            Text description of available tools
        """
        lines = ["Available tools:"]
        for tool in self._tools.values():
            lines.append(f"\n## {tool.name}")
            lines.append(f"{tool.description}")
            lines.append("Parameters:")
            for param in tool.parameters:
                req = "(required)" if param.required else "(optional)"
                lines.append(f"  - {param.name}: {param.description} {req}")

        lines.append("\n\nTo use a tool, respond with:")
        lines.append("```tool")
        lines.append('{"tool": "ToolName", "parameters": {"param1": "value1"}}')
        lines.append("```")

        return "\n".join(lines)


# Global default registry
_default_registry: Optional[ToolRegistry] = None


def get_default_registry() -> ToolRegistry:
    """Get or create the default tool registry"""
    global _default_registry
    if _default_registry is None:
        _default_registry = ToolRegistry()
    return _default_registry


def register_tool(tool: Tool) -> None:
    """Register a tool in the default registry"""
    get_default_registry().register(tool)


def register_tool_class(tool_class: Type[Tool]) -> None:
    """Register a tool class in the default registry"""
    get_default_registry().register_class(tool_class)
