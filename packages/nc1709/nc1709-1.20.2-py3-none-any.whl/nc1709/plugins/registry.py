"""
Plugin Registry for NC1709
Discovers and catalogs available plugins
"""
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type, Set
from dataclasses import dataclass, field

from .base import Plugin, PluginMetadata, PluginCapability


@dataclass
class PluginInfo:
    """Information about a registered plugin"""
    plugin_class: Type[Plugin]
    metadata: PluginMetadata
    module_path: str
    is_builtin: bool = False


class PluginRegistry:
    """
    Registry for discovering and cataloging plugins.

    Handles plugin discovery from:
    - Built-in plugins (nc1709/plugins/agents/)
    - User plugins (~/.nc1709/plugins/)
    - Project plugins (.nc1709/plugins/)
    """

    def __init__(self):
        """Initialize the registry"""
        self._plugins: Dict[str, PluginInfo] = {}
        self._discovery_paths: List[Path] = []
        self._capabilities_index: Dict[PluginCapability, Set[str]] = {}

    @property
    def plugins(self) -> Dict[str, PluginInfo]:
        """Get all registered plugins"""
        return self._plugins.copy()

    def register(
        self,
        plugin_class: Type[Plugin],
        module_path: str = "",
        is_builtin: bool = False
    ) -> bool:
        """Register a plugin class

        Args:
            plugin_class: The Plugin class to register
            module_path: Path to the module file
            is_builtin: Whether this is a built-in plugin

        Returns:
            True if registered successfully
        """
        try:
            # Create temporary instance to get metadata
            temp_instance = plugin_class.__new__(plugin_class)
            Plugin.__init__(temp_instance, {})

            # Get metadata (may need to handle abstract property)
            if hasattr(plugin_class, 'METADATA'):
                metadata = plugin_class.METADATA
            else:
                metadata = temp_instance.metadata

            plugin_name = metadata.name

            # Check for duplicates
            if plugin_name in self._plugins:
                existing = self._plugins[plugin_name]
                # Allow override only if existing is not builtin
                if existing.is_builtin and not is_builtin:
                    return False

            # Register plugin
            self._plugins[plugin_name] = PluginInfo(
                plugin_class=plugin_class,
                metadata=metadata,
                module_path=module_path,
                is_builtin=is_builtin
            )

            # Index by capabilities
            for capability in metadata.capabilities:
                if capability not in self._capabilities_index:
                    self._capabilities_index[capability] = set()
                self._capabilities_index[capability].add(plugin_name)

            return True

        except Exception as e:
            print(f"Failed to register plugin {plugin_class}: {e}")
            return False

    def unregister(self, plugin_name: str) -> bool:
        """Unregister a plugin

        Args:
            plugin_name: Name of plugin to unregister

        Returns:
            True if unregistered
        """
        if plugin_name not in self._plugins:
            return False

        info = self._plugins[plugin_name]

        # Remove from capabilities index
        for capability in info.metadata.capabilities:
            if capability in self._capabilities_index:
                self._capabilities_index[capability].discard(plugin_name)

        del self._plugins[plugin_name]
        return True

    def get(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin info by name

        Args:
            plugin_name: Plugin name

        Returns:
            PluginInfo or None
        """
        return self._plugins.get(plugin_name)

    def find_by_capability(self, capability: PluginCapability) -> List[PluginInfo]:
        """Find plugins with a specific capability

        Args:
            capability: The capability to search for

        Returns:
            List of matching PluginInfo
        """
        plugin_names = self._capabilities_index.get(capability, set())
        return [self._plugins[name] for name in plugin_names if name in self._plugins]

    def find_by_keyword(self, keyword: str) -> List[PluginInfo]:
        """Find plugins matching a keyword

        Args:
            keyword: Keyword to search

        Returns:
            List of matching PluginInfo
        """
        keyword_lower = keyword.lower()
        results = []

        for info in self._plugins.values():
            # Check name
            if keyword_lower in info.metadata.name.lower():
                results.append(info)
                continue

            # Check description
            if keyword_lower in info.metadata.description.lower():
                results.append(info)
                continue

            # Check keywords
            if any(keyword_lower in kw.lower() for kw in info.metadata.keywords):
                results.append(info)

        return results

    def add_discovery_path(self, path: Path) -> None:
        """Add a path for plugin discovery

        Args:
            path: Directory containing plugins
        """
        if path.is_dir() and path not in self._discovery_paths:
            self._discovery_paths.append(path)

    def discover(self, include_user: bool = True, include_project: bool = True) -> int:
        """Discover and register plugins from configured paths

        Args:
            include_user: Include user plugins (~/.nc1709/plugins)
            include_project: Include project plugins (.nc1709/plugins)

        Returns:
            Number of plugins discovered
        """
        count = 0

        # Built-in plugins
        builtin_path = Path(__file__).parent / "agents"
        if builtin_path.is_dir():
            count += self._discover_from_path(builtin_path, is_builtin=True)

        # User plugins
        if include_user:
            user_path = Path.home() / ".nc1709" / "plugins"
            if user_path.is_dir():
                count += self._discover_from_path(user_path, is_builtin=False)

        # Project plugins
        if include_project:
            project_path = Path.cwd() / ".nc1709" / "plugins"
            if project_path.is_dir():
                count += self._discover_from_path(project_path, is_builtin=False)

        # Custom discovery paths
        for path in self._discovery_paths:
            count += self._discover_from_path(path, is_builtin=False)

        return count

    def _discover_from_path(self, path: Path, is_builtin: bool = False) -> int:
        """Discover plugins from a directory

        Args:
            path: Directory to scan
            is_builtin: Whether these are built-in plugins

        Returns:
            Number of plugins discovered
        """
        count = 0

        for file_path in path.glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            try:
                plugin_class = self._load_plugin_from_file(file_path)
                if plugin_class:
                    if self.register(plugin_class, str(file_path), is_builtin):
                        count += 1
            except Exception as e:
                print(f"Error loading plugin from {file_path}: {e}")

        return count

    def _load_plugin_from_file(self, file_path: Path) -> Optional[Type[Plugin]]:
        """Load a plugin class from a Python file

        Args:
            file_path: Path to the .py file

        Returns:
            Plugin class or None
        """
        module_name = f"nc1709_plugin_{file_path.stem}"

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            del sys.modules[module_name]
            raise e

        # Find Plugin subclass in module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type) and
                issubclass(attr, Plugin) and
                attr is not Plugin and
                not attr.__name__.startswith("_")
            ):
                return attr

        return None

    def list_all(self) -> List[Dict]:
        """List all registered plugins

        Returns:
            List of plugin summaries
        """
        return [
            {
                "name": info.metadata.name,
                "version": info.metadata.version,
                "description": info.metadata.description,
                "capabilities": [c.value for c in info.metadata.capabilities],
                "builtin": info.is_builtin
            }
            for info in self._plugins.values()
        ]

    def get_dependencies(self, plugin_name: str) -> List[str]:
        """Get plugin dependencies

        Args:
            plugin_name: Plugin name

        Returns:
            List of dependency plugin names
        """
        info = self._plugins.get(plugin_name)
        if info:
            return info.metadata.dependencies.copy()
        return []

    def resolve_dependencies(self, plugin_name: str) -> List[str]:
        """Resolve plugin dependencies in load order

        Args:
            plugin_name: Plugin name

        Returns:
            List of plugins in order they should be loaded
        """
        resolved = []
        seen = set()

        def resolve(name: str):
            if name in seen:
                return
            seen.add(name)

            deps = self.get_dependencies(name)
            for dep in deps:
                resolve(dep)

            resolved.append(name)

        resolve(plugin_name)
        return resolved
