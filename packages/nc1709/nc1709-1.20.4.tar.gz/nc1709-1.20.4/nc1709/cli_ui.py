"""
CLI UI - Claude Code-style Interactive Visual Feedback System

Provides rich, real-time visual feedback for CLI operations with:
- Animated spinners with status messages
- Tool/Action indicators with nested output
- State transitions (in-progress -> complete/failed)
- Color coding (blue=active, green=success, red=error, yellow=info)
- Non-blocking output with line replacement
- Streaming text support
- Text wrapping for clean output
- Dynamic thinking messages for user engagement
"""
import os
import re
import shutil
import sys
import textwrap
import time
import threading
from typing import Optional, List, Callable, Any, Dict
from enum import Enum
from dataclasses import dataclass, field
from contextlib import contextmanager

# Import dynamic thinking messages
try:
    from .thinking_messages import (
        ThinkingPhase, get_thinking_message, get_tool_message,
        get_progress_message, start_thinking, set_phase, should_update_message
    )
    HAS_THINKING_MESSAGES = True
except ImportError:
    HAS_THINKING_MESSAGES = False


# =============================================================================
# ANSI Color Codes
# =============================================================================

class Color:
    """ANSI color codes for terminal output"""
    # Reset
    RESET = "\033[0m"

    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Cursor control
    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"
    CLEAR_LINE = "\033[2K"
    MOVE_UP = "\033[1A"

    @classmethod
    def disable(cls):
        """Disable colors (for non-TTY output)"""
        for attr in dir(cls):
            if not attr.startswith('_') and attr.isupper():
                setattr(cls, attr, '')


# Check if output is a TTY
if not sys.stdout.isatty():
    Color.disable()


# =============================================================================
# Status Icons and Symbols
# =============================================================================

class Icons:
    """Unicode icons for status display - Claude Code style"""
    # Status indicators
    THINKING = "✻"
    SUCCESS = "✓"
    FAILURE = "✗"
    WARNING = "⚠"
    INFO = "ℹ"

    # Claude Code style
    BULLET = "●"           # Yellow bullet for tool calls
    CORNER = "⎿"           # Corner for output indentation
    HOLLOW = "○"           # Hollow circle for pending

    # Spinners
    DOTS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    BRAILLE = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]

    # Tree (kept for backward compat)
    TREE_BRANCH = "└─"
    TREE_VERTICAL = "│"
    TREE_TEE = "├─"

    # Actions
    READ = "📄"
    WRITE = "✏️"
    EXECUTE = "⚡"
    SEARCH = "🔍"
    ANALYZE = "🧠"


# =============================================================================
# State Management
# =============================================================================

class ActionState(Enum):
    """States for action indicators"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ActionItem:
    """Represents a single action or tool call"""
    name: str
    target: Optional[str] = None
    state: ActionState = ActionState.PENDING
    message: Optional[str] = None
    children: List["ActionItem"] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    @property
    def duration(self) -> Optional[float]:
        """Get action duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return None

    def format_duration(self) -> str:
        """Format duration as human-readable string"""
        d = self.duration
        if d is None:
            return ""
        if d < 1:
            return f"{d*1000:.0f}ms"
        elif d < 60:
            return f"{d:.1f}s"
        else:
            return f"{d/60:.1f}m"


# =============================================================================
# Action Spinner - Main Visual Component
# =============================================================================

