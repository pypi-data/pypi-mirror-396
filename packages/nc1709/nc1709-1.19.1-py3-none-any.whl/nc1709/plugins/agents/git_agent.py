"""
Git Agent for NC1709
Handles Git operations: commits, branches, diffs, PRs, etc.
"""
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    from ..base import (
        Plugin, PluginMetadata, PluginCapability,
        ActionResult
    )
except ImportError:
    # When loaded dynamically via importlib
    from nc1709.plugins.base import (
        Plugin, PluginMetadata, PluginCapability,
        ActionResult
    )


@dataclass
class GitStatus:
    """Represents git repository status"""
    branch: str
    ahead: int = 0
    behind: int = 0
    staged: List[str] = None
    modified: List[str] = None
    untracked: List[str] = None
    conflicts: List[str] = None

    def __post_init__(self):
        self.staged = self.staged or []
        self.modified = self.modified or []
        self.untracked = self.untracked or []
        self.conflicts = self.conflicts or []

    @property
    def is_clean(self) -> bool:
        return not (self.staged or self.modified or self.untracked or self.conflicts)

    @property
    def has_changes(self) -> bool:
        return bool(self.staged or self.modified)


@dataclass
class CommitInfo:
    """Represents a git commit"""
    hash: str
    short_hash: str
    author: str
    email: str
    date: str
    message: str
    files_changed: int = 0


