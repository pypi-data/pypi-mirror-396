"""
Progress Indicators
Rich progress bars and status displays for long-running operations.

Features:
- Progress bars (determinate)
- Spinners (indeterminate)
- Status lines
- Multi-step progress
- Streaming progress for LLM output
- Async progress support
"""
import sys
import time
import threading
import asyncio
from typing import Optional, Callable, List, Any, AsyncIterator
from enum import Enum
from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass, field


class SpinnerStyle(Enum):
    """Available spinner styles"""
    DOTS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    BRAILLE = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    ARROWS = ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"]
    CLOCK = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"]
    MOON = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
    BOUNCE = ["⠁", "⠂", "⠄", "⠂"]
    SIMPLE = ["-", "\\", "|", "/"]


class ProgressBar:
    """Simple progress bar for terminal output"""

    def __init__(
        self,
        total: int,
        description: str = "",
        width: int = 40,
        fill_char: str = "█",
        empty_char: str = "░"
    ):
        """Initialize progress bar

        Args:
            total: Total number of steps
            description: Description text
            width: Width of progress bar in characters
            fill_char: Character for filled portion
            empty_char: Character for empty portion
        """
        self.total = total
        self.description = description
        self.width = width
        self.fill_char = fill_char
        self.empty_char = empty_char
        self.current = 0
        self.start_time = time.time()

    def update(self, amount: int = 1) -> None:
        """Update progress

        Args:
            amount: Amount to increment
        """
        self.current = min(self.current + amount, self.total)
        self._render()

    def set(self, value: int) -> None:
        """Set progress to specific value

        Args:
            value: New progress value
        """
        self.current = min(value, self.total)
        self._render()

    def _render(self) -> None:
        """Render progress bar to terminal"""
        percentage = self.current / self.total if self.total > 0 else 0
        filled_width = int(self.width * percentage)
        empty_width = self.width - filled_width

        bar = self.fill_char * filled_width + self.empty_char * empty_width

        # Calculate elapsed time and ETA
        elapsed = time.time() - self.start_time
        if percentage > 0:
            eta = elapsed / percentage - elapsed
            eta_str = f" ETA: {self._format_time(eta)}"
        else:
            eta_str = ""

        # Build progress line
        desc = f"{self.description}: " if self.description else ""
        line = f"\r{desc}[{bar}] {self.current}/{self.total} ({percentage*100:.1f}%){eta_str}"

        sys.stdout.write(line)
        sys.stdout.flush()

        if self.current >= self.total:
            print()  # New line when complete

    def _format_time(self, seconds: float) -> str:
        """Format seconds as human-readable time"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"

    def finish(self) -> None:
        """Mark progress as complete"""
        self.set(self.total)


class Spinner:
    """Animated spinner for indeterminate progress"""

    def __init__(
        self,
        message: str = "Processing",
        style: SpinnerStyle = SpinnerStyle.DOTS
    ):
        """Initialize spinner

        Args:
            message: Message to display with spinner
            style: Spinner animation style
        """
        self.message = message
        self.frames = style.value
        self.frame_index = 0
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self) -> "Spinner":
        """Start spinner animation"""
        self.running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()
        return self

    def stop(self, final_message: Optional[str] = None) -> None:
        """Stop spinner animation

        Args:
            final_message: Optional message to display after stopping
        """
        self.running = False
        if self._thread:
            self._thread.join(timeout=0.5)

        # Clear spinner line
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

        if final_message:
            print(final_message)

    def _animate(self) -> None:
        """Animation loop"""
        while self.running:
            with self._lock:
                frame = self.frames[self.frame_index]
                sys.stdout.write(f"\r{frame} {self.message}")
                sys.stdout.flush()
                self.frame_index = (self.frame_index + 1) % len(self.frames)
            time.sleep(0.1)

    def update_message(self, message: str) -> None:
        """Update spinner message

        Args:
            message: New message
        """
        with self._lock:
            # Clear old message
            old_len = len(self.message) + 10
            sys.stdout.write("\r" + " " * old_len + "\r")
            self.message = message

    def __enter__(self) -> "Spinner":
        return self.start()

    def __exit__(self, *args) -> None:
        self.stop()


class StatusLine:
    """Status line that updates in place"""

    def __init__(self):
        """Initialize status line"""
        self.current_line = ""

    def update(self, message: str, prefix: str = "→") -> None:
        """Update status line

        Args:
            message: Status message
            prefix: Prefix character/emoji
        """
        # Clear old line
        clear_len = len(self.current_line) + 5
        sys.stdout.write("\r" + " " * clear_len + "\r")

        # Write new line
        self.current_line = f"{prefix} {message}"
        sys.stdout.write(self.current_line)
        sys.stdout.flush()

    def success(self, message: str) -> None:
        """Show success message"""
        self.update(message, "✅")
        print()  # New line after success

    def error(self, message: str) -> None:
        """Show error message"""
        self.update(message, "❌")
        print()  # New line after error

    def info(self, message: str) -> None:
        """Show info message"""
        self.update(message, "ℹ️")

    def warning(self, message: str) -> None:
        """Show warning message"""
        self.update(message, "⚠️")

    def clear(self) -> None:
        """Clear status line"""
        clear_len = len(self.current_line) + 5
        sys.stdout.write("\r" + " " * clear_len + "\r")
        sys.stdout.flush()
        self.current_line = ""


class MultiStepProgress:
    """Progress indicator for multi-step operations"""

    def __init__(self, steps: List[str]):
        """Initialize multi-step progress

        Args:
            steps: List of step descriptions
        """
        self.steps = steps
        self.current_step = 0
        self.step_statuses: List[str] = ["pending"] * len(steps)

    def start_step(self, index: Optional[int] = None) -> None:
        """Start a step

        Args:
            index: Step index (uses current_step if None)
        """
        if index is None:
            index = self.current_step

        self.step_statuses[index] = "running"
        self._render()

    def complete_step(self, index: Optional[int] = None) -> None:
        """Mark step as complete

        Args:
            index: Step index (uses current_step if None)
        """
        if index is None:
            index = self.current_step

        self.step_statuses[index] = "completed"
        self.current_step = index + 1
        self._render()

    def fail_step(self, index: Optional[int] = None, error: str = "") -> None:
        """Mark step as failed

        Args:
            index: Step index (uses current_step if None)
            error: Error message
        """
        if index is None:
            index = self.current_step

        self.step_statuses[index] = f"failed: {error}" if error else "failed"
        self._render()

    def _render(self) -> None:
        """Render progress to terminal"""
        print()  # New line before rendering
        print("=" * 50)

        for i, (step, status) in enumerate(zip(self.steps, self.step_statuses)):
            if status == "completed":
                icon = "✅"
            elif status == "running":
                icon = "🔄"
            elif status.startswith("failed"):
                icon = "❌"
            else:
                icon = "⬜"

            step_num = f"[{i + 1}/{len(self.steps)}]"
            print(f"  {icon} {step_num} {step}")

            if status.startswith("failed:"):
                error_msg = status.split(": ", 1)[1]
                print(f"      └─ Error: {error_msg}")

        print("=" * 50)

    def is_complete(self) -> bool:
        """Check if all steps are complete"""
        return all(s == "completed" for s in self.step_statuses)

    def has_failures(self) -> bool:
        """Check if any step failed"""
        return any(s.startswith("failed") for s in self.step_statuses)


@contextmanager
def spinner_context(message: str, style: SpinnerStyle = SpinnerStyle.DOTS):
    """Context manager for spinner

    Usage:
        with spinner_context("Loading...") as spinner:
            do_something()
            spinner.update_message("Almost done...")
    """
    spinner = Spinner(message, style)
    try:
        yield spinner.start()
    finally:
        spinner.stop()


@contextmanager
def progress_context(
    total: int,
    description: str = "",
    callback: Optional[Callable[[ProgressBar], None]] = None
):
    """Context manager for progress bar

    Usage:
        with progress_context(100, "Processing") as progress:
            for i in range(100):
                do_work()
                progress.update()
    """
    progress = ProgressBar(total, description)
    try:
        yield progress
    finally:
        progress.finish()


class TaskProgress:
    """High-level progress tracker for NC1709 tasks"""

    def __init__(self, task_description: str):
        """Initialize task progress

        Args:
            task_description: Description of the task
        """
        self.description = task_description
        self.status = StatusLine()
        self.start_time = time.time()

    def thinking(self, detail: str = "") -> None:
        """Show thinking/processing state"""
        msg = f"Thinking: {self.description}"
        if detail:
            msg += f" ({detail})"
        self.status.update(msg, "🧠")

    def generating(self, detail: str = "") -> None:
        """Show generating state"""
        msg = f"Generating: {self.description}"
        if detail:
            msg += f" ({detail})"
        self.status.update(msg, "✨")

    def executing(self, detail: str = "") -> None:
        """Show executing state"""
        msg = f"Executing: {self.description}"
        if detail:
            msg += f" ({detail})"
        self.status.update(msg, "⚡")

    def complete(self, result: str = "") -> None:
        """Mark task as complete"""
        elapsed = time.time() - self.start_time
        msg = f"Completed: {self.description} ({elapsed:.1f}s)"
        if result:
            msg += f" - {result}"
        self.status.success(msg)

    def failed(self, error: str) -> None:
        """Mark task as failed"""
        elapsed = time.time() - self.start_time
        msg = f"Failed: {self.description} ({elapsed:.1f}s) - {error}"
        self.status.error(msg)


# Convenience functions
def show_spinner(message: str, duration: float = 0) -> Spinner:
    """Show a spinner with message

    Args:
        message: Spinner message
        duration: Auto-stop after duration seconds (0 = manual stop)

    Returns:
        Spinner instance
    """
    spinner = Spinner(message)
    spinner.start()

    if duration > 0:
        def stop_after():
            time.sleep(duration)
            spinner.stop()
        threading.Thread(target=stop_after, daemon=True).start()

    return spinner


def show_progress(
    items: List[Any],
    description: str = "",
    process_func: Optional[Callable[[Any], None]] = None
) -> None:
    """Show progress while processing items

    Args:
        items: Items to process
        description: Progress description
        process_func: Function to call for each item
    """
    progress = ProgressBar(len(items), description)

    for item in items:
        if process_func:
            process_func(item)
        progress.update()


@dataclass
class StreamingStats:
    """Statistics for streaming output"""
    tokens: int = 0
    chars: int = 0
    lines: int = 0
    start_time: float = field(default_factory=time.time)
    first_token_time: Optional[float] = None

    @property
    def elapsed(self) -> float:
        return time.time() - self.start_time

    @property
    def tokens_per_second(self) -> float:
        if self.elapsed > 0:
            return self.tokens / self.elapsed
        return 0

    @property
    def time_to_first_token(self) -> Optional[float]:
        if self.first_token_time:
            return self.first_token_time - self.start_time
        return None


class StreamingProgress:
    """Progress indicator for streaming LLM output

    Shows token count, speed, and elapsed time while streaming.
    """

    def __init__(self, show_stats: bool = True, show_cursor: bool = True):
        """Initialize streaming progress

        Args:
            show_stats: Whether to show statistics
            show_cursor: Whether to show typing cursor
        """
        self.show_stats = show_stats
        self.show_cursor = show_cursor
        self.stats = StreamingStats()
        self._cursor_visible = False
        self._lock = threading.Lock()
        self._status_line = ""

    def on_token(self, token: str) -> None:
        """Called when a new token is received

        Args:
            token: The received token
        """
        with self._lock:
            if self.stats.first_token_time is None:
                self.stats.first_token_time = time.time()

            self.stats.tokens += 1
            self.stats.chars += len(token)
            self.stats.lines += token.count('\n')

            if self.show_stats:
                self._update_status()

    def _update_status(self) -> None:
        """Update status display"""
        ttft = self.stats.time_to_first_token
        ttft_str = f" TTFT: {ttft:.2f}s |" if ttft else ""

        status = (
            f"\r\033[K"  # Clear line
            f"📊 {self.stats.tokens} tokens |"
            f" {self.stats.tokens_per_second:.1f} tok/s |"
            f"{ttft_str}"
            f" {self.stats.elapsed:.1f}s"
        )
        self._status_line = status

    def show_status(self) -> None:
        """Display current status"""
        if self.show_stats and self._status_line:
            sys.stdout.write(self._status_line)
            sys.stdout.flush()

    def hide_status(self) -> None:
        """Hide status display"""
        if self._status_line:
            sys.stdout.write("\r\033[K")  # Clear line
            sys.stdout.flush()
            self._status_line = ""

    def finish(self) -> StreamingStats:
        """Mark streaming as complete and return stats"""
        self.hide_status()
        return self.stats

    def get_summary(self) -> str:
        """Get a summary of streaming statistics"""
        ttft = self.stats.time_to_first_token
        ttft_str = f", TTFT: {ttft:.2f}s" if ttft else ""

        return (
            f"Generated {self.stats.tokens} tokens "
            f"({self.stats.tokens_per_second:.1f} tok/s{ttft_str}) "
            f"in {self.stats.elapsed:.1f}s"
        )


class AsyncSpinner:
    """Async-friendly spinner for use with asyncio"""

    def __init__(
        self,
        message: str = "Processing",
        style: SpinnerStyle = SpinnerStyle.DOTS
    ):
        self.message = message
        self.frames = style.value
        self.frame_index = 0
        self.running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> "AsyncSpinner":
        """Start spinner animation"""
        self.running = True
        self._task = asyncio.create_task(self._animate())
        return self

    async def stop(self, final_message: Optional[str] = None) -> None:
        """Stop spinner animation"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        # Clear spinner line
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

        if final_message:
            print(final_message)

    async def _animate(self) -> None:
        """Animation loop"""
        while self.running:
            frame = self.frames[self.frame_index]
            sys.stdout.write(f"\r{frame} {self.message}")
            sys.stdout.flush()
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            await asyncio.sleep(0.1)

    def update_message(self, message: str) -> None:
        """Update spinner message"""
        old_len = len(self.message) + 10
        sys.stdout.write("\r" + " " * old_len + "\r")
        self.message = message

    async def __aenter__(self) -> "AsyncSpinner":
        return await self.start()

    async def __aexit__(self, *args) -> None:
        await self.stop()