class ActionSpinner:
    """
    Claude Code-style animated spinner with status messages.

    Usage:
        spinner = ActionSpinner("Analyzing your request")
        spinner.start()
        spinner.update("Processing code...")
        spinner.add_action("Read", "main.py")
        spinner.complete_action(0)
        spinner.success("Analysis complete")
    """

    def __init__(
        self,
        message: str = "Processing",
        spinner_chars: List[str] = None,
        interval: float = 0.08,
        dynamic_messages: bool = True
    ):
        """Initialize the action spinner.

        Args:
            message: Initial status message
            spinner_chars: Characters for spinner animation
            interval: Animation interval in seconds
            dynamic_messages: Whether to use dynamic thinking messages
        """
        self.message = message
        self.initial_message = message
        self.spinner_chars = spinner_chars or Icons.DOTS
        self.interval = interval
        self.dynamic_messages = dynamic_messages and HAS_THINKING_MESSAGES

        self.running = False
        self.frame_index = 0
        self.actions: List[ActionItem] = []
        self.current_action: Optional[int] = None

        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._last_render_lines = 0
        self._start_time: Optional[float] = None
        self._last_message_update: float = 0
        self._message_update_interval: float = 4.0  # Update message every 4 seconds

    def start(self) -> "ActionSpinner":
        """Start the spinner animation."""
        self.running = True
        self._start_time = time.time()
        if self.dynamic_messages:
            start_thinking()
        sys.stdout.write(Color.HIDE_CURSOR)
        sys.stdout.flush()
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        """Stop the spinner animation."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        sys.stdout.write(Color.SHOW_CURSOR)
        sys.stdout.flush()

    def _animate(self) -> None:
        """Animation loop running in background thread."""
        while self.running:
            # Update message dynamically if enabled
            if self.dynamic_messages and self._start_time:
                now = time.time()
                if now - self._last_message_update >= self._message_update_interval:
                    self._last_message_update = now
                    self.message = get_progress_message()

            self._render()
            self.frame_index = (self.frame_index + 1) % len(self.spinner_chars)
            time.sleep(self.interval)

    def _render(self) -> None:
        """Render the current state to terminal."""
        with self._lock:
            # Clear previous output
            if self._last_render_lines > 0:
                sys.stdout.write(f"\033[{self._last_render_lines}A")  # Move up
                for _ in range(self._last_render_lines):
                    sys.stdout.write(Color.CLEAR_LINE + "\n")
                sys.stdout.write(f"\033[{self._last_render_lines}A")  # Move back up

            lines = []

            # Main status line with spinner
            spinner = self.spinner_chars[self.frame_index]
            status_line = f"{Color.BLUE}{spinner}{Color.RESET} {Color.BOLD}{Icons.THINKING}{Color.RESET} {self.message}..."
            lines.append(status_line)

            # Render actions
            for i, action in enumerate(self.actions):
                action_line = self._format_action(action, i == len(self.actions) - 1)
                lines.append(action_line)

                # Render children
                for j, child in enumerate(action.children):
                    child_line = self._format_action(
                        child,
                        j == len(action.children) - 1,
                        indent=2
                    )
                    lines.append(child_line)

            # Write all lines
            output = "\n".join(lines) + "\n"
            sys.stdout.write(output)
            sys.stdout.flush()

            self._last_render_lines = len(lines)

    def _format_action(self, action: ActionItem, is_last: bool, indent: int = 1) -> str:
        """Format a single action line."""
        # Choose tree character
        tree_char = Icons.TREE_BRANCH if is_last else Icons.TREE_TEE
        prefix = "  " * indent + tree_char + " "

        # Format action name with target
        if action.target:
            action_text = f"{action.name}({Color.CYAN}{action.target}{Color.RESET})"
        else:
            action_text = action.name

        # Add state indicator
        if action.state == ActionState.RUNNING:
            state_icon = f"{Color.BLUE}●{Color.RESET}"
        elif action.state == ActionState.SUCCESS:
            state_icon = f"{Color.GREEN}{Icons.SUCCESS}{Color.RESET}"
        elif action.state == ActionState.FAILED:
            state_icon = f"{Color.RED}{Icons.FAILURE}{Color.RESET}"
        elif action.state == ActionState.SKIPPED:
            state_icon = f"{Color.YELLOW}○{Color.RESET}"
        else:
            state_icon = f"{Color.DIM}○{Color.RESET}"

        # Add duration if complete
        duration = ""
        if action.state in (ActionState.SUCCESS, ActionState.FAILED) and action.duration:
            duration = f" {Color.DIM}({action.format_duration()}){Color.RESET}"

        return f"{prefix}{state_icon} {action_text}{duration}"

    def update(self, message: str) -> None:
        """Update the status message.

        Args:
            message: New status message
        """
        with self._lock:
            self.message = message

    def add_action(
        self,
        name: str,
        target: Optional[str] = None,
        parent_index: Optional[int] = None
    ) -> int:
        """Add a new action indicator.

        Args:
            name: Action name (e.g., "Read", "Write", "Execute")
            target: Action target (e.g., filename, command)
            parent_index: Index of parent action for nesting

        Returns:
            Index of the new action
        """
        with self._lock:
            action = ActionItem(
                name=name,
                target=target,
                state=ActionState.RUNNING,
                start_time=time.time()
            )

            if parent_index is not None and parent_index < len(self.actions):
                self.actions[parent_index].children.append(action)
                return len(self.actions[parent_index].children) - 1
            else:
                self.actions.append(action)
                return len(self.actions) - 1

    def complete_action(self, index: int, parent_index: Optional[int] = None) -> None:
        """Mark an action as complete.

        Args:
            index: Action index
            parent_index: Parent index if this is a child action
        """
        with self._lock:
            if parent_index is not None:
                action = self.actions[parent_index].children[index]
            else:
                action = self.actions[index]
            action.state = ActionState.SUCCESS
            action.end_time = time.time()

    def fail_action(
        self,
        index: int,
        message: Optional[str] = None,
        parent_index: Optional[int] = None
    ) -> None:
        """Mark an action as failed.

        Args:
            index: Action index
            message: Error message
            parent_index: Parent index if this is a child action
        """
        with self._lock:
            if parent_index is not None:
                action = self.actions[parent_index].children[index]
            else:
                action = self.actions[index]
            action.state = ActionState.FAILED
            action.message = message
            action.end_time = time.time()

    def success(self, message: str) -> None:
        """Complete spinner with success state.

        Args:
            message: Success message
        """
        self.stop()
        self._render_final(ActionState.SUCCESS, message)

    def failure(self, message: str) -> None:
        """Complete spinner with failure state.

        Args:
            message: Failure message
        """
        self.stop()
        self._render_final(ActionState.FAILED, message)

    def _render_final(self, state: ActionState, message: str) -> None:
        """Render final state after spinner stops."""
        # Clear spinner output
        if self._last_render_lines > 0:
            sys.stdout.write(f"\033[{self._last_render_lines}A")
            for _ in range(self._last_render_lines):
                sys.stdout.write(Color.CLEAR_LINE + "\n")
            sys.stdout.write(f"\033[{self._last_render_lines}A")

        # Render final state
        if state == ActionState.SUCCESS:
            icon = f"{Color.GREEN}{Icons.SUCCESS}{Color.RESET}"
        else:
            icon = f"{Color.RED}{Icons.FAILURE}{Color.RESET}"

        print(f"{icon} {message}")

        # Render completed actions
        for i, action in enumerate(self.actions):
            line = self._format_action(action, i == len(self.actions) - 1)
            print(line)
            for j, child in enumerate(action.children):
                child_line = self._format_action(child, j == len(action.children) - 1, indent=2)
                print(child_line)

    def __enter__(self) -> "ActionSpinner":
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            self.failure(str(exc_val) if exc_val else "Operation failed")
        else:
            self.stop()


# =============================================================================
# Streaming Output Handler
# =============================================================================

class StreamingOutput:
    """
    Handler for streaming text output with proper terminal management.

    Usage:
        stream = StreamingOutput()
        stream.start()
        for token in tokens:
            stream.write(token)
        stream.end()
    """

    def __init__(self, prefix: str = ""):
        """Initialize streaming output.

        Args:
            prefix: Optional prefix for the stream
        """
        self.prefix = prefix
        self.buffer = ""
        self.started = False
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start streaming output."""
        self.started = True
        if self.prefix:
            sys.stdout.write(f"{Color.DIM}{self.prefix}{Color.RESET}")
            sys.stdout.flush()

    def write(self, text: str) -> None:
        """Write text to stream.

        Args:
            text: Text to output
        """
        with self._lock:
            self.buffer += text
            sys.stdout.write(text)
            sys.stdout.flush()

    def writeline(self, text: str) -> None:
        """Write a complete line.

        Args:
            text: Line text
        """
        self.write(text + "\n")

    def end(self, newline: bool = True) -> str:
        """End streaming and return complete output.

        Args:
            newline: Whether to add trailing newline

        Returns:
            Complete buffered text
        """
        if newline and self.buffer and not self.buffer.endswith("\n"):
            sys.stdout.write("\n")
            sys.stdout.flush()
        self.started = False
        return self.buffer

    def clear(self) -> None:
        """Clear the current line."""
        sys.stdout.write(Color.CLEAR_LINE + "\r")
        sys.stdout.flush()


