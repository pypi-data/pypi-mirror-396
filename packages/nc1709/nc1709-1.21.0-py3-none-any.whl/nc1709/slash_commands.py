"""
Slash Commands System for NC1709
Provides "/" command autocomplete with descriptions
"""

from dataclasses import dataclass
from typing import List, Optional, Callable, Dict, Any
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


@dataclass
class SlashCommand:
    """Definition of a slash command"""
    name: str  # Command name without "/"
    description: str  # Short description shown in popup
    handler: Optional[Callable] = None  # Function to execute
    category: str = "general"  # Category for grouping
    aliases: Optional[List[str]] = None  # Alternative names


# All available slash commands
SLASH_COMMANDS: List[SlashCommand] = [
    # General Commands
    SlashCommand(
        name="help",
        description="Show all available commands and shortcuts",
        category="general"
    ),
    SlashCommand(
        name="clear",
        description="Clear conversation history and start fresh",
        category="general"
    ),
    SlashCommand(
        name="exit",
        description="Exit NC1709 and save session",
        category="general",
        aliases=["quit", "q"]
    ),
    SlashCommand(
        name="history",
        description="Show recent command execution history",
        category="general"
    ),
    SlashCommand(
        name="config",
        description="View current configuration summary",
        category="general"
    ),
    SlashCommand(
        name="config raw",
        description="Show full configuration as JSON",
        category="general"
    ),
    SlashCommand(
        name="version",
        description="Show NC1709 version information",
        category="general"
    ),

    # Agent Commands
    SlashCommand(
        name="agent",
        description="Toggle agent mode for autonomous tool execution",
        category="agent"
    ),
    SlashCommand(
        name="agent on",
        description="Enable agent mode with tool execution",
        category="agent"
    ),
    SlashCommand(
        name="agent off",
        description="Disable agent mode",
        category="agent"
    ),
    SlashCommand(
        name="agent tools",
        description="List all available agent tools",
        category="agent"
    ),
    SlashCommand(
        name="agent status",
        description="Show agent status and recent tool history",
        category="agent"
    ),

    # File Operations
    SlashCommand(
        name="read",
        description="Read and display a file's contents",
        category="files"
    ),
    SlashCommand(
        name="edit",
        description="Edit a file with AI assistance",
        category="files"
    ),
    SlashCommand(
        name="create",
        description="Create a new file",
        category="files"
    ),
    SlashCommand(
        name="diff",
        description="Show changes in a file or directory",
        category="files"
    ),

    # Search & Navigation
    SlashCommand(
        name="search",
        description="Search code semantically in indexed project",
        category="search"
    ),
    SlashCommand(
        name="find",
        description="Find files by name pattern",
        category="search"
    ),
    SlashCommand(
        name="grep",
        description="Search for text in files",
        category="search"
    ),
    SlashCommand(
        name="index",
        description="Index current project for semantic search",
        category="search"
    ),

    # Session Management
    SlashCommand(
        name="sessions",
        description="List all saved conversation sessions",
        category="session"
    ),
    SlashCommand(
        name="save",
        description="Save current session",
        category="session"
    ),
    SlashCommand(
        name="resume",
        description="Resume a previous session by ID",
        category="session"
    ),

    # Git Commands
    SlashCommand(
        name="git status",
        description="Show git working tree status",
        category="git"
    ),
    SlashCommand(
        name="git diff",
        description="Show git diff of changes",
        category="git"
    ),
    SlashCommand(
        name="git log",
        description="Show recent git commit history",
        category="git"
    ),
    SlashCommand(
        name="git commit",
        description="Commit staged changes with AI-generated message",
        category="git"
    ),
    SlashCommand(
        name="git branch",
        description="List or create git branches",
        category="git"
    ),
    SlashCommand(
        name="git push",
        description="Push commits to remote",
        category="git"
    ),
    SlashCommand(
        name="git pull",
        description="Pull latest changes from remote",
        category="git"
    ),

    # Docker Commands
    SlashCommand(
        name="docker ps",
        description="List running Docker containers",
        category="docker"
    ),
    SlashCommand(
        name="docker images",
        description="List Docker images",
        category="docker"
    ),
    SlashCommand(
        name="docker logs",
        description="View Docker container logs",
        category="docker"
    ),
    SlashCommand(
        name="docker compose up",
        description="Start Docker Compose services",
        category="docker"
    ),
    SlashCommand(
        name="docker compose down",
        description="Stop Docker Compose services",
        category="docker"
    ),

    # Code Actions
    SlashCommand(
        name="fix",
        description="Auto-detect and fix errors in code",
        category="code"
    ),
    SlashCommand(
        name="test",
        description="Generate unit tests for a file",
        category="code"
    ),
    SlashCommand(
        name="explain",
        description="Explain what a piece of code does",
        category="code"
    ),
    SlashCommand(
        name="refactor",
        description="Suggest refactoring improvements",
        category="code"
    ),
    SlashCommand(
        name="review",
        description="Review code for issues and improvements",
        category="code"
    ),
    SlashCommand(
        name="optimize",
        description="Suggest performance optimizations",
        category="code"
    ),
    SlashCommand(
        name="document",
        description="Generate documentation for code",
        category="code"
    ),

    # MCP Commands
    SlashCommand(
        name="mcp",
        description="Show MCP server status",
        category="mcp"
    ),
    SlashCommand(
        name="mcp tools",
        description="List available MCP tools",
        category="mcp"
    ),

    # Plugins
    SlashCommand(
        name="plugins",
        description="List available plugins",
        category="plugins"
    ),

    # Custom Commands
    SlashCommand(
        name="commands",
        description="List available custom slash commands",
        category="custom"
    ),

    # GitHub/PR Commands
    SlashCommand(
        name="pr",
        description="Create a new Pull Request from current branch",
        category="github"
    ),
    SlashCommand(
        name="pr list",
        description="List open Pull Requests",
        category="github"
    ),
    SlashCommand(
        name="pr view",
        description="View a specific Pull Request",
        category="github"
    ),
    SlashCommand(
        name="issues",
        description="List open issues",
        category="github"
    ),
    SlashCommand(
        name="gh",
        description="Run a gh CLI command",
        category="github"
    ),

    # Linting Commands
    SlashCommand(
        name="lint",
        description="Run linter on project or file",
        category="lint"
    ),
    SlashCommand(
        name="lint file",
        description="Lint a specific file",
        category="lint"
    ),
    SlashCommand(
        name="lint fix",
        description="Run linter with auto-fix enabled",
        category="lint"
    ),
    SlashCommand(
        name="lint linters",
        description="List available linters",
        category="lint"
    ),

    # Plan Mode
    SlashCommand(
        name="plan",
        description="Enter plan mode (think before acting)",
        category="plan"
    ),
    SlashCommand(
        name="plan approve",
        description="Approve the current plan and execute it",
        category="plan"
    ),
    SlashCommand(
        name="plan reject",
        description="Reject the current plan",
        category="plan"
    ),
    SlashCommand(
        name="plan show",
        description="Show the current plan",
        category="plan"
    ),
    SlashCommand(
        name="plan exit",
        description="Exit plan mode without executing",
        category="plan"
    ),

    # Image/Screenshot Input
    SlashCommand(
        name="image",
        description="Add an image file to your next prompt",
        category="image"
    ),
    SlashCommand(
        name="screenshot",
        description="Capture a screenshot to include in your next prompt",
        category="image"
    ),
    SlashCommand(
        name="paste",
        description="Paste image from clipboard for your next prompt",
        category="image"
    ),
    SlashCommand(
        name="images",
        description="List pending images for next prompt",
        category="image"
    ),
    SlashCommand(
        name="clear-images",
        description="Clear pending images",
        category="image"
    ),

    # Quick Actions
    SlashCommand(
        name="run",
        description="Run a shell command",
        category="quick"
    ),
    SlashCommand(
        name="web",
        description="Start the web dashboard",
        category="quick"
    ),
    SlashCommand(
        name="compact",
        description="Summarize conversation to reduce context",
        category="quick"
    ),

    # Checkpoint Commands
    SlashCommand(
        name="rewind",
        description="Undo last file change (rewind to previous checkpoint)",
        category="checkpoint",
        aliases=["undo"]
    ),
    SlashCommand(
        name="checkpoints",
        description="List recent file checkpoints",
        category="checkpoint"
    ),
    SlashCommand(
        name="forward",
        description="Redo after rewind (go forward in checkpoint history)",
        category="checkpoint",
        aliases=["redo"]
    ),

    # Git Auto-commit Commands
    SlashCommand(
        name="autocommit",
        description="Toggle automatic git commits after file changes",
        category="git"
    ),
    SlashCommand(
        name="autocommit on",
        description="Enable automatic git commits",
        category="git"
    ),
    SlashCommand(
        name="autocommit off",
        description="Disable automatic git commits",
        category="git"
    ),

    # Model Registry Commands
    SlashCommand(
        name="models",
        description="Show Model Registry status and available models",
        category="models"
    ),
    SlashCommand(
        name="models list",
        description="List all known models with capabilities",
        category="models"
    ),
    SlashCommand(
        name="models detect",
        description="Auto-detect models from Ollama",
        category="models"
    ),
    SlashCommand(
        name="models recommend",
        description="Get model recommendations for tasks",
        category="models"
    ),

    # Brain/Cognitive System Commands
    SlashCommand(
        name="brain",
        description="Show cognitive system status",
        category="brain"
    ),
    SlashCommand(
        name="brain status",
        description="Show cognitive system status",
        category="brain"
    ),
    SlashCommand(
        name="brain suggest",
        description="Get AI suggestions for current context",
        category="brain"
    ),
    SlashCommand(
        name="brain index",
        description="Index project for cognitive understanding",
        category="brain"
    ),
    SlashCommand(
        name="brain insights",
        description="Show AI insights about your codebase",
        category="brain"
    ),
]