@asynccontextmanager
async def async_spinner_context(
    message: str,
    style: SpinnerStyle = SpinnerStyle.DOTS
):
    """Async context manager for spinner

    Usage:
        async with async_spinner_context("Loading...") as spinner:
            await do_something()
    """
    spinner = AsyncSpinner(message, style)
    try:
        yield await spinner.start()
    finally:
        await spinner.stop()


class ToolExecutionProgress:
    """Progress indicator for tool execution

    Shows which tool is being executed and its status.
    """

    def __init__(self):
        self._current_tool: Optional[str] = None
        self._tools_executed: List[dict] = []
        self._start_time: Optional[float] = None

    def start_tool(self, tool_name: str, description: str = "") -> None:
        """Mark tool execution start"""
        self._current_tool = tool_name
        self._start_time = time.time()

        icon = self._get_tool_icon(tool_name)
        msg = f"{icon} Executing: {tool_name}"
        if description:
            msg += f" ({description})"

        sys.stdout.write(f"\r\033[K{msg}")
        sys.stdout.flush()

    def complete_tool(self, success: bool = True, result: str = "") -> None:
        """Mark tool execution complete"""
        if self._current_tool and self._start_time:
            elapsed = time.time() - self._start_time
            self._tools_executed.append({
                "tool": self._current_tool,
                "success": success,
                "elapsed": elapsed,
            })

            icon = "✅" if success else "❌"
            msg = f"{icon} {self._current_tool} ({elapsed:.2f}s)"
            if result:
                msg += f" → {result[:50]}"

            sys.stdout.write(f"\r\033[K{msg}\n")
            sys.stdout.flush()

        self._current_tool = None
        self._start_time = None

    def _get_tool_icon(self, tool_name: str) -> str:
        """Get icon for tool"""
        icons = {
            "Read": "📖",
            "Write": "✏️",
            "Edit": "📝",
            "MultiEdit": "📑",
            "Glob": "🔍",
            "Grep": "🔎",
            "Bash": "💻",
            "WebFetch": "🌐",
            "WebSearch": "🔍",
            "ReadImage": "🖼️",
        }
        return icons.get(tool_name, "🔧")

    def get_summary(self) -> str:
        """Get execution summary"""
        if not self._tools_executed:
            return "No tools executed"

        total = len(self._tools_executed)
        success = sum(1 for t in self._tools_executed if t["success"])
        total_time = sum(t["elapsed"] for t in self._tools_executed)

        return f"Executed {total} tools ({success} success) in {total_time:.2f}s"