# =============================================================================
# Status Messages
# =============================================================================

def status(message: str, state: str = "info") -> None:
    """Print a status message with icon.

    Args:
        message: Status message
        state: Status type (info, success, error, warning, thinking)
    """
    icons = {
        "info": f"{Color.BLUE}{Icons.INFO}{Color.RESET}",
        "success": f"{Color.GREEN}{Icons.SUCCESS}{Color.RESET}",
        "error": f"{Color.RED}{Icons.FAILURE}{Color.RESET}",
        "warning": f"{Color.YELLOW}{Icons.WARNING}{Color.RESET}",
        "thinking": f"{Color.BLUE}{Icons.THINKING}{Color.RESET}",
    }
    icon = icons.get(state, icons["info"])
    print(f"{icon} {message}")


def thinking(message: str = None, dynamic: bool = True) -> None:
    """Print a thinking/processing status.

    Args:
        message: Custom message (optional, uses dynamic message if None)
        dynamic: Whether to use dynamic thinking messages
    """
    if message is None and dynamic and HAS_THINKING_MESSAGES:
        message = get_thinking_message()
    elif message is None:
        message = "Thinking..."
    status(message, "thinking")


def success(message: str) -> None:
    """Print a success status."""
    status(message, "success")


def error(message: str) -> None:
    """Print an error status."""
    status(message, "error")


