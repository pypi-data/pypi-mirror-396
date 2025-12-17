"""
File Operation Tools

Tools for reading, writing, and editing files:
- Read: Read file contents
- Write: Write/create files
- Edit: Make precise edits to files

Includes checkpoint integration for undo/rewind functionality.
"""

import os
from pathlib import Path
from typing import Optional
import difflib

from .base import Tool, ToolResult, ToolParameter, ToolPermission

# Import checkpoint system
try:
    from ...checkpoints import get_checkpoint_manager, checkpoint_before_edit, checkpoint_before_write
    HAS_CHECKPOINTS = True
except ImportError:
    HAS_CHECKPOINTS = False

# Import git integration
try:
    from ...git_integration import get_git_integration, auto_commit_after_edit
    HAS_GIT = True
except ImportError:
    HAS_GIT = False


class ReadTool(Tool):
    """Read contents of a file"""

    name = "Read"
    description = "Read the contents of a file. Use this to examine code, configuration, or any text file."
    category = "file"
    permission = ToolPermission.AUTO  # Safe to auto-execute

    parameters = [
        ToolParameter(
            name="file_path",
            description="The absolute path to the file to read",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="offset",
            description="Line number to start reading from (1-indexed). Use for large files.",
            type="integer",
            required=False,
            default=None,
        ),
        ToolParameter(
            name="limit",
            description="Maximum number of lines to read. Use for large files.",
            type="integer",
            required=False,
            default=None,
        ),
    ]

    def execute(self, file_path: str, offset: int = None, limit: int = None) -> ToolResult:
        """Read file contents"""
        path = Path(file_path).expanduser()

        # Check if file exists
        if not path.exists():
            return ToolResult(
                success=False,
                output="",
                error=f"File not found: {file_path}",
                target=file_path,
            )

        # Check if it's a file
        if not path.is_file():
            return ToolResult(
                success=False,
                output="",
                error=f"Not a file: {file_path}",
                target=file_path,
            )

        try:
            # Read the file
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total_lines = len(lines)

            # Apply offset and limit
            start = (offset - 1) if offset else 0
            start = max(0, min(start, total_lines))

            if limit:
                end = start + limit
            else:
                end = total_lines

            selected_lines = lines[start:end]

            # Format output with line numbers
            output_lines = []
            for i, line in enumerate(selected_lines, start=start + 1):
                # Truncate very long lines
                if len(line) > 2000:
                    line = line[:2000] + "... (truncated)\n"
                output_lines.append(f"{i:6}→{line.rstrip()}")

            output = "\n".join(output_lines)

            # Add info about truncation
            if start > 0 or end < total_lines:
                output = f"Showing lines {start + 1}-{end} of {total_lines}\n\n{output}"

            return ToolResult(
                success=True,
                output=output,
                target=file_path,
                data={
                    "total_lines": total_lines,
                    "lines_shown": len(selected_lines),
                    "start_line": start + 1,
                    "end_line": end,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error reading file: {e}",
                target=file_path,
            )


class WriteTool(Tool):
    """Write content to a file"""

    name = "Write"
    description = "Write content to a file. Creates the file if it doesn't exist, or overwrites if it does."
    category = "file"
    permission = ToolPermission.ASK  # Ask before writing

    parameters = [
        ToolParameter(
            name="file_path",
            description="The absolute path to the file to write",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="content",
            description="The content to write to the file",
            type="string",
            required=True,
        ),
    ]

    def execute(self, file_path: str, content: str) -> ToolResult:
        """Write content to file"""
        path = Path(file_path).expanduser()

        try:
            # Create checkpoint before writing
            if HAS_CHECKPOINTS:
                checkpoint_before_write(str(path.absolute()))

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Check if file exists for reporting
            existed = path.exists()
            old_size = path.stat().st_size if existed else 0

            # Write the file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            new_size = path.stat().st_size
            action = "Updated" if existed else "Created"

            return ToolResult(
                success=True,
                output=f"{action} {file_path} ({new_size} bytes, {len(content.splitlines())} lines)",
                target=file_path,
                data={
                    "action": action.lower(),
                    "size": new_size,
                    "lines": len(content.splitlines()),
                },
            )

        except PermissionError:
            return ToolResult(
                success=False,
                output="",
                error=f"Permission denied: {file_path}",
                target=file_path,
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error writing file: {e}",
                target=file_path,
            )


class EditTool(Tool):
    """Make precise edits to a file"""

    name = "Edit"
    description = (
        "Make a precise edit to a file by replacing an exact string with new content. "
        "The old_string must match exactly (including whitespace and indentation). "
        "Use replace_all=true to replace all occurrences."
    )
    category = "file"
    permission = ToolPermission.ASK  # Ask before editing

    parameters = [
        ToolParameter(
            name="file_path",
            description="The absolute path to the file to edit",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="old_string",
            description="The exact string to find and replace (must match exactly)",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="new_string",
            description="The new string to replace it with",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="replace_all",
            description="Replace all occurrences instead of just the first",
            type="boolean",
            required=False,
            default=False,
        ),
    ]

    def execute(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ) -> ToolResult:
        """Edit file by replacing string"""
        path = Path(file_path).expanduser()

        # Check if file exists
        if not path.exists():
            return ToolResult(
                success=False,
                output="",
                error=f"File not found: {file_path}",
                target=file_path,
            )

        try:
            # Create checkpoint before editing
            if HAS_CHECKPOINTS:
                checkpoint_before_edit(str(path.absolute()))

            # Read current content
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if old_string exists
            if old_string not in content:
                # Try to find similar strings for helpful error
                lines = content.split("\n")
                similar = []
                for i, line in enumerate(lines):
                    if any(word in line for word in old_string.split()[:3]):
                        similar.append(f"  Line {i+1}: {line[:80]}")
                        if len(similar) >= 3:
                            break

                error_msg = f"String not found in file: {file_path}"
                if similar:
                    error_msg += f"\n\nSimilar lines found:\n" + "\n".join(similar)

                return ToolResult(
                    success=False,
                    output="",
                    error=error_msg,
                    target=file_path,
                )

            # Count occurrences
            count = content.count(old_string)

            # Check for ambiguity
            if count > 1 and not replace_all:
                return ToolResult(
                    success=False,
                    output="",
                    error=(
                        f"Found {count} occurrences of the string. "
                        "Either make old_string more specific to match uniquely, "
                        "or set replace_all=true to replace all occurrences."
                    ),
                    target=file_path,
                )

            # Perform replacement
            if replace_all:
                new_content = content.replace(old_string, new_string)
                replaced_count = count
            else:
                new_content = content.replace(old_string, new_string, 1)
                replaced_count = 1

            # Write back
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

            # Generate diff for output
            old_lines = content.splitlines(keepends=True)
            new_lines = new_content.splitlines(keepends=True)
            diff = difflib.unified_diff(
                old_lines, new_lines,
                fromfile=f"a/{path.name}",
                tofile=f"b/{path.name}",
                lineterm=""
            )
            diff_text = "".join(list(diff)[:50])  # Limit diff size

            return ToolResult(
                success=True,
                output=f"Replaced {replaced_count} occurrence(s) in {file_path}\n\n{diff_text}",
                target=file_path,
                data={
                    "replacements": replaced_count,
                    "file": file_path,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error editing file: {e}",
                target=file_path,
            )


class MultiEditTool(Tool):
    """Edit multiple files in a single atomic operation"""

    name = "MultiEdit"
    description = (
        "Edit multiple files in a single atomic operation. Useful for refactoring, "
        "renaming across files, or making coordinated changes. All edits succeed or none do."
    )
    category = "file"
    permission = ToolPermission.ASK  # Ask before editing multiple files

    parameters = [
        ToolParameter(
            name="edits",
            description=(
                "List of edits to perform. Each edit should be a dict with: "
                "'file_path', 'old_string', 'new_string', and optional 'replace_all' (default false). "
                "Example: [{'file_path': 'a.py', 'old_string': 'foo', 'new_string': 'bar'}]"
            ),
            type="array",
            required=True,
        ),
    ]

    def execute(self, edits: list) -> ToolResult:
        """Execute multiple file edits atomically"""
        if not edits:
            return ToolResult(
                success=False,
                output="",
                error="No edits provided",
                target="MultiEdit",
            )

        # Validate all edits first
        validated_edits = []
        errors = []

        for i, edit in enumerate(edits):
            # Validate required fields
            if not isinstance(edit, dict):
                errors.append(f"Edit {i+1}: Must be a dictionary")
                continue

            file_path = edit.get("file_path")
            old_string = edit.get("old_string")
            new_string = edit.get("new_string")
            replace_all = edit.get("replace_all", False)

            if not file_path:
                errors.append(f"Edit {i+1}: Missing 'file_path'")
                continue
            if old_string is None:
                errors.append(f"Edit {i+1}: Missing 'old_string'")
                continue
            if new_string is None:
                errors.append(f"Edit {i+1}: Missing 'new_string'")
                continue

            path = Path(file_path).expanduser()

            if not path.exists():
                errors.append(f"Edit {i+1}: File not found: {file_path}")
                continue

            # Read and validate content
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                if old_string not in content:
                    errors.append(f"Edit {i+1}: String not found in {file_path}")
                    continue

                count = content.count(old_string)
                if count > 1 and not replace_all:
                    errors.append(
                        f"Edit {i+1}: Found {count} occurrences in {file_path}. "
                        "Set 'replace_all': true or make old_string more specific."
                    )
                    continue

                validated_edits.append({
                    "path": path,
                    "file_path": file_path,
                    "old_string": old_string,
                    "new_string": new_string,
                    "replace_all": replace_all,
                    "content": content,
                    "count": count if replace_all else 1,
                })

            except Exception as e:
                errors.append(f"Edit {i+1}: Error reading {file_path}: {e}")
                continue

        # If any validation errors, abort
        if errors:
            return ToolResult(
                success=False,
                output="",
                error="Validation failed:\n" + "\n".join(errors),
                target="MultiEdit",
            )

        # Create checkpoints for all files
        if HAS_CHECKPOINTS:
            for edit in validated_edits:
                checkpoint_before_edit(str(edit["path"].absolute()))

        # Apply all edits
        results = []
        try:
            for edit in validated_edits:
                if edit["replace_all"]:
                    new_content = edit["content"].replace(
                        edit["old_string"], edit["new_string"]
                    )
                else:
                    new_content = edit["content"].replace(
                        edit["old_string"], edit["new_string"], 1
                    )

                with open(edit["path"], "w", encoding="utf-8") as f:
                    f.write(new_content)

                results.append(
                    f"✓ {edit['file_path']}: {edit['count']} replacement(s)"
                )

            output = f"Successfully edited {len(validated_edits)} file(s):\n" + "\n".join(results)

            return ToolResult(
                success=True,
                output=output,
                target=f"{len(validated_edits)} files",
                data={
                    "files_edited": len(validated_edits),
                    "edits": [
                        {
                            "file": e["file_path"],
                            "replacements": e["count"],
                        }
                        for e in validated_edits
                    ],
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error applying edits: {e}",
                target="MultiEdit",
            )


def _expand_brace_pattern(pattern: str) -> list[str]:
    """
    Expand brace patterns into individual patterns.

    Examples:
        '*.{js,ts}' -> ['*.js', '*.ts']
        '*{package.json,requirements.txt}' -> ['*package.json', '*requirements.txt']
        '**/*.{py,js,ts}' -> ['**/*.py', '**/*.js', '**/*.ts']

    Python's Path.glob() doesn't support brace expansion, so we handle it manually.
    """
    import re

    # Check if pattern contains braces
    if '{' not in pattern or '}' not in pattern:
        return [pattern]

    # Match the first brace group: {a,b,c}
    match = re.search(r'^(.*?)\{([^}]+)\}(.*)$', pattern)
    if not match:
        return [pattern]

    prefix, options, suffix = match.groups()
    expanded_options = [opt.strip() for opt in options.split(',')]

    # Recursively expand in case there are nested braces
    results = []
    for opt in expanded_options:
        expanded = _expand_brace_pattern(f"{prefix}{opt}{suffix}")
        results.extend(expanded)

    return results


class GlobTool(Tool):
    """Find files matching a pattern"""

    name = "Glob"
    description = (
        "Find files matching a glob pattern. "
        "Examples: '**/*.py' for all Python files, 'src/**/*.ts' for TypeScript in src/, "
        "'*.{js,ts}' for multiple extensions."
    )
    category = "search"
    permission = ToolPermission.AUTO  # Safe to auto-execute

    parameters = [
        ToolParameter(
            name="pattern",
            description="Glob pattern to match files (e.g., '**/*.py', 'src/*.ts')",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="path",
            description="Base directory to search in (defaults to current directory)",
            type="string",
            required=False,
            default=".",
        ),
    ]

    def execute(self, pattern: str, path: str = ".") -> ToolResult:
        """Find files matching pattern"""
        base_path = Path(path).expanduser()

        if not base_path.exists():
            return ToolResult(
                success=False,
                output="",
                error=f"Path not found: {path}",
                target=pattern,
            )

        try:
            # Expand brace patterns (e.g., '*.{js,ts}' -> ['*.js', '*.ts'])
            expanded_patterns = _expand_brace_pattern(pattern)

            # Find matching files across all expanded patterns
            matches = []
            seen = set()
            for p in expanded_patterns:
                for m in base_path.glob(p):
                    if m not in seen:
                        seen.add(m)
                        matches.append(m)

            # Filter out directories, sort by modification time
            files = [m for m in matches if m.is_file()]
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # Limit results
            max_results = 100
            truncated = len(files) > max_results
            files = files[:max_results]

            if not files:
                return ToolResult(
                    success=True,
                    output=f"No files found matching pattern: {pattern}",
                    target=pattern,
                    data={"count": 0, "files": []},
                )

            # Format output
            output_lines = [f"Found {len(files)} file(s) matching '{pattern}':"]
            file_paths = []
            for f in files:
                rel_path = f.relative_to(base_path) if f.is_relative_to(base_path) else f
                output_lines.append(f"  {rel_path}")
                file_paths.append(str(rel_path))

            if truncated:
                output_lines.append(f"\n  ... (truncated, showing first {max_results})")

            return ToolResult(
                success=True,
                output="\n".join(output_lines),
                target=pattern,
                data={"count": len(files), "files": file_paths},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error searching files: {e}",
                target=pattern,
            )


# Register tools
def register_file_tools(registry):
    """Register all file tools with a registry"""
    registry.register_class(ReadTool)
    registry.register_class(WriteTool)
    registry.register_class(EditTool)
    registry.register_class(MultiEditTool)
    registry.register_class(GlobTool)
