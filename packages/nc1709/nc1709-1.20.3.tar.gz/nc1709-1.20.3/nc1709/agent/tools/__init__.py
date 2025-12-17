"""
NC1709 Agent Tools

Built-in tools for the agentic CLI:
- File operations: Read, Write, Edit, Glob
- Search operations: Grep, Ripgrep
- Execution: Bash, BackgroundBash
- Sub-agents: Task, TodoWrite, AskUser
- Web: WebFetch, WebSearch, WebScreenshot
- Notebook: NotebookRead, NotebookEdit, NotebookRun
"""

from .base import Tool, ToolResult, ToolRegistry, ToolPermission, ToolParameter

__all__ = [
    "Tool",
    "ToolResult",
    "ToolRegistry",
    "ToolPermission",
    "ToolParameter",
]
