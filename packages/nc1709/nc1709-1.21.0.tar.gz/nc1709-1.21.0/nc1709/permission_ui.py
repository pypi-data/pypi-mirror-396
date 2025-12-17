"""
Interactive Permission UI for NC1709

A modern, Claude Code-style permission prompt with:
- Arrow key navigation
- Remember for session/directory
- Custom input option
- Syntax-highlighted command preview
"""

import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Callable

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text


class PermissionChoice(Enum):
    """Possible permission choices"""
    YES = "yes"
    YES_ALWAYS_SESSION = "yes_session"
    YES_ALWAYS_DIRECTORY = "yes_directory"
    NO = "no"
    CUSTOM = "custom"


@dataclass
class PermissionResult:
    """Result of a permission prompt"""
    choice: PermissionChoice
    custom_instruction: Optional[str] = None
    remember_pattern: Optional[str] = None


class InteractivePermissionUI:
    """
    Interactive permission prompt with arrow key navigation.

    Example:
        ┌─────────────────────────────────────────────────────────────────┐
        │  ps aux --sort=-%cpu | head -20                                 │
        │  List top processes by CPU                                      │
        └─────────────────────────────────────────────────────────────────┘

        Do you want to proceed?

        ❯ 1. Yes
          2. Yes, and don't ask again this session
          3. Yes, and don't ask again in /current/dir
          4. No
          5. Type custom instruction...

        [↑↓ to move, Enter to select, Esc to cancel]
    """

    def __init__(self):
        self.console = Console()
        self.selected_index = 0
        self.result: Optional[PermissionResult] = None
        self.cancelled = False

    def _create_options(self, command: str, cwd: str) -> List[tuple]:
        """Create the list of options"""
        dir_name = os.path.basename(cwd) or cwd
        return [
            ("yes", "Yes"),
            ("yes_session", "Yes, and don't ask again this session"),
            ("yes_directory", f"Yes, and don't ask again in {dir_name}"),
            ("no", "No"),
            ("custom", "Type custom instruction..."),
        ]

    def prompt(
        self,
        command: str,
        description: str = "",
        cwd: str = "",
        tool_name: str = "Bash",
        timeout: int = None
    ) -> PermissionResult:
        """
        Show interactive permission prompt.

        Args:
            command: The command to be executed
            description: Human-readable description of what it does
            cwd: Current working directory
            tool_name: Name of the tool requesting permission
            timeout: Optional timeout in seconds to display

        Returns:
            PermissionResult with user's choice
        """
        cwd = cwd or os.getcwd()
        options = self._create_options(command, cwd)
        self.selected_index = 0
        self.result = None
        self.cancelled = False

        # Print the command in Claude Code style: ⏺ Bash(command) timeout: 30s
        self.console.print()

        # Truncate long commands for display
        display_cmd = command[:80] + "..." if len(command) > 80 else command
        header = f"[cyan]⏺[/] [bold]{tool_name}[/]([dim]{display_cmd}[/])"
        if timeout:
            header += f" [dim]timeout: {timeout}s[/]"
        self.console.print(header)

        # Show full command with syntax highlighting in panel
        if tool_name == "Bash":
            syntax = Syntax(command, "bash", theme="monokai", line_numbers=False, word_wrap=True)
            panel = Panel(syntax, border_style="dim")
        else:
            panel = Panel(
                Text(command, style="white"),
                border_style="dim"
            )
        self.console.print(panel)

        # Show description if provided
        if description:
            self.console.print(f"  [dim]{description}[/]")
        self.console.print()
        self.console.print("[bold]Do you want to proceed?[/]")
        self.console.print()

        # Create key bindings
        kb = KeyBindings()

        @kb.add('up')
        @kb.add('k')
        def move_up(event):
            self.selected_index = max(0, self.selected_index - 1)

        @kb.add('down')
        @kb.add('j')
        def move_down(event):
            self.selected_index = min(len(options) - 1, self.selected_index + 1)

        @kb.add('enter')
        def select(event):
            choice_key = options[self.selected_index][0]
            if choice_key == "custom":
                event.app.exit(result="custom")
            else:
                self.result = PermissionResult(
                    choice=PermissionChoice(choice_key),
                    remember_pattern=command if choice_key in ("yes_session", "yes_directory") else None
                )
                event.app.exit(result="selected")

        @kb.add('escape')
        @kb.add('c-c')
        def cancel(event):
            self.cancelled = True
            event.app.exit(result="cancelled")

        @kb.add('1')
        def quick_yes(event):
            self.result = PermissionResult(choice=PermissionChoice.YES)
            event.app.exit(result="selected")

        @kb.add('2')
        def quick_session(event):
            self.result = PermissionResult(
                choice=PermissionChoice.YES_ALWAYS_SESSION,
                remember_pattern=command
            )
            event.app.exit(result="selected")

        @kb.add('3')
        def quick_directory(event):
            self.result = PermissionResult(
                choice=PermissionChoice.YES_ALWAYS_DIRECTORY,
                remember_pattern=command
            )
            event.app.exit(result="selected")

        @kb.add('4')
        @kb.add('n')
        def quick_no(event):
            self.result = PermissionResult(choice=PermissionChoice.NO)
            event.app.exit(result="selected")

        @kb.add('5')
        def quick_custom(event):
            event.app.exit(result="custom")

        def get_formatted_text():
            lines = []
            for i, (key, label) in enumerate(options):
                if i == self.selected_index:
                    lines.append(('class:selected', f' ❯ {i+1}. {label}\n'))
                else:
                    lines.append(('class:option', f'   {i+1}. {label}\n'))
            lines.append(('class:hint', '\n [↑↓ to move, Enter to select, Esc to cancel]'))
            return FormattedText(lines)

        # Create the application
        style = Style.from_dict({
            'selected': 'bold #00ff00',
            'option': '#888888',
            'hint': 'italic #666666',
        })

        layout = Layout(
            Window(
                FormattedTextControl(get_formatted_text),
                always_hide_cursor=True,
            )
        )

        app = Application(
            layout=layout,
            key_bindings=kb,
            style=style,
            full_screen=False,
            mouse_support=False,
        )

        result = app.run()

        # Clear the menu after selection
        # Move cursor up and clear the lines we printed
        num_lines = len(options) + 2  # options + hint line + blank
        sys.stdout.write(f'\033[{num_lines}A')  # Move up
        sys.stdout.write('\033[J')  # Clear from cursor to end
        sys.stdout.flush()

        if result == "custom":
            # Get custom instruction
            try:
                custom = input(" Custom instruction: ").strip()
                if custom:
                    self.result = PermissionResult(
                        choice=PermissionChoice.CUSTOM,
                        custom_instruction=custom
                    )
                else:
                    self.result = PermissionResult(choice=PermissionChoice.NO)
            except (KeyboardInterrupt, EOFError):
                self.result = PermissionResult(choice=PermissionChoice.NO)

        if self.cancelled or self.result is None:
            self.result = PermissionResult(choice=PermissionChoice.NO)

        # Print the choice made
        choice_text = {
            PermissionChoice.YES: "[green]✓ Approved[/]",
            PermissionChoice.YES_ALWAYS_SESSION: "[green]✓ Approved for session[/]",
            PermissionChoice.YES_ALWAYS_DIRECTORY: "[green]✓ Approved for directory[/]",
            PermissionChoice.NO: "[red]✗ Denied[/]",
            PermissionChoice.CUSTOM: f"[yellow]→ Custom: {self.result.custom_instruction}[/]",
        }
        self.console.print(choice_text.get(self.result.choice, ""))

        return self.result


