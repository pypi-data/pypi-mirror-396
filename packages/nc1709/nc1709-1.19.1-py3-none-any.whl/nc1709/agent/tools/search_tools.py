"""
Search Tools

Tools for searching file contents:
- Grep: Search for patterns in files
"""

import re
import subprocess
from pathlib import Path
from typing import Optional, List

from .base import Tool, ToolResult, ToolParameter, ToolPermission


class GrepTool(Tool):
    """Search for patterns in files"""

    name = "Grep"
    description = (
        "Search for a pattern in files using regex. "
        "Returns matching lines with file paths and line numbers. "
        "Supports full regex syntax."
    )
    category = "search"
    permission = ToolPermission.AUTO  # Safe to auto-execute

    parameters = [
        ToolParameter(
            name="pattern",
            description="Regular expression pattern to search for",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="path",
            description="File or directory to search in (defaults to current directory)",
            type="string",
            required=False,
            default=".",
        ),
        ToolParameter(
            name="glob",
            description="Glob pattern to filter files (e.g., '*.py', '*.ts')",
            type="string",
            required=False,
        ),
        ToolParameter(
            name="case_insensitive",
            description="Perform case-insensitive search",
            type="boolean",
            required=False,
            default=False,
        ),
        ToolParameter(
            name="context_lines",
            description="Number of context lines to show before and after matches",
            type="integer",
            required=False,
            default=0,
        ),
        ToolParameter(
            name="max_results",
            description="Maximum number of results to return",
            type="integer",
            required=False,
            default=50,
        ),
    ]

    def execute(
        self,
        pattern: str,
        path: str = ".",
        glob: str = None,
        case_insensitive: bool = False,
        context_lines: int = 0,
        max_results: int = 50,
    ) -> ToolResult:
        """Search for pattern in files"""

        base_path = Path(path).expanduser()

        if not base_path.exists():
            return ToolResult(
                success=False,
                output="",
                error=f"Path not found: {path}",
                target=pattern,
            )

        try:
            # Compile regex
            flags = re.IGNORECASE if case_insensitive else 0
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Invalid regex pattern: {e}",
                    target=pattern,
                )

            # Find files to search
            if base_path.is_file():
                files = [base_path]
            else:
                if glob:
                    files = list(base_path.glob(f"**/{glob}"))
                else:
                    # Search common code files by default
                    files = []
                    for ext in ["*.py", "*.js", "*.ts", "*.tsx", "*.jsx", "*.go", "*.rs",
                               "*.java", "*.c", "*.cpp", "*.h", "*.hpp", "*.md", "*.txt",
                               "*.json", "*.yaml", "*.yml", "*.toml", "*.sh", "*.bash"]:
                        files.extend(base_path.glob(f"**/{ext}"))

                files = [f for f in files if f.is_file()]

            # Skip binary files and very large files
            max_file_size = 1_000_000  # 1MB
            text_files = []
            for f in files:
                try:
                    if f.stat().st_size <= max_file_size:
                        text_files.append(f)
                except OSError:
                    continue

            # Search files
            results = []
            total_matches = 0

            for file_path in text_files:
                if total_matches >= max_results:
                    break

                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        lines = f.readlines()

                    for i, line in enumerate(lines):
                        if regex.search(line):
                            total_matches += 1

                            # Get context
                            start = max(0, i - context_lines)
                            end = min(len(lines), i + context_lines + 1)

                            context = []
                            for j in range(start, end):
                                prefix = ">" if j == i else " "
                                context.append(f"{prefix} {j+1:4}: {lines[j].rstrip()}")

                            rel_path = file_path.relative_to(base_path) if file_path.is_relative_to(base_path) else file_path
                            results.append({
                                "file": str(rel_path),
                                "line": i + 1,
                                "content": line.rstrip(),
                                "context": "\n".join(context) if context_lines > 0 else None,
                            })

                            if total_matches >= max_results:
                                break

                except (OSError, UnicodeDecodeError):
                    continue

            # Format output
            if not results:
                return ToolResult(
                    success=True,
                    output=f"No matches found for pattern: {pattern}",
                    target=pattern,
                    data={"count": 0, "matches": []},
                )

            output_lines = [f"Found {len(results)} match(es) for '{pattern}':"]
            for r in results:
                output_lines.append(f"\n{r['file']}:{r['line']}")
                if r.get("context"):
                    output_lines.append(r["context"])
                else:
                    output_lines.append(f"  {r['content'][:200]}")

            if total_matches >= max_results:
                output_lines.append(f"\n... (limited to {max_results} results)")

            return ToolResult(
                success=True,
                output="\n".join(output_lines),
                target=pattern,
                data={"count": len(results), "matches": results},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error searching: {e}",
                target=pattern,
            )


class RipgrepTool(Tool):
    """Fast search using ripgrep (if available)"""

    name = "Ripgrep"
    description = (
        "Fast file search using ripgrep (rg). "
        "Falls back to Python grep if ripgrep is not installed."
    )
    category = "search"
    permission = ToolPermission.AUTO

    parameters = [
        ToolParameter(
            name="pattern",
            description="Search pattern (regex)",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="path",
            description="Path to search in",
            type="string",
            required=False,
            default=".",
        ),
        ToolParameter(
            name="type",
            description="File type to search (e.g., 'py', 'js', 'ts')",
            type="string",
            required=False,
        ),
        ToolParameter(
            name="case_insensitive",
            description="Case-insensitive search",
            type="boolean",
            required=False,
            default=False,
        ),
    ]

    def execute(
        self,
        pattern: str,
        path: str = ".",
        type: str = None,
        case_insensitive: bool = False,
    ) -> ToolResult:
        """Search using ripgrep"""

        # Build command
        cmd = ["rg", "--line-number", "--no-heading", "--color=never"]

        if case_insensitive:
            cmd.append("-i")

        if type:
            cmd.extend(["-t", type])

        cmd.extend(["--max-count=100", pattern, path])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                output = result.stdout
                lines = output.strip().split("\n") if output.strip() else []
                return ToolResult(
                    success=True,
                    output=output if output else "No matches found",
                    target=pattern,
                    data={"count": len(lines)},
                )
            elif result.returncode == 1:
                # No matches
                return ToolResult(
                    success=True,
                    output="No matches found",
                    target=pattern,
                    data={"count": 0},
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=result.stderr or "ripgrep error",
                    target=pattern,
                )

        except FileNotFoundError:
            # ripgrep not installed, fall back to grep tool
            grep = GrepTool()
            return grep.execute(pattern=pattern, path=path, case_insensitive=case_insensitive)
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error="Search timed out",
                target=pattern,
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Search error: {e}",
                target=pattern,
            )


def register_search_tools(registry):
    """Register all search tools with a registry"""
    registry.register_class(GrepTool)
    registry.register_class(RipgrepTool)
