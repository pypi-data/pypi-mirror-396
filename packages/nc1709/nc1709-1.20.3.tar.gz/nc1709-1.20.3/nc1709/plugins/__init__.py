"""
NC1709 Plugin System
Extensible plugin architecture for agents and tools
"""

from .base import Plugin, PluginMetadata, PluginCapability, PluginStatus
from .registry import PluginRegistry
from .manager import PluginManager

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginCapability",
    "PluginStatus",
    "PluginRegistry",
    "PluginManager"
]
