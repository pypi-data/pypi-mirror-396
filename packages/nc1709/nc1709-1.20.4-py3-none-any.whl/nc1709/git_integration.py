"""
Git Integration for NC1709

Provides automatic git commits and git-related utilities.
Similar to Aider's git integration.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GitStatus:
    """Status of a git repository"""
    is_repo: bool
    branch: str
    has_changes: bool
    staged_files: List[str]
    modified_files: List[str]
    untracked_files: List[str]


class GitIntegration:
    """
    Git integration for automatic commits and git operations.

    Features:
    - Automatic commits after file changes
    - Smart commit message generation
    - Git status and diff display
    """

    def __init__(self, repo_path: Optional[str] = None, auto_commit: bool = True):
        """
        Initialize git integration.

        Args:
            repo_path: Path to git repository (defaults to cwd)
            auto_commit: Whether to auto-commit changes
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.auto_commit = auto_commit
        self._is_repo = self._check_git_repo()

    def _check_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @property
    def is_repo(self) -> bool:
        """Check if we're in a git repository"""
        return self._is_repo

    def _run_git(self, *args, check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command"""
        return subprocess.run(
            ["git"] + list(args),
            cwd=str(self.repo_path),
            capture_output=True,
            text=True,
            check=check
        )

    def get_status(self) -> GitStatus:
        """Get current git status"""
        if not self._is_repo:
            return GitStatus(
                is_repo=False,
                branch="",
                has_changes=False,
                staged_files=[],
                modified_files=[],
                untracked_files=[]
            )

        # Get branch name
        try:
            result = self._run_git("branch", "--show-current")
            branch = result.stdout.strip()
        except subprocess.CalledProcessError:
            branch = "unknown"

        # Get status --porcelain
        result = self._run_git("status", "--porcelain", check=False)
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

        staged_files = []
        modified_files = []
        untracked_files = []

        for line in lines:
            if len(line) < 3:
                continue
            index_status = line[0]
            worktree_status = line[1]
            filename = line[3:]

            if index_status in "MADRC":
                staged_files.append(filename)
            if worktree_status == "M":
                modified_files.append(filename)
            if index_status == "?" and worktree_status == "?":
                untracked_files.append(filename)

        return GitStatus(
            is_repo=True,
            branch=branch,
            has_changes=bool(staged_files or modified_files or untracked_files),
            staged_files=staged_files,
            modified_files=modified_files,
            untracked_files=untracked_files
        )

    def get_diff(self, staged: bool = False) -> str:
        """Get git diff"""
        if not self._is_repo:
            return ""

        args = ["diff"]
        if staged:
            args.append("--staged")

        result = self._run_git(*args, check=False)
        return result.stdout

    def stage_file(self, file_path: str) -> bool:
        """Stage a file for commit"""
        if not self._is_repo:
            return False

        try:
            self._run_git("add", file_path)
            return True
        except subprocess.CalledProcessError:
            return False

    def stage_all(self) -> bool:
        """Stage all changes"""
        if not self._is_repo:
            return False

        try:
            self._run_git("add", "-A")
            return True
        except subprocess.CalledProcessError:
            return False

    def commit(self, message: str, files: Optional[List[str]] = None) -> bool:
        """
        Create a commit.

        Args:
            message: Commit message
            files: Specific files to commit (stages them first)

        Returns:
            True if commit was successful
        """
        if not self._is_repo:
            return False

        try:
            # Stage specific files if provided
            if files:
                for f in files:
                    self.stage_file(f)

            # Check if there's anything to commit
            status = self.get_status()
            if not status.staged_files:
                return False

            # Create commit
            self._run_git("commit", "-m", message)
            return True

        except subprocess.CalledProcessError:
            return False

    def auto_commit_files(
        self,
        files: List[str],
        tool_name: str = "NC1709",
        description: str = ""
    ) -> Optional[str]:
        """
        Automatically commit changed files with a generated message.

        Args:
            files: List of file paths that were modified
            tool_name: Name of the tool that made the change
            description: Optional description of what changed

        Returns:
            Commit hash if successful, None otherwise
        """
        if not self._is_repo or not self.auto_commit:
            return None

        # Filter to files that actually have changes
        changed_files = []
        for f in files:
            result = self._run_git("status", "--porcelain", f, check=False)
            if result.stdout.strip():
                changed_files.append(f)

        if not changed_files:
            return None

        # Generate commit message
        file_names = [Path(f).name for f in changed_files]
        if len(file_names) == 1:
            file_desc = file_names[0]
        elif len(file_names) <= 3:
            file_desc = ", ".join(file_names)
        else:
            file_desc = f"{file_names[0]} and {len(file_names) - 1} other files"

        if description:
            message = f"{description}\n\nModified: {file_desc}\n\n[{tool_name}]"
        else:
            message = f"Update {file_desc}\n\n[{tool_name}]"

        # Stage and commit
        for f in changed_files:
            self.stage_file(f)

        try:
            self._run_git("commit", "-m", message)

            # Get the commit hash
            result = self._run_git("rev-parse", "--short", "HEAD")
            return result.stdout.strip()

        except subprocess.CalledProcessError:
            return None

    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commit history"""
        if not self._is_repo:
            return []

        try:
            result = self._run_git(
                "log",
                f"-{limit}",
                "--pretty=format:%h|%s|%an|%ar",
                check=False
            )

            commits = []
            for line in result.stdout.strip().split("\n"):
                if "|" in line:
                    parts = line.split("|", 3)
                    if len(parts) >= 4:
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1],
                            "author": parts[2],
                            "time_ago": parts[3]
                        })

            return commits

        except subprocess.CalledProcessError:
            return []

    def init_repo(self) -> bool:
        """Initialize a new git repository"""
        try:
            self._run_git("init")
            self._is_repo = True
            return True
        except subprocess.CalledProcessError:
            return False


# Global git integration instance
_git_integration: Optional[GitIntegration] = None


def get_git_integration(auto_commit: bool = True) -> GitIntegration:
    """Get or create the global git integration"""
    global _git_integration
    if _git_integration is None:
        _git_integration = GitIntegration(auto_commit=auto_commit)
    return _git_integration


def auto_commit_after_edit(file_path: str, tool_name: str = "Edit") -> Optional[str]:
    """Convenience function to auto-commit after editing a file"""
    git = get_git_integration()
    if git.is_repo and git.auto_commit:
        return git.auto_commit_files([file_path], tool_name=tool_name)
    return None