def warning(message: str) -> None:
    """Print a warning status."""
    status(message, "warning")


def info(message: str) -> None:
    """Print an info status."""
    status(message, "info")


# =============================================================================
# Action Logging - Claude Code Style
# =============================================================================

def log_action(action: str, target: str, state: str = "running") -> None:
    """Log a tool/action with its target in Claude Code style.

    Format: ● Action(target)

    Args:
        action: Action name (Read, Write, Bash, etc.)
        target: Action target (filename, command, etc.)
        state: Action state (running, success, error)
    """
    # Yellow bullet for all tool calls (Claude Code style)
    bullet = f"{Color.YELLOW}{Icons.BULLET}{Color.RESET}"
    print(f"{bullet} {Color.BOLD}{action}{Color.RESET}({Color.CYAN}{target}{Color.RESET})")


def log_output(output: str, is_error: bool = False, max_lines: int = 10) -> None:
    """Log tool output with Claude Code style corner indentation.

    Format:
      ⎿  Output line 1
         Output line 2

    Args:
        output: Output text to display
        is_error: Whether this is error output
        max_lines: Max lines to show before truncating (0 = no limit)
    """
    if not output or not output.strip():
        return

    lines = output.strip().split('\n')
    show_truncation = max_lines > 0 and len(lines) > max_lines

    if show_truncation:
        display_lines = lines[:max_lines]
    else:
        display_lines = lines

    # Color for output
    text_color = Color.RED if is_error else Color.DIM

    for i, line in enumerate(display_lines):
        if i == 0:
            # First line gets the corner symbol
            prefix = f"  {Color.DIM}{Icons.CORNER}{Color.RESET}  "
        else:
            # Subsequent lines get spacing to align
            prefix = "     "

        if is_error and i == 0:
            # Error prefix for first line
            print(f"{prefix}{Color.RED}Error:{Color.RESET} {text_color}{line}{Color.RESET}")
        else:
            print(f"{prefix}{text_color}{line}{Color.RESET}")

    if show_truncation:
        remaining = len(lines) - max_lines
        print(f"     {Color.DIM}... (+{remaining} more lines){Color.RESET}")


# =============================================================================
# Progress Indicators
# =============================================================================

