"""
Base Plugin Classes for NC1709
Defines the plugin interface and core abstractions
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime


class PluginCapability(Enum):
    """Capabilities that plugins can provide"""
    FILE_OPERATIONS = "file_operations"      # Read, write, modify files
    COMMAND_EXECUTION = "command_execution"  # Execute shell commands
    VERSION_CONTROL = "version_control"      # Git operations
    CONTAINER_MANAGEMENT = "container_mgmt"  # Docker operations
    CODE_GENERATION = "code_generation"      # Generate code
    CODE_ANALYSIS = "code_analysis"          # Analyze code
    PROJECT_SCAFFOLDING = "scaffolding"      # Create project structure
    TESTING = "testing"                      # Run tests
    DEPLOYMENT = "deployment"                # Deploy applications
    DATABASE = "database"                    # Database operations
    API_INTERACTION = "api_interaction"      # External API calls
    DOCUMENTATION = "documentation"          # Generate docs


class PluginStatus(Enum):
    """Plugin lifecycle states"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class PluginMetadata:
    """Metadata describing a plugin"""
    name: str
    version: str
    description: str
    author: str = "NC1709 Team"
    capabilities: List[PluginCapability] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Other plugin names
    config_schema: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)  # For discovery
    enabled_by_default: bool = True


@dataclass
class PluginAction:
    """Represents an action a plugin can perform"""
    name: str
    description: str
    handler: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    dangerous: bool = False


@dataclass
class ActionResult:
    """Result of a plugin action"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0

    @classmethod
    def ok(cls, message: str, data: Any = None) -> "ActionResult":
        """Create a successful result"""
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, error: str, message: str = "Action failed") -> "ActionResult":
        """Create a failed result"""
        return cls(success=False, message=message, error=error)


class Plugin(ABC):
    """
    Base class for all NC1709 plugins.

    Plugins extend NC1709's capabilities by providing specialized
    functionality for specific domains (Git, Docker, frameworks, etc.)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the plugin

        Args:
            config: Plugin-specific configuration
        """
        self._config = config or {}
        self._status = PluginStatus.UNLOADED
        self._actions: Dict[str, PluginAction] = {}
        self._error: Optional[str] = None
        self._loaded_at: Optional[datetime] = None

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass

    @property
    def status(self) -> PluginStatus:
        """Get current plugin status"""
        return self._status

    @property
    def config(self) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self._config

    @property
    def actions(self) -> Dict[str, PluginAction]:
        """Get registered actions"""
        return self._actions

    @property
    def error(self) -> Optional[str]:
        """Get last error message"""
        return self._error

    def configure(self, config: Dict[str, Any]) -> bool:
        """Update plugin configuration

        Args:
            config: New configuration values

        Returns:
            True if configuration was updated successfully
        """
        self._config.update(config)
        return self.validate_config()

    def validate_config(self) -> bool:
        """Validate current configuration

        Returns:
            True if configuration is valid
        """
        # Default implementation - override for custom validation
        return True

    def load(self) -> bool:
        """Load and initialize the plugin

        Returns:
            True if loaded successfully
        """
        try:
            self._status = PluginStatus.LOADING

            # Validate configuration
            if not self.validate_config():
                self._status = PluginStatus.ERROR
                self._error = "Invalid configuration"
                return False

            # Check dependencies
            if not self._check_dependencies():
                self._status = PluginStatus.ERROR
                return False

            # Initialize plugin
            if not self.initialize():
                self._status = PluginStatus.ERROR
                return False

            # Register actions
            self._register_actions()

            self._status = PluginStatus.ACTIVE
            self._loaded_at = datetime.now()
            return True

        except Exception as e:
            self._status = PluginStatus.ERROR
            self._error = str(e)
            return False

    def unload(self) -> bool:
        """Unload the plugin and cleanup resources

        Returns:
            True if unloaded successfully
        """
        try:
            self.cleanup()
            self._status = PluginStatus.UNLOADED
            self._actions.clear()
            return True
        except Exception as e:
            self._error = str(e)
            return False

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize plugin resources

        Called during load(). Override to set up connections,
        verify tools are installed, etc.

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources

        Called during unload(). Override to close connections,
        cleanup temp files, etc.
        """
        pass

    @abstractmethod
    def _register_actions(self) -> None:
        """Register available actions

        Override to register PluginAction instances in self._actions
        """
        pass

    def _check_dependencies(self) -> bool:
        """Check if plugin dependencies are available

        Returns:
            True if all dependencies are met
        """
        # This will be enhanced by PluginManager to check other plugins
        return True

    def register_action(
        self,
        name: str,
        handler: Callable,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        requires_confirmation: bool = False,
        dangerous: bool = False
    ) -> None:
        """Register a new action

        Args:
            name: Action name (used for invocation)
            handler: Function to execute
            description: Human-readable description
            parameters: Parameter schema
            requires_confirmation: Whether to ask user before executing
            dangerous: Whether action can cause data loss
        """
        self._actions[name] = PluginAction(
            name=name,
            handler=handler,
            description=description,
            parameters=parameters or {},
            requires_confirmation=requires_confirmation,
            dangerous=dangerous
        )

    def execute(self, action_name: str, **kwargs) -> ActionResult:
        """Execute a plugin action

        Args:
            action_name: Name of the action to execute
            **kwargs: Action parameters

        Returns:
            ActionResult with success/failure info
        """
        if self._status != PluginStatus.ACTIVE:
            return ActionResult.fail(
                f"Plugin not active (status: {self._status.value})"
            )

        if action_name not in self._actions:
            return ActionResult.fail(
                f"Unknown action: {action_name}",
                f"Available actions: {list(self._actions.keys())}"
            )

        action = self._actions[action_name]

        try:
            import time
            start = time.time()
            result = action.handler(**kwargs)
            elapsed = time.time() - start

            if isinstance(result, ActionResult):
                result.execution_time = elapsed
                return result

            # If handler returns something else, wrap it
            return ActionResult.ok(
                message=f"Action '{action_name}' completed",
                data=result
            )

        except Exception as e:
            return ActionResult.fail(
                error=str(e),
                message=f"Action '{action_name}' failed"
            )

    def can_handle(self, request: str) -> float:
        """Check if plugin can handle a user request

        Args:
            request: User's natural language request

        Returns:
            Confidence score 0.0-1.0 (0 = cannot handle)
        """
        # Default implementation uses keyword matching
        request_lower = request.lower()
        score = 0.0

        for keyword in self.metadata.keywords:
            if keyword.lower() in request_lower:
                score += 0.2

        return min(score, 1.0)

    def get_help(self) -> str:
        """Get plugin help text

        Returns:
            Formatted help string
        """
        lines = [
            f"# {self.metadata.name} v{self.metadata.version}",
            f"",
            f"{self.metadata.description}",
            f"",
            f"## Capabilities",
        ]

        for cap in self.metadata.capabilities:
            lines.append(f"  - {cap.value}")

        if self._actions:
            lines.append("")
            lines.append("## Available Actions")
            for name, action in self._actions.items():
                lines.append(f"  - **{name}**: {action.description}")
                if action.dangerous:
                    lines.append(f"    ⚠️  This action can modify/delete data")

        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"<Plugin {self.metadata.name} v{self.metadata.version} [{self._status.value}]>"