class SlashCommandCompleter(Completer):
    """Autocomplete for slash commands including custom commands"""

    def __init__(self, commands: Optional[List[SlashCommand]] = None):
        self.commands = commands or SLASH_COMMANDS
        self._custom_manager = None

    def _get_custom_manager(self):
        """Lazy load custom command manager"""
        if self._custom_manager is None:
            try:
                from .custom_commands import get_custom_command_manager
                self._custom_manager = get_custom_command_manager()
            except ImportError:
                pass
        return self._custom_manager

    def get_completions(self, document: Document, complete_event) -> List[Completion]:
        """Get completions for current input"""
        text = document.text_before_cursor

        # Only complete if starting with /
        if not text.startswith('/'):
            return

        # Get the partial command (without the /)
        partial = text[1:].lower()

        # Find matching built-in commands
        for cmd in self.commands:
            cmd_name = cmd.name.lower()

            # Match if partial is empty (show all) or partial is prefix of command name
            if partial == "" or cmd_name.startswith(partial):
                # Calculate how much to complete
                completion_text = cmd.name[len(partial):]

                yield Completion(
                    completion_text,
                    start_position=0,
                    display=f"/{cmd.name}",
                    display_meta=cmd.description,
                    style='class:completion',
                    selected_style='class:completion.selected'
                )

            # Also check aliases (but not when showing all)
            elif cmd.aliases:
                for alias in cmd.aliases:
                    if alias.lower().startswith(partial):
                        completion_text = alias[len(partial):]
                        yield Completion(
                            completion_text,
                            start_position=0,
                            display=f"/{alias}",
                            display_meta=f"{cmd.description} (alias for /{cmd.name})",
                            style='class:completion',
                            selected_style='class:completion.selected'
                        )

        # Add custom commands
        manager = self._get_custom_manager()
        if manager:
            for custom_cmd in manager.list_commands():
                cmd_name = custom_cmd.name.lower()
                if partial == "" or cmd_name.startswith(partial):
                    completion_text = custom_cmd.name[len(partial):]
                    scope_tag = "[project]" if custom_cmd.scope == "project" else "[personal]"

                    yield Completion(
                        completion_text,
                        start_position=0,
                        display=f"/{custom_cmd.name}",
                        display_meta=f"{custom_cmd.description} {scope_tag}",
                        style='class:completion.custom',
                        selected_style='class:completion.selected'
                    )