class InlineProgress:
    """Inline progress indicator that updates in place."""

    def __init__(self, total: int, description: str = ""):
        """Initialize progress.

        Args:
            total: Total number of items
            description: Progress description
        """
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()

    def update(self, amount: int = 1) -> None:
        """Update progress.

        Args:
            amount: Amount to increment
        """
        self.current = min(self.current + amount, self.total)
        self._render()

    def _render(self) -> None:
        """Render progress line."""
        pct = self.current / self.total if self.total > 0 else 0
        bar_width = 20
        filled = int(bar_width * pct)
        bar = "█" * filled + "░" * (bar_width - filled)

        elapsed = time.time() - self.start_time
        eta = ""
        if pct > 0:
            remaining = (elapsed / pct) - elapsed
            eta = f" ETA: {remaining:.0f}s" if remaining > 1 else ""

        desc = f"{self.description}: " if self.description else ""
        line = f"\r{desc}[{bar}] {self.current}/{self.total} ({pct*100:.0f}%){eta}"

        sys.stdout.write(Color.CLEAR_LINE + line)
        sys.stdout.flush()

        if self.current >= self.total:
            print()  # Newline when done

    def finish(self) -> None:
        """Mark as complete."""
        self.current = self.total
        self._render()


# =============================================================================
# Context Managers
# =============================================================================

@contextmanager
def action_spinner(message: str = "Processing"):
    """Context manager for action spinner.

    Usage:
        with action_spinner("Analyzing code") as spinner:
            spinner.add_action("Read", "main.py")
            do_work()
            spinner.complete_action(0)
    """
    spinner = ActionSpinner(message)
    try:
        yield spinner.start()
    except Exception as e:
        spinner.failure(str(e))
        raise
    finally:
        if spinner.running:
            spinner.stop()


@contextmanager
def progress(total: int, description: str = ""):
    """Context manager for progress indicator.

    Usage:
        with progress(100, "Processing files") as p:
            for item in items:
                process(item)
                p.update()
    """
    prog = InlineProgress(total, description)
    try:
        yield prog
    finally:
        prog.finish()


# =============================================================================
# Task Display
# =============================================================================

class TaskDisplay:
    """
    Display for multi-step task execution with Claude Code style.

    Usage:
        task = TaskDisplay("Implementing feature")
        task.start()
        task.step("Analyzing requirements")
        task.action("Read", "spec.md")
        task.complete_step()
        task.step("Writing code")
        task.action("Write", "feature.py")
        task.complete_step()
        task.finish()
    """

    def __init__(self, title: str):
        """Initialize task display.

        Args:
            title: Task title
        """
        self.title = title
        self.steps: List[Dict[str, Any]] = []
        self.current_step: Optional[int] = None
        self.start_time: Optional[float] = None
        self._spinner: Optional[ActionSpinner] = None

    def start(self) -> "TaskDisplay":
        """Start task execution display."""
        self.start_time = time.time()
        print(f"\n{Color.BOLD}{Icons.THINKING} {self.title}{Color.RESET}")
        print(f"{Color.DIM}{'─' * 50}{Color.RESET}\n")
        return self

    def step(self, description: str) -> None:
        """Start a new step.

        Args:
            description: Step description
        """
        # Complete previous spinner if any
        if self._spinner and self._spinner.running:
            self._spinner.stop()

        step_info = {
            "description": description,
            "actions": [],
            "state": ActionState.RUNNING,
            "start_time": time.time()
        }
        self.steps.append(step_info)
        self.current_step = len(self.steps) - 1

        # Start new spinner for this step
        self._spinner = ActionSpinner(description)
        self._spinner.start()

    def action(self, name: str, target: str) -> int:
        """Add an action to current step.

        Args:
            name: Action name
            target: Action target

        Returns:
            Action index
        """
        if self._spinner:
            return self._spinner.add_action(name, target)
        return -1

    def complete_action(self, index: int) -> None:
        """Mark action as complete.

        Args:
            index: Action index
        """
        if self._spinner:
            self._spinner.complete_action(index)

    def fail_action(self, index: int, message: str = "") -> None:
        """Mark action as failed.

        Args:
            index: Action index
            message: Error message
        """
        if self._spinner:
            self._spinner.fail_action(index, message)

    def complete_step(self, message: str = "") -> None:
        """Complete current step.

        Args:
            message: Optional completion message
        """
        if self.current_step is not None:
            self.steps[self.current_step]["state"] = ActionState.SUCCESS
            self.steps[self.current_step]["end_time"] = time.time()

        if self._spinner:
            msg = message or f"Step {self.current_step + 1} complete"
            self._spinner.success(msg)
            self._spinner = None

    def fail_step(self, message: str) -> None:
        """Fail current step.

        Args:
            message: Error message
        """
        if self.current_step is not None:
            self.steps[self.current_step]["state"] = ActionState.FAILED
            self.steps[self.current_step]["end_time"] = time.time()

        if self._spinner:
            self._spinner.failure(message)
            self._spinner = None

    def finish(self, message: str = "") -> None:
        """Finish task display.

        Args:
            message: Completion message
        """
        # Stop any running spinner
        if self._spinner and self._spinner.running:
            self._spinner.stop()

        duration = time.time() - self.start_time if self.start_time else 0

        # Summary
        success_count = sum(1 for s in self.steps if s["state"] == ActionState.SUCCESS)
        failed_count = sum(1 for s in self.steps if s["state"] == ActionState.FAILED)

        print(f"\n{Color.DIM}{'─' * 50}{Color.RESET}")

        if failed_count == 0:
            icon = f"{Color.GREEN}{Icons.SUCCESS}{Color.RESET}"
            status_text = "Complete"
        else:
            icon = f"{Color.YELLOW}{Icons.WARNING}{Color.RESET}"
            status_text = f"Completed with {failed_count} error(s)"

        msg = message or f"{self.title} - {status_text}"
        print(f"{icon} {msg}")
        print(f"{Color.DIM}   {success_count} steps completed in {duration:.1f}s{Color.RESET}\n")


