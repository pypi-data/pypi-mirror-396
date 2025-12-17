"""
Claude Code-style Tool UI for NC1709

Provides:
- Beautiful tool execution display with ⏺ prefix
- Collapsible output with ⎿ tree-style indentation
- Timeout display
- Auto-approve for safe commands
- Expandable long outputs (ctrl+r to expand)
"""

import os
import sys
import shutil
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any, Set

from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
from rich.style import Style


# ANSI color codes for direct terminal output
class C:
    """Terminal colors"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"

    # Colors
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"


# Unicode symbols
class S:
    """Symbols for tool display"""
    BULLET = "⏺"      # Tool execution marker
    CORNER = "⎿"      # Output tree connector
    CHECK = "✓"       # Success
    CROSS = "✗"       # Failure
    ARROW = "→"       # Action indicator
    THINKING = "✻"    # Thinking indicator


# Safe commands that auto-approve (read-only operations)
SAFE_COMMANDS = {
    # File reading
    "cat", "head", "tail", "less", "more", "file", "wc",
    # Directory listing
    "ls", "dir", "tree", "find", "locate",
    # System info
    "ps", "top", "htop", "df", "du", "free", "uptime", "whoami", "id",
    "uname", "hostname", "date", "cal", "env", "printenv",
    # Network info (read-only)
    "netstat", "ss", "lsof", "ifconfig", "ip", "ping", "host", "nslookup", "dig",
    # Git info (read-only)
    "git status", "git log", "git diff", "git branch", "git remote",
    # Package info
    "pip list", "pip show", "npm list", "brew list",
    # Text processing (read-only)
    "grep", "awk", "sed", "sort", "uniq", "cut", "tr",
    # Echo and printing
    "echo", "printf",
}

# Commands that need approval
DANGEROUS_PATTERNS = [
    "rm ", "rm -", "rmdir", "mv ", "cp ",  # File operations
    "chmod", "chown", "chgrp",              # Permission changes
    "kill", "pkill", "killall",             # Process control
    "sudo", "su ",                          # Privilege escalation
    "> ", ">> ", "tee ",                    # File writing
    "curl", "wget",                         # Network downloads
    "pip install", "npm install",           # Package installation
    "git push", "git commit", "git reset",  # Git modifications
    "docker", "kubectl",                    # Container operations
]


@dataclass
class ToolExecution:
    """Represents a tool execution with its output"""
    tool_name: str
    command: str
    timeout: int
    output: str = ""
    error: str = ""
    success: bool = True
    duration_ms: int = 0
    expanded: bool = False


class ToolUI:
    """
    Claude Code-style tool execution UI.

    Usage:
        ui = ToolUI()

        # Show tool being called
        ui.show_tool_call("Bash", "ps aux | head -20", timeout=30)

        # Execute and show output
        output = execute_command(...)
        ui.show_tool_output(output, collapsible=True)
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.terminal_width = shutil.get_terminal_size().columns
        self._session_approved: Set[str] = set()
        self._auto_approve_patterns: Set[str] = set()

    def is_safe_command(self, command: str) -> bool:
        """Check if a command is safe (read-only) and can auto-approve"""
        cmd_lower = command.lower().strip()

        # Check for dangerous patterns first
        for pattern in DANGEROUS_PATTERNS:
            if pattern in cmd_lower:
                return False

        # Check if starts with a safe command
        first_word = cmd_lower.split()[0] if cmd_lower.split() else ""
        first_two = " ".join(cmd_lower.split()[:2]) if len(cmd_lower.split()) >= 2 else ""

        return first_word in SAFE_COMMANDS or first_two in SAFE_COMMANDS

    def truncate_command(self, command: str, max_len: int = 80) -> str:
        """Truncate long commands for display"""
        if len(command) <= max_len:
            return command
        return command[:max_len-3] + "..."

    def show_tool_call(
        self,
        tool_name: str,
        command: str,
        timeout: int = 30,
        auto_approved: bool = False
    ) -> None:
        """
        Display a tool call in Claude Code style.

        Example output:
        ⏺ Bash(ps aux | head -20) timeout: 30s
        """
        truncated = self.truncate_command(command)
        timeout_str = f"timeout: {timeout}s" if timeout else ""

        # Build the display line
        line = f"{C.CYAN}{S.BULLET}{C.RESET} {C.BOLD}{tool_name}{C.RESET}"
        line += f"({C.DIM}{truncated}{C.RESET})"
        if timeout_str:
            line += f" {C.GRAY}{timeout_str}{C.RESET}"

        print(line)

    def show_tool_output(
        self,
        output: str,
        max_lines: int = 3,
        collapsible: bool = True,
        error: bool = False
    ) -> None:
        """
        Display tool output with collapsible long content.

        Example:
          ⎿  USER   PID  %CPU
             root   1    0.0
             ... +148 more lines (ctrl+r to expand)
        """
        if not output:
            return

        lines = output.split('\n')
        total_lines = len(lines)

        # Color for output
        color = C.RED if error else C.RESET

        # Show first few lines with tree connector
        for i, line in enumerate(lines[:max_lines]):
            if i == 0:
                # First line with corner connector
                print(f"  {C.DIM}{S.CORNER}{C.RESET}  {color}{line}{C.RESET}")
            else:
                # Subsequent lines indented
                print(f"     {color}{line}{C.RESET}")

        # Show collapse indicator if there's more
        if collapsible and total_lines > max_lines:
            remaining = total_lines - max_lines
            print(f"     {C.DIM}... +{remaining} more lines (ctrl+r to expand){C.RESET}")

    def show_tool_success(self, tool_name: str, target: str = "") -> None:
        """Show successful tool completion"""
        if target:
            print(f"  {C.GREEN}{S.CHECK}{C.RESET} {tool_name}({C.CYAN}{target}{C.RESET})")
        else:
            print(f"  {C.GREEN}{S.CHECK}{C.RESET} {tool_name}")

    def show_tool_error(self, tool_name: str, error: str, target: str = "") -> None:
        """Show tool failure"""
        if target:
            print(f"  {C.RED}{S.CROSS}{C.RESET} {tool_name}({C.CYAN}{target}{C.RESET})")
        else:
            print(f"  {C.RED}{S.CROSS}{C.RESET} {tool_name}")
        if error:
            print(f"     {C.RED}{error}{C.RESET}")

    def show_thinking(self, iteration: int = 1) -> None:
        """Show thinking indicator"""
        print(f"{C.YELLOW}{S.THINKING}{C.RESET} {C.DIM}Thinking...{C.RESET} (iteration {iteration})")

    def prompt_approval(
        self,
        tool_name: str,
        command: str,
        timeout: int = 30,
        cwd: str = ""
    ) -> bool:
        """
        Prompt for tool approval with auto-approve for safe commands.

        Returns True if approved, False if denied.
        """
        # Check if already approved for session
        if command in self._session_approved:
            self.show_tool_call(tool_name, command, timeout, auto_approved=True)
            return True

        # Check if safe command - auto approve
        if self.is_safe_command(command):
            self.show_tool_call(tool_name, command, timeout, auto_approved=True)
            return True

        # Need manual approval
        self.show_tool_call(tool_name, command, timeout)
        print()

        try:
            response = input(f"  {C.BOLD}Allow?{C.RESET} [y/N/always]: ").strip().lower()

            if response == "always":
                self._session_approved.add(command)
                print(f"  {C.GREEN}{S.CHECK} Approved for session{C.RESET}")
                return True
            elif response in ("y", "yes"):
                print(f"  {C.GREEN}{S.CHECK} Approved{C.RESET}")
                return True
            else:
                print(f"  {C.RED}{S.CROSS} Denied{C.RESET}")
                return False
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {C.RED}{S.CROSS} Cancelled{C.RESET}")
            return False

    def format_file_output(
        self,
        file_path: str,
        content: str,
        max_lines: int = 5
    ) -> None:
        """Format file read output"""
        lines = content.split('\n')
        total = len(lines)

        print(f"  {C.DIM}{S.CORNER}{C.RESET}  {C.CYAN}{file_path}{C.RESET}")

        for i, line in enumerate(lines[:max_lines]):
            print(f"     {C.DIM}{line}{C.RESET}")

        if total > max_lines:
            print(f"     {C.DIM}... +{total - max_lines} more lines{C.RESET}")


