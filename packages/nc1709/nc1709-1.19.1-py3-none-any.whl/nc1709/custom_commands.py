"""
Custom Slash Commands for NC1709

Allows users to define their own slash commands in:
- ~/.nc1709/commands/ (personal commands)
- .nc1709/commands/ (project commands)

Similar to Claude Code's custom command system.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class CustomCommand:
    """A user-defined custom command"""
    name: str           # Command name (without /)
    content: str        # Command content/prompt
    description: str    # Optional description (first line of file)
    file_path: Path     # Path to the command file
    scope: str          # "personal" or "project"


class CustomCommandManager:
    """
    Manages custom slash commands defined in markdown files.

    Commands are loaded from:
    - ~/.nc1709/commands/*.md (personal commands, available everywhere)
    - .nc1709/commands/*.md (project commands, available in current project)

    The filename becomes the command name (e.g., fix-bug.md -> /project:fix-bug)
    The first line starting with # is used as the description.
    The rest is the command content/prompt.
    """

    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize the custom command manager.

        Args:
            project_path: Path to current project (defaults to cwd)
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.personal_dir = Path.home() / ".nc1709" / "commands"
        self.project_dir = self.project_path / ".nc1709" / "commands"

        # Ensure personal commands directory exists
        self.personal_dir.mkdir(parents=True, exist_ok=True)

        # Cache loaded commands
        self._commands: Dict[str, CustomCommand] = {}
        self._loaded = False

    def _load_commands(self) -> None:
        """Load all custom commands from disk"""
        self._commands = {}

        # Load personal commands
        if self.personal_dir.exists():
            for file_path in self.personal_dir.glob("*.md"):
                cmd = self._load_command_file(file_path, scope="personal")
                if cmd:
                    self._commands[cmd.name] = cmd

        # Load project commands (override personal if same name)
        if self.project_dir.exists():
            for file_path in self.project_dir.glob("*.md"):
                cmd = self._load_command_file(file_path, scope="project")
                if cmd:
                    # Use project: prefix to avoid collisions
                    self._commands[f"project:{cmd.name}"] = cmd

        self._loaded = True

    def _load_command_file(self, file_path: Path, scope: str) -> Optional[CustomCommand]:
        """Load a single command file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.strip().split('\n')

            # Extract description from first heading line
            description = ""
            content_start = 0

            for i, line in enumerate(lines):
                if line.startswith('#'):
                    # Extract text after # (the description)
                    description = line.lstrip('#').strip()
                    content_start = i + 1
                    break
                elif line.strip():
                    # First non-empty, non-heading line - no description
                    break

            # Command name is filename without extension
            name = file_path.stem

            # Content is everything after the description
            command_content = '\n'.join(lines[content_start:]).strip()

            return CustomCommand(
                name=name,
                content=command_content,
                description=description or f"Custom command: {name}",
                file_path=file_path,
                scope=scope
            )

        except Exception:
            return None

    def reload(self) -> None:
        """Force reload all commands"""
        self._loaded = False
        self._load_commands()

    def get_command(self, name: str) -> Optional[CustomCommand]:
        """
        Get a custom command by name.

        Args:
            name: Command name (with or without /)

        Returns:
            CustomCommand if found, None otherwise
        """
        if not self._loaded:
            self._load_commands()

        # Remove leading / if present
        if name.startswith('/'):
            name = name[1:]

        return self._commands.get(name)

    def list_commands(self) -> List[CustomCommand]:
        """Get all available custom commands"""
        if not self._loaded:
            self._load_commands()

        return list(self._commands.values())

    def get_commands_for_autocomplete(self) -> List[Dict[str, str]]:
        """Get commands formatted for autocomplete"""
        if not self._loaded:
            self._load_commands()

        return [
            {
                "name": cmd.name,
                "description": cmd.description,
                "scope": cmd.scope
            }
            for cmd in self._commands.values()
        ]

    def create_command(
        self,
        name: str,
        content: str,
        description: str = "",
        scope: str = "personal"
    ) -> CustomCommand:
        """
        Create a new custom command.

        Args:
            name: Command name (without /)
            content: Command content/prompt
            description: Optional description
            scope: "personal" or "project"

        Returns:
            The created CustomCommand
        """
        # Determine target directory
        if scope == "project":
            target_dir = self.project_dir
        else:
            target_dir = self.personal_dir

        target_dir.mkdir(parents=True, exist_ok=True)

        # Create the file content
        file_content = ""
        if description:
            file_content = f"# {description}\n\n"
        file_content += content

        # Write the file
        file_path = target_dir / f"{name}.md"
        file_path.write_text(file_content, encoding='utf-8')

        # Create and cache the command
        cmd = CustomCommand(
            name=name if scope == "personal" else f"project:{name}",
            content=content,
            description=description or f"Custom command: {name}",
            file_path=file_path,
            scope=scope
        )

        self._commands[cmd.name] = cmd
        return cmd

    def delete_command(self, name: str) -> bool:
        """
        Delete a custom command.

        Args:
            name: Command name

        Returns:
            True if deleted, False if not found
        """
        cmd = self.get_command(name)
        if cmd and cmd.file_path.exists():
            cmd.file_path.unlink()
            del self._commands[cmd.name]
            return True
        return False

    def get_example_commands(self) -> str:
        """Get example custom commands for users"""
        return """# Example Custom Commands

Create markdown files in ~/.nc1709/commands/ or .nc1709/commands/

## Example: fix-bug.md

```markdown
# Fix a bug in the codebase

Look at the error message or description provided.
Find the relevant code files.
Analyze the root cause.
Propose and implement a fix.
Test that the fix works.
```

## Example: add-tests.md

```markdown
# Add unit tests for a file

Read the specified file.
Identify all public functions and classes.
Generate comprehensive unit tests.
Include edge cases and error handling tests.
Write tests to a corresponding test file.
```

## Example: review-pr.md

```markdown
# Review a pull request

Check the diff for:
- Code style and best practices
- Potential bugs or edge cases
- Security vulnerabilities
- Performance issues
- Missing tests

Provide actionable feedback.
```
"""


# Global custom command manager
_custom_command_manager: Optional[CustomCommandManager] = None


def get_custom_command_manager() -> CustomCommandManager:
    """Get or create the global custom command manager"""
    global _custom_command_manager
    if _custom_command_manager is None:
        _custom_command_manager = CustomCommandManager()
    return _custom_command_manager


def execute_custom_command(name: str) -> Optional[str]:
    """
    Get the prompt content for a custom command.

    Args:
        name: Command name

    Returns:
        Command prompt content if found, None otherwise
    """
    manager = get_custom_command_manager()
    cmd = manager.get_command(name)
    if cmd:
        return cmd.content
    return None