# =============================================================================
# Text Wrapping and Response Formatting
# =============================================================================

def get_terminal_width() -> int:
    """Get terminal width, with fallback to 80 columns.

    Returns:
        Terminal width in columns
    """
    try:
        size = shutil.get_terminal_size()
        return size.columns
    except Exception:
        return 80


def get_response_width(percentage: float = 0.75) -> int:
    """Get the width for response output (default 75% of terminal).

    Args:
        percentage: Fraction of terminal width to use (0.0 to 1.0)

    Returns:
        Width in columns for response text
    """
    terminal_width = get_terminal_width()
    width = int(terminal_width * percentage)
    # Ensure minimum width of 40 and max of terminal width
    return max(40, min(width, terminal_width))


def wrap_text(text: str, width: Optional[int] = None, indent: str = "") -> str:
    """Wrap text to specified width, preserving paragraphs and code blocks.

    Args:
        text: Text to wrap
        width: Maximum width (default: 75% of terminal)
        indent: Prefix for each line

    Returns:
        Wrapped text string
    """
    if width is None:
        width = get_response_width()

    # Adjust width for indent
    effective_width = width - len(indent)
    if effective_width < 20:
        effective_width = 20

    lines = []
    in_code_block = False
    code_block_content = []

    for line in text.split('\n'):
        # Check for code block markers
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block - add as-is
                code_block_content.append(line)
                lines.extend(code_block_content)
                code_block_content = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
                code_block_content = [line]
            continue

        if in_code_block:
            # Inside code block - don't wrap
            code_block_content.append(line)
            continue

        # Empty line - preserve paragraph break
        if not line.strip():
            lines.append("")
            continue

        # Check for list items or special formatting to preserve
        stripped = line.lstrip()
        leading_spaces = len(line) - len(stripped)

        # Preserve list items (- or * or numbered)
        if stripped.startswith(('-', '*', '•')) or re.match(r'^\d+\.', stripped):
            # Wrap list items with hanging indent
            list_indent = ' ' * leading_spaces
            # Find the marker and content
            match = re.match(r'^([-*•]|\d+\.)\s*', stripped)
            if match:
                marker = match.group(0)
                content = stripped[len(marker):]
                subsequent_indent = list_indent + ' ' * len(marker)
                wrapped = textwrap.fill(
                    content,
                    width=effective_width,
                    initial_indent=list_indent + marker,
                    subsequent_indent=subsequent_indent
                )
                lines.append(wrapped)
            else:
                lines.append(line)
            continue

        # Check for headers (## style)
        if stripped.startswith('#'):
            lines.append(line)
            continue

        # Regular paragraph - wrap with preserved leading indent
        if leading_spaces > 0:
            para_indent = ' ' * leading_spaces
            wrapped = textwrap.fill(
                stripped,
                width=effective_width,
                initial_indent=para_indent,
                subsequent_indent=para_indent
            )
        else:
            wrapped = textwrap.fill(stripped, width=effective_width)

        lines.append(wrapped)

    # Handle unclosed code block
    if in_code_block:
        lines.extend(code_block_content)

    # Apply indent to all lines
    if indent:
        lines = [indent + line if line else line for line in lines]

    return '\n'.join(lines)