class GitAgent(Plugin):
    """
    Git operations agent.

    Provides safe, intelligent Git operations including:
    - Status checking and diff viewing
    - Committing with smart message generation
    - Branch management
    - Remote operations (push, pull, fetch)
    - History viewing and searching
    """

    METADATA = PluginMetadata(
        name="git",
        version="1.0.0",
        description="Git version control operations",
        author="NC1709 Team",
        capabilities=[
            PluginCapability.VERSION_CONTROL,
            PluginCapability.FILE_OPERATIONS
        ],
        keywords=[
            "git", "commit", "push", "pull", "branch", "merge",
            "diff", "status", "log", "history", "checkout", "stash",
            "rebase", "cherry-pick", "remote", "fetch", "clone"
        ],
        config_schema={
            "repo_path": {"type": "string", "default": "."},
            "auto_stage": {"type": "boolean", "default": False},
            "sign_commits": {"type": "boolean", "default": False},
            "default_remote": {"type": "string", "default": "origin"}
        }
    )

    @property
    def metadata(self) -> PluginMetadata:
        return self.METADATA

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._repo_path: Optional[Path] = None
        self._git_available = False

    def initialize(self) -> bool:
        """Initialize the Git agent"""
        # Check if git is available
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True
            )
            self._git_available = result.returncode == 0
        except FileNotFoundError:
            self._error = "Git is not installed"
            return False

        # Set repository path
        repo_path = self._config.get("repo_path", ".")
        self._repo_path = Path(repo_path).resolve()

        return True

    def cleanup(self) -> None:
        """Cleanup resources"""
        pass

    def _register_actions(self) -> None:
        """Register Git actions"""
        self.register_action(
            "status",
            self.get_status,
            "Get repository status",
            parameters={"detailed": {"type": "boolean", "default": False}}
        )

        self.register_action(
            "diff",
            self.get_diff,
            "Show changes",
            parameters={
                "staged": {"type": "boolean", "default": False},
                "file": {"type": "string", "optional": True}
            }
        )

        self.register_action(
            "commit",
            self.commit,
            "Create a commit",
            parameters={
                "message": {"type": "string", "required": True},
                "files": {"type": "array", "optional": True},
                "all": {"type": "boolean", "default": False}
            },
            requires_confirmation=True
        )

        self.register_action(
            "branch",
            self.manage_branch,
            "Branch operations",
            parameters={
                "action": {"type": "string", "enum": ["list", "create", "delete", "switch"]},
                "name": {"type": "string", "optional": True}
            }
        )

        self.register_action(
            "push",
            self.push,
            "Push to remote",
            parameters={
                "remote": {"type": "string", "default": "origin"},
                "branch": {"type": "string", "optional": True},
                "force": {"type": "boolean", "default": False}
            },
            requires_confirmation=True,
            dangerous=True
        )

        self.register_action(
            "pull",
            self.pull,
            "Pull from remote",
            parameters={
                "remote": {"type": "string", "default": "origin"},
                "branch": {"type": "string", "optional": True},
                "rebase": {"type": "boolean", "default": False}
            }
        )

        self.register_action(
            "log",
            self.get_log,
            "View commit history",
            parameters={
                "count": {"type": "integer", "default": 10},
                "oneline": {"type": "boolean", "default": False},
                "author": {"type": "string", "optional": True}
            }
        )

        self.register_action(
            "stash",
            self.manage_stash,
            "Stash operations",
            parameters={
                "action": {"type": "string", "enum": ["save", "pop", "list", "drop"]},
                "message": {"type": "string", "optional": True}
            }
        )

        self.register_action(
            "reset",
            self.reset,
            "Reset changes",
            parameters={
                "mode": {"type": "string", "enum": ["soft", "mixed", "hard"], "default": "mixed"},
                "target": {"type": "string", "default": "HEAD"}
            },
            requires_confirmation=True,
            dangerous=True
        )

    def _run_git(self, *args, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run a git command

        Args:
            *args: Git command arguments
            cwd: Working directory

        Returns:
            CompletedProcess result
        """
        cmd = ["git"] + list(args)
        return subprocess.run(
            cmd,
            cwd=cwd or self._repo_path,
            capture_output=True,
            text=True
        )

    def is_git_repo(self, path: Optional[Path] = None) -> bool:
        """Check if path is a git repository"""
        result = self._run_git("rev-parse", "--git-dir", cwd=path)
        return result.returncode == 0

    def get_status(self, detailed: bool = False) -> ActionResult:
        """Get repository status

        Args:
            detailed: Include detailed file information

        Returns:
            ActionResult with GitStatus
        """
        if not self.is_git_repo():
            return ActionResult.fail("Not a git repository")

        # Get branch name
        result = self._run_git("branch", "--show-current")
        branch = result.stdout.strip() or "HEAD"

        # Get status
        result = self._run_git("status", "--porcelain", "-b")
        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        lines = result.stdout.strip().split("\n")

        status = GitStatus(branch=branch)

        # Parse ahead/behind from first line
        if lines and lines[0].startswith("##"):
            branch_line = lines[0]
            ahead_match = re.search(r"ahead (\d+)", branch_line)
            behind_match = re.search(r"behind (\d+)", branch_line)
            if ahead_match:
                status.ahead = int(ahead_match.group(1))
            if behind_match:
                status.behind = int(behind_match.group(1))
            lines = lines[1:]

        # Parse file statuses
        for line in lines:
            if not line:
                continue

            index_status = line[0]
            worktree_status = line[1]
            filename = line[3:]

            if index_status == "U" or worktree_status == "U":
                status.conflicts.append(filename)
            elif index_status != " " and index_status != "?":
                status.staged.append(filename)

            if worktree_status == "M":
                status.modified.append(filename)
            elif worktree_status == "?":
                status.untracked.append(filename)

        # Build message
        msg_parts = [f"On branch {status.branch}"]

        if status.ahead:
            msg_parts.append(f"ahead by {status.ahead} commit(s)")
        if status.behind:
            msg_parts.append(f"behind by {status.behind} commit(s)")

        if status.is_clean:
            msg_parts.append("Working tree clean")
        else:
            if status.staged:
                msg_parts.append(f"{len(status.staged)} staged")
            if status.modified:
                msg_parts.append(f"{len(status.modified)} modified")
            if status.untracked:
                msg_parts.append(f"{len(status.untracked)} untracked")
            if status.conflicts:
                msg_parts.append(f"{len(status.conflicts)} conflicts")

        return ActionResult.ok(
            message=", ".join(msg_parts),
            data=status
        )

    def get_diff(
        self,
        staged: bool = False,
        file: Optional[str] = None
    ) -> ActionResult:
        """Get diff of changes

        Args:
            staged: Show staged changes only
            file: Specific file to diff

        Returns:
            ActionResult with diff content
        """
        args = ["diff"]

        if staged:
            args.append("--staged")

        if file:
            args.append("--")
            args.append(file)

        result = self._run_git(*args)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        diff = result.stdout

        if not diff:
            return ActionResult.ok("No changes", data="")

        # Count changes
        additions = diff.count("\n+") - diff.count("\n+++")
        deletions = diff.count("\n-") - diff.count("\n---")

        return ActionResult.ok(
            message=f"+{additions} -{deletions} lines",
            data=diff
        )

    def commit(
        self,
        message: str,
        files: Optional[List[str]] = None,
        all: bool = False
    ) -> ActionResult:
        """Create a commit

        Args:
            message: Commit message
            files: Specific files to commit
            all: Stage all changes (-a flag)

        Returns:
            ActionResult with commit info
        """
        if not message:
            return ActionResult.fail("Commit message required")

        # Stage files if specified
        if files:
            result = self._run_git("add", *files)
            if result.returncode != 0:
                return ActionResult.fail(f"Failed to stage files: {result.stderr}")

        # Build commit command
        args = ["commit"]

        if all:
            args.append("-a")

        if self._config.get("sign_commits"):
            args.append("-S")

        args.extend(["-m", message])

        result = self._run_git(*args)

        if result.returncode != 0:
            if "nothing to commit" in result.stdout:
                return ActionResult.ok("Nothing to commit", data=None)
            return ActionResult.fail(result.stderr or result.stdout)

        # Get commit hash
        hash_result = self._run_git("rev-parse", "--short", "HEAD")
        commit_hash = hash_result.stdout.strip()

        return ActionResult.ok(
            message=f"Created commit {commit_hash}",
            data={"hash": commit_hash, "message": message}
        )

    def manage_branch(
        self,
        action: str = "list",
        name: Optional[str] = None
    ) -> ActionResult:
        """Branch management operations

        Args:
            action: Operation (list, create, delete, switch)
            name: Branch name for create/delete/switch

        Returns:
            ActionResult
        """
        if action == "list":
            result = self._run_git("branch", "-a", "-v")
            if result.returncode != 0:
                return ActionResult.fail(result.stderr)

            branches = []
            current = None
            for line in result.stdout.strip().split("\n"):
                if line.startswith("*"):
                    current = line[2:].split()[0]
                    branches.append(line[2:].strip())
                else:
                    branches.append(line.strip())

            return ActionResult.ok(
                message=f"Current: {current}, {len(branches)} branches",
                data={"current": current, "branches": branches}
            )

        elif action == "create":
            if not name:
                return ActionResult.fail("Branch name required")

            result = self._run_git("checkout", "-b", name)
            if result.returncode != 0:
                return ActionResult.fail(result.stderr)

            return ActionResult.ok(f"Created and switched to branch '{name}'")

        elif action == "delete":
            if not name:
                return ActionResult.fail("Branch name required")

            result = self._run_git("branch", "-d", name)
            if result.returncode != 0:
                return ActionResult.fail(result.stderr)

            return ActionResult.ok(f"Deleted branch '{name}'")

        elif action == "switch":
            if not name:
                return ActionResult.fail("Branch name required")

            result = self._run_git("checkout", name)
            if result.returncode != 0:
                return ActionResult.fail(result.stderr)

            return ActionResult.ok(f"Switched to branch '{name}'")

        return ActionResult.fail(f"Unknown action: {action}")

    def push(
        self,
        remote: str = "origin",
        branch: Optional[str] = None,
        force: bool = False
    ) -> ActionResult:
        """Push to remote

        Args:
            remote: Remote name
            branch: Branch to push
            force: Force push

        Returns:
            ActionResult
        """
        args = ["push", remote]

        if branch:
            args.append(branch)

        if force:
            args.append("--force")

        result = self._run_git(*args)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(
            message=f"Pushed to {remote}" + (f"/{branch}" if branch else ""),
            data=result.stdout
        )

    def pull(
        self,
        remote: str = "origin",
        branch: Optional[str] = None,
        rebase: bool = False
    ) -> ActionResult:
        """Pull from remote

        Args:
            remote: Remote name
            branch: Branch to pull
            rebase: Use rebase instead of merge

        Returns:
            ActionResult
        """
        args = ["pull"]

        if rebase:
            args.append("--rebase")

        args.append(remote)

        if branch:
            args.append(branch)

        result = self._run_git(*args)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(
            message=f"Pulled from {remote}" + (f"/{branch}" if branch else ""),
            data=result.stdout
        )

    def get_log(
        self,
        count: int = 10,
        oneline: bool = False,
        author: Optional[str] = None
    ) -> ActionResult:
        """Get commit history

        Args:
            count: Number of commits
            oneline: One line per commit
            author: Filter by author

        Returns:
            ActionResult with commits
        """
        args = ["log", f"-{count}"]

        if oneline:
            args.append("--oneline")
        else:
            args.append("--format=%H|%h|%an|%ae|%ad|%s")
            args.append("--date=short")

        if author:
            args.append(f"--author={author}")

        result = self._run_git(*args)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        if oneline:
            return ActionResult.ok(
                message=f"Last {count} commits",
                data=result.stdout.strip()
            )

        # Parse formatted output
        commits = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 6:
                commits.append(CommitInfo(
                    hash=parts[0],
                    short_hash=parts[1],
                    author=parts[2],
                    email=parts[3],
                    date=parts[4],
                    message=parts[5]
                ))

        return ActionResult.ok(
            message=f"Last {len(commits)} commits",
            data=commits
        )

    def manage_stash(
        self,
        action: str = "list",
        message: Optional[str] = None
    ) -> ActionResult:
        """Stash operations

        Args:
            action: Operation (save, pop, list, drop)
            message: Stash message for save

        Returns:
            ActionResult
        """
        if action == "list":
            result = self._run_git("stash", "list")
            return ActionResult.ok(
                message=f"{len(result.stdout.strip().split(chr(10)))} stashes" if result.stdout.strip() else "No stashes",
                data=result.stdout.strip()
            )

        elif action == "save":
            args = ["stash", "push"]
            if message:
                args.extend(["-m", message])

            result = self._run_git(*args)
            if result.returncode != 0:
                return ActionResult.fail(result.stderr)

            return ActionResult.ok("Changes stashed", data=result.stdout)

        elif action == "pop":
            result = self._run_git("stash", "pop")
            if result.returncode != 0:
                return ActionResult.fail(result.stderr)

            return ActionResult.ok("Stash applied and dropped", data=result.stdout)

        elif action == "drop":
            result = self._run_git("stash", "drop")
            if result.returncode != 0:
                return ActionResult.fail(result.stderr)

            return ActionResult.ok("Stash dropped", data=result.stdout)

        return ActionResult.fail(f"Unknown action: {action}")

    def reset(
        self,
        mode: str = "mixed",
        target: str = "HEAD"
    ) -> ActionResult:
        """Reset changes

        Args:
            mode: Reset mode (soft, mixed, hard)
            target: Reset target

        Returns:
            ActionResult
        """
        args = ["reset", f"--{mode}", target]

        result = self._run_git(*args)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr)

        return ActionResult.ok(
            message=f"Reset ({mode}) to {target}",
            data=result.stdout
        )

    def can_handle(self, request: str) -> float:
        """Check if request is git-related"""
        request_lower = request.lower()

        # High confidence keywords
        high_conf = ["git ", "commit", "push", "pull", "branch", "merge", "diff"]
        for kw in high_conf:
            if kw in request_lower:
                return 0.9

        # Medium confidence
        med_conf = ["changes", "history", "checkout", "stash", "log"]
        for kw in med_conf:
            if kw in request_lower:
                return 0.6

        return super().can_handle(request)

    def handle_request(self, request: str, **kwargs) -> Optional[ActionResult]:
        """Handle a natural language request

        Args:
            request: User's request

        Returns:
            ActionResult or None
        """
        request_lower = request.lower()

        # Status
        if any(kw in request_lower for kw in ["status", "what changed", "changes"]):
            return self.get_status(detailed=True)

        # Diff
        if "diff" in request_lower or "show changes" in request_lower:
            staged = "staged" in request_lower
            return self.get_diff(staged=staged)

        # Log
        if any(kw in request_lower for kw in ["log", "history", "commits"]):
            return self.get_log(count=10, oneline=True)

        # Branch list
        if "branch" in request_lower and "list" in request_lower:
            return self.manage_branch(action="list")

        return None
