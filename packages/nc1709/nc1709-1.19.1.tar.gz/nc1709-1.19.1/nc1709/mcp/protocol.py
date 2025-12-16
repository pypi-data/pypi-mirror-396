"""
MCP Protocol Definitions
Implements the Model Context Protocol message types and structures
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import json


class MCPMessageType(Enum):
    """MCP message types"""
    # Requests
    INITIALIZE = "initialize"
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    LIST_PROMPTS = "prompts/list"
    GET_PROMPT = "prompts/get"

    # Responses
    RESULT = "result"
    ERROR = "error"

    # Notifications
    NOTIFICATION = "notification"


@dataclass
class MCPMessage:
    """Base MCP message structure"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        data = {"jsonrpc": self.jsonrpc}
        if self.id is not None:
            data["id"] = self.id
        if self.method is not None:
            data["method"] = self.method
        if self.params is not None:
            data["params"] = self.params
        if self.result is not None:
            data["result"] = self.result
        if self.error is not None:
            data["error"] = self.error
        return data

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, data: str) -> "MCPMessage":
        """Parse from JSON string"""
        parsed = json.loads(data)
        return cls(**parsed)

    @classmethod
    def request(cls, id: Union[str, int], method: str, params: Optional[Dict] = None) -> "MCPMessage":
        """Create a request message"""
        return cls(id=id, method=method, params=params)

    @classmethod
    def response(cls, id: Union[str, int], result: Any) -> "MCPMessage":
        """Create a success response"""
        return cls(id=id, result=result)

    @classmethod
    def error_response(cls, id: Union[str, int], code: int, message: str, data: Any = None) -> "MCPMessage":
        """Create an error response"""
        error = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        return cls(id=id, error=error)


@dataclass
class MCPToolParameter:
    """Parameter definition for an MCP tool"""
    name: str
    type: str  # "string", "number", "boolean", "array", "object"
    description: str = ""
    required: bool = False
    default: Any = None

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format"""
        schema = {
            "type": self.type,
            "description": self.description
        }
        if self.default is not None:
            schema["default"] = self.default
        return schema


@dataclass
class MCPTool:
    """Represents an MCP tool (capability)"""
    name: str
    description: str
    parameters: List[MCPToolParameter] = field(default_factory=list)
    handler: Optional[Any] = None  # Callable for local tools

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP tool format"""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }


@dataclass
class MCPResource:
    """Represents an MCP resource"""
    uri: str
    name: str
    description: str = ""
    mimeType: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP resource format"""
        data = {
            "uri": self.uri,
            "name": self.name,
            "description": self.description
        }
        if self.mimeType:
            data["mimeType"] = self.mimeType
        return data


@dataclass
class MCPPrompt:
    """Represents an MCP prompt template"""
    name: str
    description: str
    arguments: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP prompt format"""
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments
        }


@dataclass
class MCPServerInfo:
    """MCP server capabilities and information"""
    name: str
    version: str
    capabilities: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities
        }


@dataclass
class MCPClientInfo:
    """MCP client information"""
    name: str
    version: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version
        }


# Error codes following JSON-RPC 2.0
class MCPErrorCode:
    """Standard MCP error codes"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Custom MCP errors
    TOOL_NOT_FOUND = -32000
    RESOURCE_NOT_FOUND = -32001
    PERMISSION_DENIED = -32002
    EXECUTION_ERROR = -32003