def format_response(response: str, width_percentage: float = 0.75) -> str:
    """Format an AI response for clean terminal display.

    This wraps text to 75% of terminal width (configurable) while:
    - Preserving code blocks (``` ... ```)
    - Preserving list formatting
    - Preserving headers
    - Maintaining paragraph breaks

    Args:
        response: The response text to format
        width_percentage: Fraction of terminal width to use

    Returns:
        Formatted response string
    """
    if not response:
        return response

    width = get_response_width(width_percentage)
    return wrap_text(response, width)


def print_response(response: str, width_percentage: float = 0.75) -> None:
    """Print a formatted response with proper text wrapping.

    The agent's response is visually distinct from user input with:
    - A colored "NC1709" header
    - Cyan-colored text
    - Left border indicator

    Args:
        response: Response text to print
        width_percentage: Fraction of terminal width to use
    """
    # Account for border prefix "│ " (2 chars) in width calculation
    # Reduce percentage slightly to ensure text + border fits within 75% of terminal
    border_width = 2
    terminal_width = get_terminal_width()
    effective_percentage = (width_percentage * terminal_width - border_width) / terminal_width

    formatted = format_response(response, effective_percentage)

    # Add visual distinction for agent responses
    # Header with robot icon and name
    header = f"\n{Color.BOLD}{Color.CYAN}◆ NC1709{Color.RESET}"

    # Add subtle left border by indenting and coloring
    lines = formatted.split('\n')
    bordered_lines = []
    for line in lines:
        # Use dim cyan vertical bar as left border + agent text in cyan
        bordered_lines.append(f"{Color.DIM}{Color.CYAN}│{Color.RESET} {Color.CYAN}{line}{Color.RESET}")

    bordered_response = '\n'.join(bordered_lines)

    print(header)
    print(bordered_response)
    print()  # Extra line for spacing


# =============================================================================
# Demo / Test
# =============================================================================

def demo():
    """Demonstrate CLI UI components - Claude Code style."""
    print("\n" + "=" * 60)
    print("NC1709 CLI UI Demo - Claude Code Style")
    print("=" * 60 + "\n")

    # Demo 1: Claude Code style tool calls
    print("Demo 1: Tool Calls (Claude Code Style)")
    print("-" * 40)

    # Simulate tool calls with output
    log_action("Read", "main.py")
    log_output("def main():\n    print('Hello World')\n\nif __name__ == '__main__':\n    main()")

    log_action("Bash", "python main.py")
    log_output("Hello World")

    log_action("Bash", "python broken.py")
    log_output("ModuleNotFoundError: No module named 'nonexistent'", is_error=True)

    print()

    # Demo 2: Status messages
    print("Demo 2: Status Messages")
    print("-" * 40)
    thinking("Processing your request...")
    info("Found 5 relevant files")
    success("Analysis complete")
    warning("One file needs review")
    error("Failed to parse config.json")
    print()

    # Demo 3: Multi-line output with truncation
    print("Demo 3: Multi-line Output")
    print("-" * 40)
    log_action("Grep", "TODO")
    long_output = "\n".join([f"src/file{i}.py:42: # TODO: implement feature {i}" for i in range(15)])
    log_output(long_output, max_lines=5)

    print()

    # Demo 4: Response formatting
    print("Demo 4: Agent Response")
    print("-" * 40)
    sample_response = """I've analyzed your codebase and found the following:

1. The main entry point is in `main.py`
2. Configuration is loaded from `config.json`
3. There are 3 utility modules in the `utils/` directory

Here's a quick example of how to run it:

```python
from myapp import main
main.run()
```

Let me know if you need any additional help!"""
    print_response(sample_response)

    print("Demo complete!")


if __name__ == "__main__":
    demo()
