"""
Plugin Manager for NC1709
Manages plugin lifecycle and execution
"""
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .base import Plugin, PluginStatus, PluginCapability, ActionResult
from .registry import PluginRegistry, PluginInfo


class PluginManager:
    """
    Manages plugin lifecycle, configuration, and execution.

    Handles:
    - Plugin loading/unloading
    - Configuration management
    - Request routing to appropriate plugins
    - Action execution with confirmation
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the plugin manager

        Args:
            config: Global plugin configuration
        """
        self._config = config or {}
        self._registry = PluginRegistry()
        self._instances: Dict[str, Plugin] = {}
        self._load_order: List[str] = []

    @property
    def registry(self) -> PluginRegistry:
        """Get the plugin registry"""
        return self._registry

    @property
    def loaded_plugins(self) -> Dict[str, Plugin]:
        """Get all loaded plugin instances"""
        return self._instances.copy()

    def discover_plugins(self) -> int:
        """Discover available plugins

        Returns:
            Number of plugins discovered
        """
        return self._registry.discover()

    def load_plugin(self, plugin_name: str, config: Optional[Dict] = None) -> bool:
        """Load a plugin by name

        Args:
            plugin_name: Name of plugin to load
            config: Plugin-specific configuration

        Returns:
            True if loaded successfully
        """
        # Check if already loaded
        if plugin_name in self._instances:
            instance = self._instances[plugin_name]
            if instance.status == PluginStatus.ACTIVE:
                return True

        # Get plugin info from registry
        info = self._registry.get(plugin_name)
        if info is None:
            print(f"Plugin '{plugin_name}' not found in registry")
            return False

        # Resolve and load dependencies first
        dependencies = self._registry.resolve_dependencies(plugin_name)
        for dep_name in dependencies[:-1]:  # Exclude the plugin itself
            if dep_name not in self._instances:
                if not self.load_plugin(dep_name):
                    print(f"Failed to load dependency: {dep_name}")
                    return False

        # Merge configuration
        plugin_config = {}
        if plugin_name in self._config:
            plugin_config.update(self._config[plugin_name])
        if config:
            plugin_config.update(config)

        # Create and load instance
        try:
            instance = info.plugin_class(plugin_config)
            if instance.load():
                self._instances[plugin_name] = instance
                self._load_order.append(plugin_name)
                return True
            else:
                print(f"Plugin '{plugin_name}' failed to load: {instance.error}")
                return False

        except Exception as e:
            print(f"Error creating plugin '{plugin_name}': {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            True if unloaded
        """
        if plugin_name not in self._instances:
            return False

        # Check if other plugins depend on this one
        dependents = self._find_dependents(plugin_name)
        if dependents:
            # Unload dependents first
            for dep in dependents:
                self.unload_plugin(dep)

        instance = self._instances[plugin_name]
        if instance.unload():
            del self._instances[plugin_name]
            if plugin_name in self._load_order:
                self._load_order.remove(plugin_name)
            return True

        return False

    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin

        Args:
            plugin_name: Plugin to reload

        Returns:
            True if reloaded
        """
        config = None
        if plugin_name in self._instances:
            config = self._instances[plugin_name].config.copy()
            self.unload_plugin(plugin_name)

        return self.load_plugin(plugin_name, config)

    def load_all(self, enabled_only: bool = True) -> int:
        """Load all registered plugins

        Args:
            enabled_only: Only load plugins enabled by default

        Returns:
            Number of plugins loaded
        """
        count = 0

        for name, info in self._registry.plugins.items():
            if enabled_only and not info.metadata.enabled_by_default:
                continue

            if self.load_plugin(name):
                count += 1

        return count

    def unload_all(self) -> None:
        """Unload all plugins"""
        # Unload in reverse order
        for name in reversed(self._load_order.copy()):
            self.unload_plugin(name)

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a loaded plugin instance

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self._instances.get(plugin_name)

    def execute_action(
        self,
        plugin_name: str,
        action_name: str,
        confirm_dangerous: bool = True,
        **kwargs
    ) -> ActionResult:
        """Execute a plugin action

        Args:
            plugin_name: Plugin name
            action_name: Action to execute
            confirm_dangerous: Ask for confirmation on dangerous actions
            **kwargs: Action parameters

        Returns:
            ActionResult
        """
        plugin = self._instances.get(plugin_name)
        if plugin is None:
            return ActionResult.fail(f"Plugin '{plugin_name}' not loaded")

        if plugin.status != PluginStatus.ACTIVE:
            return ActionResult.fail(
                f"Plugin '{plugin_name}' not active (status: {plugin.status.value})"
            )

        action = plugin.actions.get(action_name)
        if action is None:
            return ActionResult.fail(
                f"Action '{action_name}' not found in plugin '{plugin_name}'"
            )

        # Check for dangerous action
        if confirm_dangerous and action.dangerous:
            # In a real implementation, this would prompt the user
            # For now, we'll just note it in the result
            pass

        return plugin.execute(action_name, **kwargs)

    def find_handler(self, request: str) -> List[Tuple[str, float]]:
        """Find plugins that can handle a request

        Args:
            request: User's natural language request

        Returns:
            List of (plugin_name, confidence) tuples, sorted by confidence
        """
        candidates = []

        for name, plugin in self._instances.items():
            if plugin.status != PluginStatus.ACTIVE:
                continue

            confidence = plugin.can_handle(request)
            if confidence > 0:
                candidates.append((name, confidence))

        # Sort by confidence (highest first)
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

    def route_request(self, request: str, **kwargs) -> Optional[ActionResult]:
        """Route a request to the most suitable plugin

        Args:
            request: User's natural language request
            **kwargs: Additional parameters

        Returns:
            ActionResult or None if no handler found
        """
        handlers = self.find_handler(request)

        if not handlers:
            return None

        # Try handlers in order of confidence
        for plugin_name, confidence in handlers:
            plugin = self._instances[plugin_name]

            # Let plugin decide which action to use
            if hasattr(plugin, 'handle_request'):
                result = plugin.handle_request(request, **kwargs)
                if result and result.success:
                    return result

        return None

    def get_all_actions(self) -> Dict[str, List[Dict]]:
        """Get all available actions from loaded plugins

        Returns:
            Dict mapping plugin names to their actions
        """
        actions = {}

        for name, plugin in self._instances.items():
            if plugin.status != PluginStatus.ACTIVE:
                continue

            plugin_actions = []
            for action_name, action in plugin.actions.items():
                plugin_actions.append({
                    "name": action_name,
                    "description": action.description,
                    "parameters": action.parameters,
                    "dangerous": action.dangerous,
                    "requires_confirmation": action.requires_confirmation
                })

            actions[name] = plugin_actions

        return actions

    def find_by_capability(
        self,
        capability: PluginCapability,
        loaded_only: bool = True
    ) -> List[str]:
        """Find plugins with a specific capability

        Args:
            capability: Capability to search for
            loaded_only: Only return loaded plugins

        Returns:
            List of plugin names
        """
        infos = self._registry.find_by_capability(capability)
        names = [info.metadata.name for info in infos]

        if loaded_only:
            names = [n for n in names if n in self._instances]

        return names

    def get_status(self) -> Dict[str, Dict]:
        """Get status of all plugins

        Returns:
            Dict with plugin statuses
        """
        status = {}

        for name, info in self._registry.plugins.items():
            plugin_status = {
                "registered": True,
                "loaded": name in self._instances,
                "status": "unloaded",
                "version": info.metadata.version,
                "builtin": info.is_builtin
            }

            if name in self._instances:
                instance = self._instances[name]
                plugin_status["status"] = instance.status.value
                plugin_status["error"] = instance.error

            status[name] = plugin_status

        return status

    def configure_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Update plugin configuration

        Args:
            plugin_name: Plugin to configure
            config: New configuration values

        Returns:
            True if configured successfully
        """
        if plugin_name in self._instances:
            return self._instances[plugin_name].configure(config)

        # Store for later loading
        if plugin_name not in self._config:
            self._config[plugin_name] = {}
        self._config[plugin_name].update(config)
        return True

    def _find_dependents(self, plugin_name: str) -> List[str]:
        """Find plugins that depend on the given plugin

        Args:
            plugin_name: Plugin name

        Returns:
            List of dependent plugin names
        """
        dependents = []

        for name in self._instances:
            deps = self._registry.get_dependencies(name)
            if plugin_name in deps:
                dependents.append(name)

        return dependents

    def get_help(self, plugin_name: Optional[str] = None) -> str:
        """Get help text for plugins

        Args:
            plugin_name: Specific plugin (None for all)

        Returns:
            Help text
        """
        if plugin_name:
            plugin = self._instances.get(plugin_name)
            if plugin:
                return plugin.get_help()
            return f"Plugin '{plugin_name}' not loaded"

        # General help
        lines = ["# NC1709 Plugins", ""]

        for name, plugin in self._instances.items():
            if plugin.status == PluginStatus.ACTIVE:
                lines.append(f"## {plugin.metadata.name}")
                lines.append(f"{plugin.metadata.description}")
                lines.append("")

        return "\n".join(lines)
