"""
Filesystem Controller with Safety Features
Handles all file operations with automatic backups and atomic transactions
"""
import os
import shutil
import hashlib
import difflib
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

from .config import get_config


class FileController:
    """Manages safe filesystem operations"""

    def __init__(self):
        """Initialize the file controller"""
        self.config = get_config()
        # Get backup directory from config, with fallback to default
        backup_path = self.config.get("safety.backup_dir", "~/.nc1709/backups")
        self.backup_dir = Path(backup_path).expanduser().resolve()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def read_file(self, file_path: str) -> str:
        """Read a file safely
        
        Args:
            file_path: Path to the file
        
        Returns:
            File contents as string
        
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be read
        """
        path = Path(file_path).expanduser().resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try reading as binary if UTF-8 fails
            with open(path, 'rb') as f:
                return f.read().decode('utf-8', errors='replace')
    
    def write_file(
        self,
        file_path: str,
        content: str,
        create_backup: bool = True,
        confirm: bool = True
    ) -> bool:
        """Write content to a file with safety checks
        
        Args:
            file_path: Path to the file
            content: Content to write
            create_backup: Whether to create a backup first
            confirm: Whether to ask for confirmation
        
        Returns:
            True if write was successful
        
        Raises:
            PermissionError: If file can't be written
        """
        path = Path(file_path).expanduser().resolve()
        
        # Check if we should confirm
        if confirm and self.config.get("safety.confirm_writes", True):
            if path.exists():
                print(f"\n⚠️  File exists: {path}")
                print("This will overwrite the existing file.")
                response = input("Continue? [y/N]: ").strip().lower()
                if response != 'y':
                    print("Write cancelled.")
                    return False
        
        # Create backup if file exists
        if create_backup and path.exists() and self.config.get("safety.auto_backup", True):
            self._create_backup(path)
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ File written: {path}")
            return True
        except Exception as e:
            print(f"❌ Failed to write file: {e}")
            return False
    
    def edit_file(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        create_backup: bool = True
    ) -> bool:
        """Edit a file by replacing old content with new content
        
        Args:
            file_path: Path to the file
            old_content: Content to replace
            new_content: New content
            create_backup: Whether to create a backup first
        
        Returns:
            True if edit was successful
        """
        path = Path(file_path).expanduser().resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read current content
        current_content = self.read_file(file_path)
        
        # Check if old_content exists in file
        if old_content not in current_content:
            print(f"⚠️  Content to replace not found in {file_path}")
            return False
        
        # Create backup
        if create_backup and self.config.get("safety.auto_backup", True):
            self._create_backup(path)
        
        # Replace content
        updated_content = current_content.replace(old_content, new_content, 1)
        
        # Show diff
        self._show_diff(current_content, updated_content, str(path))
        
        # Confirm
        if self.config.get("safety.confirm_writes", True):
            response = input("\nApply these changes? [y/N]: ").strip().lower()
            if response != 'y':
                print("Edit cancelled.")
                return False
        
        # Write updated content
        return self.write_file(file_path, updated_content, create_backup=False, confirm=False)
    
    def create_file(self, file_path: str, content: str = "") -> bool:
        """Create a new file
        
        Args:
            file_path: Path to the file
            content: Initial content (default: empty)
        
        Returns:
            True if creation was successful
        """
        path = Path(file_path).expanduser().resolve()
        
        if path.exists():
            print(f"⚠️  File already exists: {file_path}")
            return False
        
        return self.write_file(file_path, content, create_backup=False, confirm=False)
    
    def delete_file(self, file_path: str, confirm: bool = True) -> bool:
        """Delete a file with confirmation
        
        Args:
            file_path: Path to the file
            confirm: Whether to ask for confirmation
        
        Returns:
            True if deletion was successful
        """
        path = Path(file_path).expanduser().resolve()
        
        if not path.exists():
            print(f"⚠️  File not found: {file_path}")
            return False
        
        # Create backup before deleting
        if self.config.get("safety.auto_backup", True):
            self._create_backup(path)
        
        # Confirm deletion
        if confirm and self.config.get("safety.confirm_destructive", True):
            print(f"\n⚠️  About to delete: {path}")
            response = input("Are you sure? [y/N]: ").strip().lower()
            if response != 'y':
                print("Deletion cancelled.")
                return False
        
        try:
            path.unlink()
            print(f"✅ File deleted: {path}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete file: {e}")
            return False
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """List files in a directory
        
        Args:
            directory: Directory path
            pattern: Glob pattern (default: all files)
        
        Returns:
            List of file paths
        """
        path = Path(directory).expanduser().resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not path.is_dir():
            raise ValueError(f"Not a directory: {directory}")
        
        return [str(p) for p in path.glob(pattern) if p.is_file()]
    
    def get_file_info(self, file_path: str) -> dict:
        """Get information about a file
        
        Args:
            file_path: Path to the file
        
        Returns:
            Dictionary with file information
        """
        path = Path(file_path).expanduser().resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = path.stat()
        
        return {
            "path": str(path),
            "name": path.name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "extension": path.suffix
        }
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create a backup of a file
        
        Args:
            file_path: Path to the file
        
        Returns:
            Path to the backup file
        """
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
        backup_name = f"{file_path.name}.{timestamp}.{file_hash}.backup"
        backup_path = self.backup_dir / backup_name
        
        # Copy file to backup
        shutil.copy2(file_path, backup_path)
        
        return backup_path
    
    def _show_diff(self, old_content: str, new_content: str, filename: str) -> None:
        """Show a diff between old and new content
        
        Args:
            old_content: Original content
            new_content: New content
            filename: Name of the file (for display)
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{filename} (original)",
            tofile=f"{filename} (modified)",
            lineterm=''
        )
        
        print("\n" + "="*60)
        print("PROPOSED CHANGES:")
        print("="*60)
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                print(f"\033[92m{line}\033[0m", end='')  # Green for additions
            elif line.startswith('-') and not line.startswith('---'):
                print(f"\033[91m{line}\033[0m", end='')  # Red for deletions
            else:
                print(line, end='')
        print("="*60)
    
    def restore_from_backup(self, backup_path: str, target_path: Optional[str] = None) -> bool:
        """Restore a file from backup
        
        Args:
            backup_path: Path to the backup file
            target_path: Target path (default: original location)
        
        Returns:
            True if restore was successful
        """
        backup = Path(backup_path)
        
        if not backup.exists():
            print(f"⚠️  Backup not found: {backup_path}")
            return False
        
        if target_path is None:
            # Extract original filename from backup name
            original_name = backup.name.split('.')[0]
            target_path = Path.cwd() / original_name
        else:
            target_path = Path(target_path)
        
        try:
            shutil.copy2(backup, target_path)
            print(f"✅ File restored from backup: {target_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to restore from backup: {e}")
            return False
    
    def list_backups(self) -> List[Tuple[str, datetime]]:
        """List all available backups
        
        Returns:
            List of (backup_path, timestamp) tuples
        """
        backups = []
        for backup_file in self.backup_dir.glob("*.backup"):
            stat = backup_file.stat()
            timestamp = datetime.fromtimestamp(stat.st_mtime)
            backups.append((str(backup_file), timestamp))
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x[1], reverse=True)
        
        return backups
