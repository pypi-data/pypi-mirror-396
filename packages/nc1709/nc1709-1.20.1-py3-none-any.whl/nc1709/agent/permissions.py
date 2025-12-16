"""
Tool Permissions System

Manages permissions for tool execution with configurable policies.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

from .tools.base import ToolPermission, ToolRegistry


class PermissionPolicy(Enum):
    """Permission policies for different contexts"""
    STRICT = "strict"       # Ask for everything
    NORMAL = "normal"       # Ask for writes/executes, auto for reads
    PERMISSIVE = "permissive"  # Auto-approve most, ask for dangerous
    TRUST = "trust"         # Auto-approve everything


@dataclass
class PermissionRule:
    """A rule for tool permissions"""
    tool_pattern: str  # Tool name or pattern (supports wildcards)
    permission: ToolPermission
    reason: Optional[str] = None


@dataclass
class PermissionConfig:
    """Configuration for the permissions system"""
    policy: PermissionPolicy = PermissionPolicy.PERMISSIVE  # Default to permissive for better UX
    custom_rules: List[PermissionRule] = field(default_factory=list)
    blocked_tools: Set[str] = field(default_factory=set)
    session_approvals: Set[str] = field(default_factory=set)


class PermissionManager:
    """
    Manages tool permissions with configurable policies.

    Provides:
    - Policy-based default permissions
    - Custom per-tool rules
    - Session-level approvals
    - Blocking of dangerous tools
    """

    # Default permissions by policy
    POLICY_DEFAULTS = {
        PermissionPolicy.STRICT: {
            "default": ToolPermission.ASK,
            "auto": [],
        },
        PermissionPolicy.NORMAL: {
            "default": ToolPermission.ASK,
            "auto": ["Read", "Glob", "Grep", "Ripgrep", "TodoWrite"],
        },
        PermissionPolicy.PERMISSIVE: {
            "default": ToolPermission.AUTO,
            "ask": ["Write", "Edit"],  # Only ask for file modifications, auto-approve Bash/Task
        },
        PermissionPolicy.TRUST: {
            "default": ToolPermission.AUTO,
            "ask": [],
        },
    }

    def __init__(self, config: PermissionConfig = None):
        """Initialize the permission manager

        Args:
            config: Permission configuration
        """
        self.config = config or PermissionConfig()
        self._registry: Optional[ToolRegistry] = None

    def attach_registry(self, registry: ToolRegistry) -> None:
        """Attach a tool registry and apply permissions

        Args:
            registry: Tool registry to manage
        """
        self._registry = registry
        self._apply_policy()
        self._apply_custom_rules()

    def _apply_policy(self) -> None:
        """Apply the current policy to the registry"""
        if not self._registry:
            return

        policy_config = self.POLICY_DEFAULTS.get(self.config.policy, {})
        default_perm = policy_config.get("default", ToolPermission.ASK)

        # Set default for all tools
        for tool_name in self._registry.list_names():
            self._registry.set_permission(tool_name, default_perm)

        # Apply auto-approve list
        for tool_name in policy_config.get("auto", []):
            self._registry.set_permission(tool_name, ToolPermission.AUTO)

        # Apply ask list
        for tool_name in policy_config.get("ask", []):
            self._registry.set_permission(tool_name, ToolPermission.ASK)

    def _apply_custom_rules(self) -> None:
        """Apply custom permission rules"""
        if not self._registry:
            return

        for rule in self.config.custom_rules:
            # Handle wildcards
            if "*" in rule.tool_pattern:
                import fnmatch
                for tool_name in self._registry.list_names():
                    if fnmatch.fnmatch(tool_name, rule.tool_pattern):
                        self._registry.set_permission(tool_name, rule.permission)
            else:
                self._registry.set_permission(rule.tool_pattern, rule.permission)

        # Apply blocked tools
        for tool_name in self.config.blocked_tools:
            self._registry.set_permission(tool_name, ToolPermission.DENY)

    def set_policy(self, policy: PermissionPolicy) -> None:
        """Change the permission policy

        Args:
            policy: New policy to apply
        """
        self.config.policy = policy
        self._apply_policy()
        self._apply_custom_rules()

    def add_rule(self, rule: PermissionRule) -> None:
        """Add a custom permission rule

        Args:
            rule: Rule to add
        """
        self.config.custom_rules.append(rule)
        if self._registry:
            self._apply_custom_rules()

    def block_tool(self, tool_name: str) -> None:
        """Block a tool from being used

        Args:
            tool_name: Tool to block
        """
        self.config.blocked_tools.add(tool_name)
        if self._registry:
            self._registry.set_permission(tool_name, ToolPermission.DENY)

    def unblock_tool(self, tool_name: str) -> None:
        """Unblock a tool

        Args:
            tool_name: Tool to unblock
        """
        self.config.blocked_tools.discard(tool_name)
        if self._registry:
            self._apply_policy()
            self._apply_custom_rules()

    def approve_for_session(self, tool_name: str) -> None:
        """Approve a tool for the current session

        Args:
            tool_name: Tool to approve
        """
        self.config.session_approvals.add(tool_name)
        if self._registry:
            self._registry.approve_for_session(tool_name)

    def clear_session_approvals(self) -> None:
        """Clear all session approvals"""
        self.config.session_approvals.clear()
        if self._registry:
            self._registry.clear_session_approvals()

    def needs_approval(self, tool_name: str) -> bool:
        """Check if a tool needs approval

        Args:
            tool_name: Tool to check

        Returns:
            True if approval is needed
        """
        if not self._registry:
            return True

        if tool_name in self.config.blocked_tools:
            return True  # Will be denied

        if tool_name in self.config.session_approvals:
            return False

        return self._registry.needs_approval(tool_name)

    def get_permission(self, tool_name: str) -> ToolPermission:
        """Get the current permission for a tool

        Args:
            tool_name: Tool name

        Returns:
            Current permission level
        """
        if tool_name in self.config.blocked_tools:
            return ToolPermission.DENY

        if self._registry:
            return self._registry.get_permission(tool_name)

        return ToolPermission.ASK

    def get_status(self) -> Dict:
        """Get current permission status

        Returns:
            Dict with permission information
        """
        tools_by_permission = {
            "auto": [],
            "ask": [],
            "ask_once": [],
            "deny": [],
        }

        if self._registry:
            for tool_name in self._registry.list_names():
                perm = self.get_permission(tool_name)
                tools_by_permission[perm.value].append(tool_name)

        return {
            "policy": self.config.policy.value,
            "tools": tools_by_permission,
            "blocked": list(self.config.blocked_tools),
            "session_approved": list(self.config.session_approvals),
            "custom_rules": len(self.config.custom_rules),
        }

    def save_config(self, path: str) -> None:
        """Save permission configuration to file

        Args:
            path: Path to save config
        """
        config_data = {
            "policy": self.config.policy.value,
            "custom_rules": [
                {
                    "tool_pattern": r.tool_pattern,
                    "permission": r.permission.value,
                    "reason": r.reason,
                }
                for r in self.config.custom_rules
            ],
            "blocked_tools": list(self.config.blocked_tools),
        }

        with open(path, "w") as f:
            json.dump(config_data, f, indent=2)

    @classmethod
    def load_config(cls, path: str) -> "PermissionManager":
        """Load permission configuration from file

        Args:
            path: Path to config file

        Returns:
            PermissionManager with loaded config
        """
        with open(path, "r") as f:
            data = json.load(f)

        config = PermissionConfig(
            policy=PermissionPolicy(data.get("policy", "normal")),
            custom_rules=[
                PermissionRule(
                    tool_pattern=r["tool_pattern"],
                    permission=ToolPermission(r["permission"]),
                    reason=r.get("reason"),
                )
                for r in data.get("custom_rules", [])
            ],
            blocked_tools=set(data.get("blocked_tools", [])),
        )

        return cls(config)
