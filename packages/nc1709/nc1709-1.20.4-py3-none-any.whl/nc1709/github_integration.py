"""
GitHub Integration for NC1709

Provides GitHub-related functionality:
- PR creation and management
- Issue tracking
- GitHub CLI (gh) integration
- Repository information
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PullRequest:
    """Represents a GitHub Pull Request"""
    number: int
    title: str
    url: str
    state: str  # open, closed, merged
    author: str
    branch: str
    base: str
    created_at: str
    updated_at: str
    body: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)
    checks_status: Optional[str] = None


@dataclass
class Issue:
    """Represents a GitHub Issue"""
    number: int
    title: str
    url: str
    state: str  # open, closed
    author: str
    created_at: str
    body: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)


class GitHubIntegration:
    """
    GitHub integration using the gh CLI.

    Features:
    - Check gh CLI availability
    - Create and manage PRs
    - View and manage issues
    - Get repository info
    """

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize GitHub integration.

        Args:
            repo_path: Path to git repository (defaults to cwd)
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self._gh_available = self._check_gh_cli()
        self._authenticated = False

        if self._gh_available:
            self._authenticated = self._check_auth()

    def _check_gh_cli(self) -> bool:
        """Check if gh CLI is available"""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _check_auth(self) -> bool:
        """Check if gh is authenticated"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                cwd=str(self.repo_path),
                timeout=10
            )
            return result.returncode == 0
        except subprocess.SubprocessError:
            return False

    @property
    def is_available(self) -> bool:
        """Check if GitHub integration is available"""
        return self._gh_available

    @property
    def is_authenticated(self) -> bool:
        """Check if gh is authenticated"""
        return self._authenticated

    def _run_gh(self, *args, json_output: bool = False) -> subprocess.CompletedProcess:
        """Run a gh command"""
        cmd = ["gh"] + list(args)
        if json_output:
            cmd.append("--json")
        return subprocess.run(
            cmd,
            cwd=str(self.repo_path),
            capture_output=True,
            text=True,
            timeout=60
        )

    def get_repo_info(self) -> Optional[Dict[str, Any]]:
        """Get current repository information"""
        if not self._gh_available:
            return None

        try:
            result = self._run_gh(
                "repo", "view", "--json",
                "name,owner,description,url,defaultBranchRef,isPrivate"
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except (subprocess.SubprocessError, json.JSONDecodeError):
            pass
        return None

    def create_pr(
        self,
        title: str,
        body: str,
        base: str = "main",
        draft: bool = False,
        labels: Optional[List[str]] = None,
        reviewers: Optional[List[str]] = None
    ) -> Optional[PullRequest]:
        """
        Create a new Pull Request.

        Args:
            title: PR title
            body: PR description
            base: Base branch to merge into
            draft: Create as draft PR
            labels: List of labels to apply
            reviewers: List of reviewers to request

        Returns:
            PullRequest object if successful, None otherwise
        """
        if not self._gh_available or not self._authenticated:
            return None

        try:
            cmd = ["pr", "create", "--title", title, "--body", body, "--base", base]

            if draft:
                cmd.append("--draft")

            if labels:
                for label in labels:
                    cmd.extend(["--label", label])

            if reviewers:
                for reviewer in reviewers:
                    cmd.extend(["--reviewer", reviewer])

            result = self._run_gh(*cmd)

            if result.returncode == 0:
                # Parse the output URL to get PR info
                pr_url = result.stdout.strip()

                # Get PR details
                pr_info = self.get_pr_by_url(pr_url)
                if pr_info:
                    return pr_info

                # Fallback: create minimal PR object
                return PullRequest(
                    number=0,
                    title=title,
                    url=pr_url,
                    state="open",
                    author="",
                    branch="",
                    base=base,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    body=body
                )

        except subprocess.SubprocessError:
            pass

        return None

    def get_pr_by_url(self, url: str) -> Optional[PullRequest]:
        """Get PR details from URL"""
        try:
            # Extract PR number from URL
            parts = url.rstrip('/').split('/')
            pr_number = parts[-1] if parts else None

            if pr_number and pr_number.isdigit():
                return self.get_pr(int(pr_number))
        except Exception:
            pass
        return None

    def get_pr(self, number: int) -> Optional[PullRequest]:
        """Get Pull Request by number"""
        if not self._gh_available:
            return None

        try:
            result = self._run_gh(
                "pr", "view", str(number), "--json",
                "number,title,url,state,author,headRefName,baseRefName,createdAt,updatedAt,body,labels,reviewRequests"
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return PullRequest(
                    number=data.get("number", 0),
                    title=data.get("title", ""),
                    url=data.get("url", ""),
                    state=data.get("state", "").lower(),
                    author=data.get("author", {}).get("login", ""),
                    branch=data.get("headRefName", ""),
                    base=data.get("baseRefName", ""),
                    created_at=data.get("createdAt", ""),
                    updated_at=data.get("updatedAt", ""),
                    body=data.get("body"),
                    labels=[l.get("name", "") for l in data.get("labels", [])],
                    reviewers=[r.get("login", "") for r in data.get("reviewRequests", [])]
                )
        except (subprocess.SubprocessError, json.JSONDecodeError):
            pass
        return None

    def list_prs(self, state: str = "open", limit: int = 10) -> List[PullRequest]:
        """List Pull Requests"""
        if not self._gh_available:
            return []

        try:
            result = self._run_gh(
                "pr", "list", "--state", state, "--limit", str(limit), "--json",
                "number,title,url,state,author,headRefName,baseRefName,createdAt,updatedAt,labels"
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return [
                    PullRequest(
                        number=pr.get("number", 0),
                        title=pr.get("title", ""),
                        url=pr.get("url", ""),
                        state=pr.get("state", "").lower(),
                        author=pr.get("author", {}).get("login", ""),
                        branch=pr.get("headRefName", ""),
                        base=pr.get("baseRefName", ""),
                        created_at=pr.get("createdAt", ""),
                        updated_at=pr.get("updatedAt", ""),
                        labels=[l.get("name", "") for l in pr.get("labels", [])]
                    )
                    for pr in data
                ]
        except (subprocess.SubprocessError, json.JSONDecodeError):
            pass
        return []

    def get_pr_checks(self, number: int) -> Optional[Dict[str, Any]]:
        """Get CI check status for a PR"""
        if not self._gh_available:
            return None

        try:
            result = self._run_gh(
                "pr", "checks", str(number), "--json",
                "name,status,conclusion,startedAt,completedAt"
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
        except (subprocess.SubprocessError, json.JSONDecodeError):
            pass
        return None

    def merge_pr(
        self,
        number: int,
        method: str = "merge",  # merge, squash, rebase
        delete_branch: bool = True
    ) -> bool:
        """Merge a Pull Request"""
        if not self._gh_available or not self._authenticated:
            return False

        try:
            cmd = ["pr", "merge", str(number), f"--{method}"]
            if delete_branch:
                cmd.append("--delete-branch")

            result = self._run_gh(*cmd)
            return result.returncode == 0
        except subprocess.SubprocessError:
            return False

    def list_issues(self, state: str = "open", limit: int = 10) -> List[Issue]:
        """List Issues"""
        if not self._gh_available:
            return []

        try:
            result = self._run_gh(
                "issue", "list", "--state", state, "--limit", str(limit), "--json",
                "number,title,url,state,author,createdAt,body,labels,assignees"
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return [
                    Issue(
                        number=issue.get("number", 0),
                        title=issue.get("title", ""),
                        url=issue.get("url", ""),
                        state=issue.get("state", "").lower(),
                        author=issue.get("author", {}).get("login", ""),
                        created_at=issue.get("createdAt", ""),
                        body=issue.get("body"),
                        labels=[l.get("name", "") for l in issue.get("labels", [])],
                        assignees=[a.get("login", "") for a in issue.get("assignees", [])]
                    )
                    for issue in data
                ]
        except (subprocess.SubprocessError, json.JSONDecodeError):
            pass
        return []

    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Optional[Issue]:
        """Create a new Issue"""
        if not self._gh_available or not self._authenticated:
            return None

        try:
            cmd = ["issue", "create", "--title", title, "--body", body]

            if labels:
                for label in labels:
                    cmd.extend(["--label", label])

            if assignees:
                for assignee in assignees:
                    cmd.extend(["--assignee", assignee])

            result = self._run_gh(*cmd)

            if result.returncode == 0:
                issue_url = result.stdout.strip()
                # Extract issue number and return
                parts = issue_url.rstrip('/').split('/')
                issue_number = int(parts[-1]) if parts and parts[-1].isdigit() else 0

                return Issue(
                    number=issue_number,
                    title=title,
                    url=issue_url,
                    state="open",
                    author="",
                    created_at=datetime.now().isoformat(),
                    body=body,
                    labels=labels or [],
                    assignees=assignees or []
                )

        except subprocess.SubprocessError:
            pass

        return None

    def get_current_branch(self) -> Optional[str]:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except subprocess.SubprocessError:
            pass
        return None

    def push_branch(self, set_upstream: bool = True) -> bool:
        """Push current branch to remote"""
        try:
            branch = self.get_current_branch()
            if not branch:
                return False

            cmd = ["git", "push"]
            if set_upstream:
                cmd.extend(["-u", "origin", branch])

            result = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except subprocess.SubprocessError:
            return False


# Global GitHub integration
_github_integration: Optional[GitHubIntegration] = None


def get_github_integration() -> GitHubIntegration:
    """Get or create the global GitHub integration"""
    global _github_integration
    if _github_integration is None:
        _github_integration = GitHubIntegration()
    return _github_integration


def format_pr_summary(pr: PullRequest) -> str:
    """Format a PR for display"""
    lines = []
    lines.append(f"\033[1m#{pr.number}: {pr.title}\033[0m")
    lines.append(f"  URL: {pr.url}")
    lines.append(f"  State: {pr.state}")
    lines.append(f"  Branch: {pr.branch} → {pr.base}")
    lines.append(f"  Author: {pr.author}")
    if pr.labels:
        lines.append(f"  Labels: {', '.join(pr.labels)}")
    return "\n".join(lines)


def format_issue_summary(issue: Issue) -> str:
    """Format an issue for display"""
    lines = []
    lines.append(f"\033[1m#{issue.number}: {issue.title}\033[0m")
    lines.append(f"  URL: {issue.url}")
    lines.append(f"  State: {issue.state}")
    lines.append(f"  Author: {issue.author}")
    if issue.labels:
        lines.append(f"  Labels: {', '.join(issue.labels)}")
    if issue.assignees:
        lines.append(f"  Assignees: {', '.join(issue.assignees)}")
    return "\n".join(lines)
