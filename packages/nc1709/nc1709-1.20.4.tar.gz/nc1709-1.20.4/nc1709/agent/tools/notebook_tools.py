"""
Jupyter Notebook Tools

Tools for working with Jupyter notebooks (.ipynb files):
- NotebookRead: Read notebook contents with cells and outputs
- NotebookEdit: Edit, insert, or delete notebook cells
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from .base import Tool, ToolResult, ToolParameter, ToolPermission


class NotebookReadTool(Tool):
    """Read contents of a Jupyter notebook"""

    name = "NotebookRead"
    description = (
        "Read the contents of a Jupyter notebook (.ipynb file). "
        "Returns all cells with their types (code/markdown), source, and outputs."
    )
    category = "notebook"
    permission = ToolPermission.AUTO  # Safe to auto-execute

    parameters = [
        ToolParameter(
            name="notebook_path",
            description="The absolute path to the Jupyter notebook file",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="cell_numbers",
            description="Optional list of specific cell numbers to read (0-indexed). If not provided, reads all cells.",
            type="array",
            required=False,
            default=None,
        ),
        ToolParameter(
            name="include_outputs",
            description="Whether to include cell outputs in the result (default: true)",
            type="boolean",
            required=False,
            default=True,
        ),
    ]

    def execute(
        self,
        notebook_path: str,
        cell_numbers: List[int] = None,
        include_outputs: bool = True,
    ) -> ToolResult:
        """Read notebook contents"""
        path = Path(notebook_path).expanduser()

        # Check if file exists
        if not path.exists():
            return ToolResult(
                success=False,
                output="",
                error=f"Notebook not found: {notebook_path}",
                target=notebook_path,
            )

        # Check file extension
        if path.suffix.lower() != ".ipynb":
            return ToolResult(
                success=False,
                output="",
                error=f"Not a Jupyter notebook file (expected .ipynb): {notebook_path}",
                target=notebook_path,
            )

        try:
            # Read and parse notebook
            with open(path, "r", encoding="utf-8") as f:
                notebook = json.load(f)

            cells = notebook.get("cells", [])
            total_cells = len(cells)

            # Filter to specific cells if requested
            if cell_numbers:
                selected_indices = [i for i in cell_numbers if 0 <= i < total_cells]
                if not selected_indices:
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"No valid cell numbers in range 0-{total_cells-1}",
                        target=notebook_path,
                    )
            else:
                selected_indices = list(range(total_cells))

            # Format output
            output_parts = [
                f"Notebook: {notebook_path}",
                f"Total cells: {total_cells}",
                f"Kernel: {notebook.get('metadata', {}).get('kernelspec', {}).get('display_name', 'Unknown')}",
                "=" * 60,
            ]

            for idx in selected_indices:
                cell = cells[idx]
                cell_type = cell.get("cell_type", "unknown")
                source = "".join(cell.get("source", []))
                cell_id = cell.get("id", f"cell_{idx}")

                output_parts.append(f"\n[Cell {idx}] ({cell_type}) id={cell_id}")
                output_parts.append("-" * 40)

                # Show source with line numbers
                for i, line in enumerate(source.split("\n"), 1):
                    output_parts.append(f"  {i:3}│ {line}")

                # Include outputs for code cells
                if include_outputs and cell_type == "code":
                    outputs = cell.get("outputs", [])
                    if outputs:
                        output_parts.append("\n  Output:")
                        for out in outputs[:5]:  # Limit outputs shown
                            out_type = out.get("output_type", "")
                            if out_type == "stream":
                                text = "".join(out.get("text", []))[:500]
                                output_parts.append(f"    [stream] {text}")
                            elif out_type == "execute_result":
                                data = out.get("data", {})
                                if "text/plain" in data:
                                    text = "".join(data["text/plain"])[:500]
                                    output_parts.append(f"    [result] {text}")
                            elif out_type == "error":
                                ename = out.get("ename", "Error")
                                evalue = out.get("evalue", "")[:200]
                                output_parts.append(f"    [error] {ename}: {evalue}")
                            elif out_type == "display_data":
                                data_types = list(out.get("data", {}).keys())
                                output_parts.append(f"    [display] types: {', '.join(data_types)}")

            return ToolResult(
                success=True,
                output="\n".join(output_parts),
                target=notebook_path,
                data={
                    "total_cells": total_cells,
                    "cells_shown": len(selected_indices),
                    "kernel": notebook.get("metadata", {}).get("kernelspec", {}).get("name"),
                },
            )

        except json.JSONDecodeError as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Invalid notebook JSON: {e}",
                target=notebook_path,
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error reading notebook: {e}",
                target=notebook_path,
            )


class NotebookEditTool(Tool):
    """Edit a cell in a Jupyter notebook"""

    name = "NotebookEdit"
    description = (
        "Edit, insert, or delete a cell in a Jupyter notebook. "
        "Use edit_mode='replace' to update a cell, 'insert' to add a new cell, "
        "or 'delete' to remove a cell."
    )
    category = "notebook"
    permission = ToolPermission.ASK  # Ask before modifying notebooks

    parameters = [
        ToolParameter(
            name="notebook_path",
            description="The absolute path to the Jupyter notebook file",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="cell_number",
            description="The cell number to edit (0-indexed). For insert, new cell is added after this position.",
            type="integer",
            required=True,
        ),
        ToolParameter(
            name="new_source",
            description="The new source code/content for the cell",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="cell_type",
            description="Cell type: 'code' or 'markdown'. Required for insert, optional for replace.",
            type="string",
            required=False,
            default=None,
        ),
        ToolParameter(
            name="edit_mode",
            description="Edit mode: 'replace' (update cell), 'insert' (add new cell), 'delete' (remove cell)",
            type="string",
            required=False,
            default="replace",
        ),
    ]

    def execute(
        self,
        notebook_path: str,
        cell_number: int,
        new_source: str,
        cell_type: str = None,
        edit_mode: str = "replace",
    ) -> ToolResult:
        """Edit notebook cell"""
        path = Path(notebook_path).expanduser()

        # Validate edit_mode
        if edit_mode not in ["replace", "insert", "delete"]:
            return ToolResult(
                success=False,
                output="",
                error=f"Invalid edit_mode: {edit_mode}. Use 'replace', 'insert', or 'delete'.",
                target=notebook_path,
            )

        # Check if file exists
        if not path.exists():
            return ToolResult(
                success=False,
                output="",
                error=f"Notebook not found: {notebook_path}",
                target=notebook_path,
            )

        try:
            # Read notebook
            with open(path, "r", encoding="utf-8") as f:
                notebook = json.load(f)

            cells = notebook.get("cells", [])
            total_cells = len(cells)

            # Validate cell number
            if edit_mode == "insert":
                # For insert, -1 means at the beginning, cell_number means after that cell
                if cell_number < -1 or cell_number >= total_cells:
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"Invalid cell number for insert: {cell_number}. Use -1 to {total_cells-1}.",
                        target=notebook_path,
                    )
            else:
                if cell_number < 0 or cell_number >= total_cells:
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"Cell number {cell_number} out of range. Notebook has {total_cells} cells (0-{total_cells-1}).",
                        target=notebook_path,
                    )

            # Perform the edit
            if edit_mode == "delete":
                deleted_cell = cells.pop(cell_number)
                action_msg = f"Deleted cell {cell_number} ({deleted_cell.get('cell_type', 'unknown')})"

            elif edit_mode == "insert":
                # Determine cell type
                if not cell_type:
                    cell_type = "code"  # Default to code cell
                if cell_type not in ["code", "markdown"]:
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"Invalid cell_type: {cell_type}. Use 'code' or 'markdown'.",
                        target=notebook_path,
                    )

                # Create new cell
                new_cell = self._create_cell(cell_type, new_source)
                insert_pos = cell_number + 1  # Insert after the specified cell
                cells.insert(insert_pos, new_cell)
                action_msg = f"Inserted new {cell_type} cell at position {insert_pos}"

            else:  # replace
                old_cell = cells[cell_number]
                old_source = "".join(old_cell.get("source", []))

                # Update cell type if specified
                if cell_type and cell_type in ["code", "markdown"]:
                    old_cell["cell_type"] = cell_type

                # Update source
                old_cell["source"] = new_source.split("\n")
                # Add newlines except for last line
                old_cell["source"] = [
                    line + "\n" if i < len(old_cell["source"]) - 1 else line
                    for i, line in enumerate(old_cell["source"])
                ]

                # Clear outputs for code cells
                if old_cell.get("cell_type") == "code":
                    old_cell["outputs"] = []
                    old_cell["execution_count"] = None

                action_msg = f"Replaced cell {cell_number} ({old_cell.get('cell_type', 'unknown')})"

            # Write back
            with open(path, "w", encoding="utf-8") as f:
                json.dump(notebook, f, indent=1)

            return ToolResult(
                success=True,
                output=f"{action_msg}\nNotebook saved: {notebook_path}",
                target=f"{notebook_path}:cell_{cell_number}",
                data={
                    "action": edit_mode,
                    "cell_number": cell_number,
                    "total_cells": len(cells),
                },
            )

        except json.JSONDecodeError as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Invalid notebook JSON: {e}",
                target=notebook_path,
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error editing notebook: {e}",
                target=notebook_path,
            )

    def _create_cell(self, cell_type: str, source: str) -> Dict[str, Any]:
        """Create a new notebook cell"""
        import uuid

        source_lines = source.split("\n")
        # Add newlines except for last line
        source_lines = [
            line + "\n" if i < len(source_lines) - 1 else line
            for i, line in enumerate(source_lines)
        ]

        cell = {
            "cell_type": cell_type,
            "id": str(uuid.uuid4())[:8],
            "metadata": {},
            "source": source_lines,
        }

        if cell_type == "code":
            cell["execution_count"] = None
            cell["outputs"] = []

        return cell


class NotebookRunTool(Tool):
    """Execute a notebook cell (requires jupyter kernel)"""

    name = "NotebookRun"
    description = (
        "Execute a specific cell in a Jupyter notebook. "
        "Requires nbconvert and a kernel to be available. "
        "Returns the output of the execution."
    )
    category = "notebook"
    permission = ToolPermission.ASK  # Ask before executing code

    parameters = [
        ToolParameter(
            name="notebook_path",
            description="The absolute path to the Jupyter notebook file",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="cell_number",
            description="The cell number to execute (0-indexed)",
            type="integer",
            required=True,
        ),
        ToolParameter(
            name="timeout",
            description="Execution timeout in seconds (default: 60)",
            type="integer",
            required=False,
            default=60,
        ),
    ]

    def execute(
        self,
        notebook_path: str,
        cell_number: int,
        timeout: int = 60,
    ) -> ToolResult:
        """Execute notebook cell"""
        try:
            import nbformat
            from nbconvert.preprocessors import ExecutePreprocessor
        except ImportError:
            return ToolResult(
                success=False,
                output="",
                error="nbconvert not installed. Install with: pip install nbconvert",
                target=notebook_path,
            )

        path = Path(notebook_path).expanduser()

        if not path.exists():
            return ToolResult(
                success=False,
                output="",
                error=f"Notebook not found: {notebook_path}",
                target=notebook_path,
            )

        try:
            # Read notebook
            with open(path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)

            cells = nb.get("cells", [])
            if cell_number < 0 or cell_number >= len(cells):
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Cell number {cell_number} out of range",
                    target=notebook_path,
                )

            cell = cells[cell_number]
            if cell.get("cell_type") != "code":
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Cell {cell_number} is not a code cell",
                    target=notebook_path,
                )

            # Create a mini-notebook with just this cell
            mini_nb = nbformat.v4.new_notebook()
            mini_nb.cells = [cell]

            # Execute
            ep = ExecutePreprocessor(timeout=timeout, kernel_name='python3')
            ep.preprocess(mini_nb, {'metadata': {'path': str(path.parent)}})

            # Get outputs
            executed_cell = mini_nb.cells[0]
            outputs = executed_cell.get("outputs", [])

            # Format outputs
            output_parts = [f"Executed cell {cell_number}:"]
            for out in outputs:
                out_type = out.get("output_type", "")
                if out_type == "stream":
                    text = "".join(out.get("text", []))
                    output_parts.append(f"[stream] {text}")
                elif out_type == "execute_result":
                    data = out.get("data", {})
                    if "text/plain" in data:
                        text = "".join(data["text/plain"])
                        output_parts.append(f"[result] {text}")
                elif out_type == "error":
                    ename = out.get("ename", "Error")
                    evalue = out.get("evalue", "")
                    output_parts.append(f"[error] {ename}: {evalue}")

            # Update the original notebook's cell
            cells[cell_number] = executed_cell
            with open(path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)

            return ToolResult(
                success=True,
                output="\n".join(output_parts),
                target=f"{notebook_path}:cell_{cell_number}",
                data={
                    "cell_number": cell_number,
                    "execution_count": executed_cell.get("execution_count"),
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error executing cell: {e}",
                target=notebook_path,
            )


# Register tools
def register_notebook_tools(registry):
    """Register all notebook tools with a registry"""
    registry.register_class(NotebookReadTool)
    registry.register_class(NotebookEditTool)
    registry.register_class(NotebookRunTool)