class CollapsibleOutput:
    """
    Manages collapsible output that can be expanded.

    Stores full output and displays collapsed version,
    allowing expansion on demand.
    """

    def __init__(self):
        self._outputs: List[Dict[str, Any]] = []
        self._expanded: Set[int] = set()

    def add(self, tool_name: str, output: str, error: bool = False) -> int:
        """Add output and return its index"""
        idx = len(self._outputs)
        self._outputs.append({
            "tool": tool_name,
            "output": output,
            "error": error,
            "lines": output.split('\n') if output else []
        })
        return idx

    def display(self, idx: int, max_lines: int = 3) -> None:
        """Display output, collapsed or expanded"""
        if idx >= len(self._outputs):
            return

        data = self._outputs[idx]
        lines = data["lines"]
        expanded = idx in self._expanded
        color = C.RED if data["error"] else C.RESET

        if expanded or len(lines) <= max_lines:
            # Show all lines
            for i, line in enumerate(lines):
                prefix = f"  {C.DIM}{S.CORNER}{C.RESET}  " if i == 0 else "     "
                print(f"{prefix}{color}{line}{C.RESET}")
        else:
            # Show collapsed
            for i, line in enumerate(lines[:max_lines]):
                prefix = f"  {C.DIM}{S.CORNER}{C.RESET}  " if i == 0 else "     "
                print(f"{prefix}{color}{line}{C.RESET}")
            remaining = len(lines) - max_lines
            print(f"     {C.DIM}... +{remaining} more lines (ctrl+r to expand){C.RESET}")

    def expand(self, idx: int) -> None:
        """Mark output as expanded"""
        self._expanded.add(idx)

    def collapse(self, idx: int) -> None:
        """Mark output as collapsed"""
        self._expanded.discard(idx)

    def toggle(self, idx: int) -> None:
        """Toggle expansion state"""
        if idx in self._expanded:
            self._expanded.discard(idx)
        else:
            self._expanded.add(idx)


# Global instance for easy access
_tool_ui: Optional[ToolUI] = None


def get_tool_ui() -> ToolUI:
    """Get or create the global ToolUI instance"""
    global _tool_ui
    if _tool_ui is None:
        _tool_ui = ToolUI()
    return _tool_ui


def show_tool_call(tool_name: str, command: str, timeout: int = 30) -> None:
    """Convenience function to show a tool call"""
    get_tool_ui().show_tool_call(tool_name, command, timeout)


def show_tool_output(output: str, max_lines: int = 3, error: bool = False) -> None:
    """Convenience function to show tool output"""
    get_tool_ui().show_tool_output(output, max_lines, error=error)


def prompt_tool_approval(tool_name: str, command: str, timeout: int = 30) -> bool:
    """Convenience function to prompt for approval"""
    return get_tool_ui().prompt_approval(tool_name, command, timeout)