def get_command_by_name(name: str) -> Optional[SlashCommand]:
    """Get a slash command by name or alias

    Args:
        name: Command name (with or without leading /)

    Returns:
        SlashCommand if found, None otherwise
    """
    # Remove leading / if present
    if name.startswith('/'):
        name = name[1:]

    name = name.lower()

    for cmd in SLASH_COMMANDS:
        if cmd.name.lower() == name:
            return cmd
        if cmd.aliases and name in [a.lower() for a in cmd.aliases]:
            return cmd

    return None


def list_commands_by_category() -> Dict[str, List[SlashCommand]]:
    """Get all commands grouped by category

    Returns:
        Dict mapping category names to lists of commands
    """
    by_category: Dict[str, List[SlashCommand]] = {}

    for cmd in SLASH_COMMANDS:
        if cmd.category not in by_category:
            by_category[cmd.category] = []
        by_category[cmd.category].append(cmd)

    return by_category


def format_help_text() -> str:
    """Format all commands as help text

    Returns:
        Formatted help string
    """
    lines = []
    lines.append("\n\033[1mSlash Commands\033[0m")
    lines.append("Type / to see available commands with autocomplete.\n")

    category_titles = {
        "general": "General",
        "agent": "Agent Mode",
        "files": "File Operations",
        "search": "Search & Navigation",
        "session": "Session Management",
        "git": "Git",
        "docker": "Docker",
        "code": "Code Actions",
        "mcp": "MCP",
        "plugins": "Plugins",
        "custom": "Custom Commands",
        "github": "GitHub/PR",
        "lint": "Linting",
        "plan": "Plan Mode",
        "image": "Image/Screenshot Input",
        "quick": "Quick Actions",
        "checkpoint": "Checkpoints (Undo/Redo)",
        "models": "Model Registry",
        "brain": "Brain (Cognitive System)",
    }

    by_category = list_commands_by_category()

    for category, title in category_titles.items():
        if category not in by_category:
            continue

        commands = by_category[category]
        lines.append(f"\033[36m{title}:\033[0m")

        for cmd in commands:
            lines.append(f"  \033[1m/{cmd.name:<16}\033[0m {cmd.description}")

        lines.append("")

    return "\n".join(lines)
