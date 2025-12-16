"""
Checkpoints System for NC1709

Saves file states before each change, allowing users to rewind to previous versions.
Similar to Claude Code's checkpoint system.
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class FileSnapshot:
    """Snapshot of a single file"""
    path: str
    content: str
    hash: str
    exists: bool

    @classmethod
    def from_file(cls, path: str) -> "FileSnapshot":
        """Create a snapshot from an existing file"""
        path_obj = Path(path)
        if path_obj.exists():
            try:
                content = path_obj.read_text(encoding='utf-8')
                file_hash = hashlib.md5(content.encode()).hexdigest()
                return cls(path=str(path_obj.absolute()), content=content, hash=file_hash, exists=True)
            except (UnicodeDecodeError, IOError):
                # Binary file or read error - store empty
                return cls(path=str(path_obj.absolute()), content="", hash="", exists=True)
        else:
            return cls(path=str(path_obj.absolute()), content="", hash="", exists=False)


@dataclass
class Checkpoint:
    """A checkpoint containing multiple file snapshots"""
    id: str
    timestamp: str
    description: str
    tool_name: str
    files: Dict[str, FileSnapshot]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "description": self.description,
            "tool_name": self.tool_name,
            "files": {
                path: asdict(snapshot)
                for path, snapshot in self.files.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        """Create from dictionary"""
        files = {
            path: FileSnapshot(**snapshot_data)
            for path, snapshot_data in data.get("files", {}).items()
        }
        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            description=data["description"],
            tool_name=data.get("tool_name", "unknown"),
            files=files
        )


class CheckpointManager:
    """
    Manages checkpoints for file operations.

    Creates a checkpoint before each file modification, allowing
    users to rewind to any previous state.
    """

    def __init__(self, storage_dir: Optional[str] = None, max_checkpoints: int = 50):
        """
        Initialize the checkpoint manager.

        Args:
            storage_dir: Directory to store checkpoint data.
                        Defaults to ~/.nc1709/checkpoints/
            max_checkpoints: Maximum number of checkpoints to keep
        """
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".nc1709" / "checkpoints"

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.max_checkpoints = max_checkpoints
        self.checkpoints: List[Checkpoint] = []
        self.current_index: int = -1  # Points to current checkpoint

        # Load existing checkpoints for current session
        self._session_file = self.storage_dir / "current_session.json"
        self._load_session()

    def _load_session(self) -> None:
        """Load checkpoints from current session file"""
        if self._session_file.exists():
            try:
                data = json.loads(self._session_file.read_text())
                self.checkpoints = [
                    Checkpoint.from_dict(cp) for cp in data.get("checkpoints", [])
                ]
                self.current_index = data.get("current_index", len(self.checkpoints) - 1)
            except (json.JSONDecodeError, KeyError):
                self.checkpoints = []
                self.current_index = -1

    def _save_session(self) -> None:
        """Save checkpoints to session file"""
        data = {
            "checkpoints": [cp.to_dict() for cp in self.checkpoints],
            "current_index": self.current_index
        }
        self._session_file.write_text(json.dumps(data, indent=2))

    def _generate_id(self) -> str:
        """Generate a unique checkpoint ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"cp_{timestamp}"

    def create_checkpoint(
        self,
        files: List[str],
        tool_name: str = "unknown",
        description: str = ""
    ) -> Checkpoint:
        """
        Create a checkpoint before modifying files.

        Args:
            files: List of file paths that will be modified
            tool_name: Name of the tool making the modification
            description: Human-readable description of the change

        Returns:
            The created Checkpoint
        """
        # Snapshot all files
        file_snapshots = {}
        for file_path in files:
            snapshot = FileSnapshot.from_file(file_path)
            file_snapshots[snapshot.path] = snapshot

        # Create checkpoint
        checkpoint = Checkpoint(
            id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            description=description or f"{tool_name} operation",
            tool_name=tool_name,
            files=file_snapshots
        )

        # If we're not at the end (user rewound), truncate future checkpoints
        if self.current_index < len(self.checkpoints) - 1:
            self.checkpoints = self.checkpoints[:self.current_index + 1]

        # Add checkpoint
        self.checkpoints.append(checkpoint)
        self.current_index = len(self.checkpoints) - 1

        # Prune old checkpoints if needed
        if len(self.checkpoints) > self.max_checkpoints:
            self.checkpoints = self.checkpoints[-self.max_checkpoints:]
            self.current_index = len(self.checkpoints) - 1

        self._save_session()
        return checkpoint

    def rewind(self, steps: int = 1) -> Optional[Checkpoint]:
        """
        Rewind to a previous checkpoint.

        Args:
            steps: Number of checkpoints to go back (default: 1)

        Returns:
            The checkpoint that was restored, or None if can't rewind
        """
        target_index = self.current_index - steps

        if target_index < 0:
            return None

        return self.restore_to_index(target_index)

    def restore_to_index(self, index: int) -> Optional[Checkpoint]:
        """
        Restore files to state at specific checkpoint index.

        Args:
            index: Checkpoint index to restore

        Returns:
            The checkpoint that was restored, or None if invalid
        """
        if index < 0 or index >= len(self.checkpoints):
            return None

        checkpoint = self.checkpoints[index]

        # Restore all files
        for path, snapshot in checkpoint.files.items():
            self._restore_file(snapshot)

        self.current_index = index
        self._save_session()

        return checkpoint

    def restore_to_id(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Restore files to state at specific checkpoint ID.

        Args:
            checkpoint_id: ID of checkpoint to restore

        Returns:
            The checkpoint that was restored, or None if not found
        """
        for i, cp in enumerate(self.checkpoints):
            if cp.id == checkpoint_id:
                return self.restore_to_index(i)
        return None

    def _restore_file(self, snapshot: FileSnapshot) -> None:
        """Restore a single file from snapshot"""
        path = Path(snapshot.path)

        if not snapshot.exists:
            # File didn't exist at checkpoint - delete it
            if path.exists():
                path.unlink()
        else:
            # Restore file content
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(snapshot.content, encoding='utf-8')

    def list_checkpoints(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent checkpoints.

        Args:
            limit: Maximum number to return

        Returns:
            List of checkpoint summaries
        """
        result = []
        start = max(0, len(self.checkpoints) - limit)

        for i in range(start, len(self.checkpoints)):
            cp = self.checkpoints[i]
            result.append({
                "index": i,
                "id": cp.id,
                "timestamp": cp.timestamp,
                "description": cp.description,
                "tool": cp.tool_name,
                "files": list(cp.files.keys()),
                "is_current": i == self.current_index
            })

        return result

    def get_current_checkpoint(self) -> Optional[Checkpoint]:
        """Get the current checkpoint"""
        if 0 <= self.current_index < len(self.checkpoints):
            return self.checkpoints[self.current_index]
        return None

    def can_rewind(self) -> bool:
        """Check if we can rewind"""
        return self.current_index > 0

    def can_forward(self) -> bool:
        """Check if we can go forward (after rewinding)"""
        return self.current_index < len(self.checkpoints) - 1

    def forward(self, steps: int = 1) -> Optional[Checkpoint]:
        """
        Go forward after rewinding.

        Args:
            steps: Number of checkpoints to go forward

        Returns:
            The checkpoint that was restored
        """
        target_index = self.current_index + steps

        if target_index >= len(self.checkpoints):
            target_index = len(self.checkpoints) - 1

        return self.restore_to_index(target_index)

    def clear_session(self) -> None:
        """Clear all checkpoints for current session"""
        self.checkpoints = []
        self.current_index = -1
        if self._session_file.exists():
            self._session_file.unlink()

    def get_diff(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Get diff between current state and a checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to compare with

        Returns:
            Dictionary with file changes
        """
        for cp in self.checkpoints:
            if cp.id == checkpoint_id:
                changes = {}
                for path, snapshot in cp.files.items():
                    current = FileSnapshot.from_file(path)
                    if current.hash != snapshot.hash:
                        changes[path] = {
                            "had_content": snapshot.exists,
                            "has_content": current.exists,
                            "changed": True
                        }
                return {"checkpoint": checkpoint_id, "changes": changes}

        return {"error": "Checkpoint not found"}


# Global checkpoint manager instance
_checkpoint_manager: Optional[CheckpointManager] = None


def get_checkpoint_manager() -> CheckpointManager:
    """Get or create the global checkpoint manager"""
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager


def checkpoint_before_edit(file_path: str, tool_name: str = "Edit") -> Checkpoint:
    """Convenience function to create checkpoint before editing a file"""
    return get_checkpoint_manager().create_checkpoint(
        files=[file_path],
        tool_name=tool_name,
        description=f"Before editing {Path(file_path).name}"
    )


def checkpoint_before_write(file_path: str, tool_name: str = "Write") -> Checkpoint:
    """Convenience function to create checkpoint before writing a file"""
    return get_checkpoint_manager().create_checkpoint(
        files=[file_path],
        tool_name=tool_name,
        description=f"Before writing {Path(file_path).name}"
    )