def ask_permission(
    command: str,
    description: str = "",
    cwd: str = "",
    tool_name: str = "Bash",
    timeout: int = None,
    fallback_simple: bool = True
) -> PermissionResult:
    """
    Convenience function to ask for permission.

    Falls back to simple y/n if terminal doesn't support interactive mode.

    Args:
        command: Command to execute
        description: What it does
        cwd: Current working directory
        tool_name: Tool requesting permission
        timeout: Optional timeout in seconds to display
        fallback_simple: Use simple prompt if interactive fails

    Returns:
        PermissionResult
    """
    # Check if we're in an interactive terminal
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        if fallback_simple:
            return _simple_prompt(command, description, tool_name, timeout)
        return PermissionResult(choice=PermissionChoice.NO)

    try:
        ui = InteractivePermissionUI()
        return ui.prompt(command, description, cwd, tool_name, timeout)
    except Exception:
        # Fall back to simple prompt on any error
        if fallback_simple:
            return _simple_prompt(command, description, tool_name, timeout)
        return PermissionResult(choice=PermissionChoice.NO)


def _simple_prompt(command: str, description: str, tool_name: str, timeout: int = None) -> PermissionResult:
    """Simple y/n fallback prompt with Claude Code style header"""
    console = Console()

    # Claude Code style: ⏺ Bash(command) timeout: 30s
    display_cmd = command[:80] + "..." if len(command) > 80 else command
    header = f"\n[cyan]⏺[/] [bold]{tool_name}[/]([dim]{display_cmd}[/])"
    if timeout:
        header += f" [dim]timeout: {timeout}s[/]"
    console.print(header)

    if description:
        console.print(f"  [dim]⎿ {description}[/]")

    try:
        response = input("\nAllow? [y/N/always]: ").strip().lower()
        if response in ('y', 'yes'):
            return PermissionResult(choice=PermissionChoice.YES)
        elif response in ('a', 'always'):
            return PermissionResult(
                choice=PermissionChoice.YES_ALWAYS_SESSION,
                remember_pattern=command
            )
        else:
            return PermissionResult(choice=PermissionChoice.NO)
    except (KeyboardInterrupt, EOFError):
        return PermissionResult(choice=PermissionChoice.NO)


# Global permission memory
_session_approvals: set = set()
_directory_approvals: dict = {}  # {directory: set of patterns}


def check_remembered(command: str, cwd: str = "") -> Optional[bool]:
    """
    Check if a command was previously approved.

    Returns:
        True if approved, False if denied, None if not remembered
    """
    # Check session approvals
    if command in _session_approvals:
        return True

    # Check directory approvals
    cwd = cwd or os.getcwd()
    if cwd in _directory_approvals:
        if command in _directory_approvals[cwd]:
            return True

    return None


def remember_approval(result: PermissionResult, command: str, cwd: str = ""):
    """Remember an approval for future prompts"""
    if result.choice == PermissionChoice.YES_ALWAYS_SESSION:
        _session_approvals.add(command)
    elif result.choice == PermissionChoice.YES_ALWAYS_DIRECTORY:
        cwd = cwd or os.getcwd()
        if cwd not in _directory_approvals:
            _directory_approvals[cwd] = set()
        _directory_approvals[cwd].add(command)


def clear_session_approvals():
    """Clear all session approvals"""
    _session_approvals.clear()


def clear_directory_approvals(directory: str = ""):
    """Clear approvals for a directory"""
    if directory:
        _directory_approvals.pop(directory, None)
    else:
        _directory_approvals.clear()