class LiveOutput:
    """Live updating output for long-running operations

    Supports both line-by-line and streaming updates.
    """

    def __init__(self, max_lines: int = 10):
        """Initialize live output

        Args:
            max_lines: Maximum lines to display
        """
        self.max_lines = max_lines
        self._lines: List[str] = []
        self._lock = threading.Lock()

    def add_line(self, line: str) -> None:
        """Add a new line"""
        with self._lock:
            self._lines.append(line)
            if len(self._lines) > self.max_lines:
                self._lines = self._lines[-self.max_lines:]
            self._render()

    def update_last(self, line: str) -> None:
        """Update the last line"""
        with self._lock:
            if self._lines:
                self._lines[-1] = line
            else:
                self._lines.append(line)
            self._render()

    def _render(self) -> None:
        """Render output"""
        # Move cursor up and clear lines
        for _ in range(len(self._lines)):
            sys.stdout.write("\033[A\033[K")

        # Print current lines
        for line in self._lines:
            print(line)

        sys.stdout.flush()

    def clear(self) -> None:
        """Clear output"""
        with self._lock:
            for _ in range(len(self._lines)):
                sys.stdout.write("\033[A\033[K")
            sys.stdout.flush()
            self._lines = []


# Global tool progress instance for easy access
_tool_progress: Optional[ToolExecutionProgress] = None


def get_tool_progress() -> ToolExecutionProgress:
    """Get or create global tool progress instance"""
    global _tool_progress
    if _tool_progress is None:
        _tool_progress = ToolExecutionProgress()
    return _tool_progress
