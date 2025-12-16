"""
Project Requirements Tracker
Persistent tracking of project requirements and user requests.
"""
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime


class RequirementStatus(Enum):
    """Status of a requirement"""
    PENDING = "pending"          # Not started
    IN_PROGRESS = "in_progress"  # Currently working on
    COMPLETED = "completed"      # Done
    DEFERRED = "deferred"        # Postponed
    CANCELLED = "cancelled"      # No longer needed


class RequirementPriority(Enum):
    """Priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Requirement:
    """A single project requirement"""
    id: str
    title: str
    description: str
    status: str = RequirementStatus.PENDING.value
    priority: str = RequirementPriority.MEDIUM.value
    created_at: str = ""
    updated_at: str = ""
    completed_at: str = ""
    notes: List[str] = field(default_factory=list)
    sub_tasks: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Requirement":
        return cls(**data)


@dataclass
class Project:
    """Project containing requirements"""
    name: str
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    requirements: List[Requirement] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "requirements": [r.to_dict() for r in self.requirements]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Project":
        reqs = [Requirement.from_dict(r) for r in data.get("requirements", [])]
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            requirements=reqs
        )


class RequirementsTracker:
    """
    Manages project requirements with persistence.

    Features:
    - Add/update/remove requirements
    - Track status and priority
    - Persist to file
    - Query and filter requirements
    """

    # Storage location for requirements
    STORAGE_DIR = ".nc1709"
    STORAGE_FILE = "requirements.json"

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the tracker.

        Args:
            project_root: Root directory of the project (defaults to cwd)
        """
        self.project_root = project_root or Path.cwd()
        self.storage_path = self.project_root / self.STORAGE_DIR / self.STORAGE_FILE
        self.project: Optional[Project] = None
        self._load()

    def _ensure_storage_dir(self) -> None:
        """Ensure storage directory exists"""
        storage_dir = self.project_root / self.STORAGE_DIR
        storage_dir.mkdir(exist_ok=True)

    def _load(self) -> None:
        """Load requirements from disk"""
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text())
                self.project = Project.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                self.project = None
        else:
            self.project = None

    def _save(self) -> None:
        """Save requirements to disk"""
        if self.project:
            self._ensure_storage_dir()
            self.project.updated_at = datetime.now().isoformat()
            self.storage_path.write_text(
                json.dumps(self.project.to_dict(), indent=2)
            )

    def _generate_id(self) -> str:
        """Generate a unique requirement ID"""
        import hashlib
        timestamp = str(time.time()).encode()
        return f"REQ-{hashlib.md5(timestamp).hexdigest()[:8].upper()}"

    def init_project(self, name: str, description: str = "") -> Project:
        """
        Initialize a new project.

        Args:
            name: Project name
            description: Project description

        Returns:
            The created project
        """
        self.project = Project(name=name, description=description)
        self._save()
        return self.project

    def has_project(self) -> bool:
        """Check if a project is initialized"""
        return self.project is not None

    def get_project(self) -> Optional[Project]:
        """Get the current project"""
        return self.project

    def add_requirement(
        self,
        title: str,
        description: str = "",
        priority: str = RequirementPriority.MEDIUM.value,
        tags: List[str] = None
    ) -> Requirement:
        """
        Add a new requirement.

        Args:
            title: Short requirement title
            description: Detailed description
            priority: Priority level
            tags: Tags for categorization

        Returns:
            The created requirement
        """
        if not self.project:
            # Auto-create project based on directory name
            self.init_project(self.project_root.name)

        req = Requirement(
            id=self._generate_id(),
            title=title,
            description=description,
            priority=priority,
            tags=tags or []
        )

        self.project.requirements.append(req)
        self._save()
        return req

    def update_requirement(
        self,
        req_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        notes: Optional[List[str]] = None,
        sub_tasks: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Requirement]:
        """
        Update an existing requirement.

        Args:
            req_id: Requirement ID
            title: New title (if changing)
            description: New description (if changing)
            status: New status (if changing)
            priority: New priority (if changing)
            notes: New notes (if changing)
            sub_tasks: New sub-tasks (if changing)
            tags: New tags (if changing)

        Returns:
            Updated requirement or None if not found
        """
        if not self.project:
            return None

        req = self.get_requirement(req_id)
        if not req:
            return None

        if title is not None:
            req.title = title
        if description is not None:
            req.description = description
        if status is not None:
            req.status = status
            if status == RequirementStatus.COMPLETED.value:
                req.completed_at = datetime.now().isoformat()
        if priority is not None:
            req.priority = priority
        if notes is not None:
            req.notes = notes
        if sub_tasks is not None:
            req.sub_tasks = sub_tasks
        if tags is not None:
            req.tags = tags

        req.updated_at = datetime.now().isoformat()
        self._save()
        return req

    def add_note(self, req_id: str, note: str) -> Optional[Requirement]:
        """Add a note to a requirement"""
        if not self.project:
            return None

        req = self.get_requirement(req_id)
        if not req:
            return None

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        req.notes.append(f"[{timestamp}] {note}")
        req.updated_at = datetime.now().isoformat()
        self._save()
        return req

    def add_sub_task(self, req_id: str, sub_task: str) -> Optional[Requirement]:
        """Add a sub-task to a requirement"""
        if not self.project:
            return None

        req = self.get_requirement(req_id)
        if not req:
            return None

        req.sub_tasks.append(sub_task)
        req.updated_at = datetime.now().isoformat()
        self._save()
        return req

    def set_status(self, req_id: str, status: RequirementStatus) -> Optional[Requirement]:
        """Set requirement status"""
        return self.update_requirement(req_id, status=status.value)

    def remove_requirement(self, req_id: str) -> bool:
        """
        Remove a requirement.

        Args:
            req_id: Requirement ID

        Returns:
            True if removed, False if not found
        """
        if not self.project:
            return False

        for i, req in enumerate(self.project.requirements):
            if req.id == req_id:
                self.project.requirements.pop(i)
                self._save()
                return True
        return False

    def get_requirement(self, req_id: str) -> Optional[Requirement]:
        """Get a requirement by ID"""
        if not self.project:
            return None

        for req in self.project.requirements:
            if req.id == req_id:
                return req
        return None

    def get_requirements(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Requirement]:
        """
        Get filtered requirements.

        Args:
            status: Filter by status
            priority: Filter by priority
            tag: Filter by tag

        Returns:
            List of matching requirements
        """
        if not self.project:
            return []

        reqs = self.project.requirements

        if status:
            reqs = [r for r in reqs if r.status == status]
        if priority:
            reqs = [r for r in reqs if r.priority == priority]
        if tag:
            reqs = [r for r in reqs if tag in r.tags]

        return reqs

    def get_pending(self) -> List[Requirement]:
        """Get all pending requirements"""
        return self.get_requirements(status=RequirementStatus.PENDING.value)

    def get_in_progress(self) -> List[Requirement]:
        """Get all in-progress requirements"""
        return self.get_requirements(status=RequirementStatus.IN_PROGRESS.value)

    def get_completed(self) -> List[Requirement]:
        """Get all completed requirements"""
        return self.get_requirements(status=RequirementStatus.COMPLETED.value)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of requirements.

        Returns:
            Dictionary with counts and stats
        """
        if not self.project:
            return {
                "project": None,
                "total": 0,
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
                "deferred": 0,
                "cancelled": 0,
            }

        reqs = self.project.requirements
        return {
            "project": self.project.name,
            "description": self.project.description,
            "total": len(reqs),
            "pending": len([r for r in reqs if r.status == RequirementStatus.PENDING.value]),
            "in_progress": len([r for r in reqs if r.status == RequirementStatus.IN_PROGRESS.value]),
            "completed": len([r for r in reqs if r.status == RequirementStatus.COMPLETED.value]),
            "deferred": len([r for r in reqs if r.status == RequirementStatus.DEFERRED.value]),
            "cancelled": len([r for r in reqs if r.status == RequirementStatus.CANCELLED.value]),
        }

    def format_requirement(self, req: Requirement, verbose: bool = False) -> str:
        """
        Format a requirement for display.

        Args:
            req: The requirement
            verbose: Include full details

        Returns:
            Formatted string
        """
        # Status icons
        status_icons = {
            RequirementStatus.PENDING.value: "○",
            RequirementStatus.IN_PROGRESS.value: "●",
            RequirementStatus.COMPLETED.value: "✓",
            RequirementStatus.DEFERRED.value: "◐",
            RequirementStatus.CANCELLED.value: "✗",
        }

        # Priority colors (ANSI)
        priority_colors = {
            RequirementPriority.HIGH.value: "\033[91m",    # Red
            RequirementPriority.MEDIUM.value: "\033[93m",  # Yellow
            RequirementPriority.LOW.value: "\033[92m",     # Green
        }
        reset = "\033[0m"

        icon = status_icons.get(req.status, "○")
        priority_color = priority_colors.get(req.priority, "")

        line = f"{icon} [{req.id}] {priority_color}{req.title}{reset}"

        if req.priority == RequirementPriority.HIGH.value:
            line += " 🔥"

        if verbose:
            line += f"\n   Status: {req.status}"
            line += f"\n   Priority: {req.priority}"
            if req.description:
                line += f"\n   Description: {req.description}"
            if req.tags:
                line += f"\n   Tags: {', '.join(req.tags)}"
            if req.sub_tasks:
                line += f"\n   Sub-tasks:"
                for task in req.sub_tasks:
                    line += f"\n     - {task}"
            if req.notes:
                line += f"\n   Notes:"
                for note in req.notes[-3:]:  # Show last 3 notes
                    line += f"\n     {note}"
            line += f"\n   Created: {req.created_at[:16]}"
            if req.completed_at:
                line += f"\n   Completed: {req.completed_at[:16]}"

        return line

    def format_all(self, verbose: bool = False, include_completed: bool = False) -> str:
        """
        Format all requirements for display.

        Args:
            verbose: Include full details
            include_completed: Include completed requirements

        Returns:
            Formatted string of all requirements
        """
        if not self.project:
            return "No project initialized. Use /requirements init <name> to start."

        lines = []
        lines.append(f"📋 Project: {self.project.name}")
        if self.project.description:
            lines.append(f"   {self.project.description}")
        lines.append("")

        # Group by status
        statuses = [
            (RequirementStatus.IN_PROGRESS.value, "In Progress"),
            (RequirementStatus.PENDING.value, "Pending"),
        ]

        if include_completed:
            statuses.extend([
                (RequirementStatus.COMPLETED.value, "Completed"),
                (RequirementStatus.DEFERRED.value, "Deferred"),
            ])

        for status_value, status_name in statuses:
            reqs = [r for r in self.project.requirements if r.status == status_value]
            if reqs:
                lines.append(f"── {status_name} ({len(reqs)}) ──")
                for req in reqs:
                    lines.append(self.format_requirement(req, verbose))
                lines.append("")

        # Summary
        summary = self.get_summary()
        lines.append(f"Total: {summary['total']} | "
                    f"Pending: {summary['pending']} | "
                    f"In Progress: {summary['in_progress']} | "
                    f"Completed: {summary['completed']}")

        return "\n".join(lines)


# Global instance
_tracker: Optional[RequirementsTracker] = None


def get_tracker() -> RequirementsTracker:
    """Get the global requirements tracker"""
    global _tracker
    if _tracker is None:
        _tracker = RequirementsTracker()
    return _tracker


def reset_tracker(project_root: Optional[Path] = None) -> RequirementsTracker:
    """Reset the tracker with a new project root"""
    global _tracker
    _tracker = RequirementsTracker(project_root)
    return _tracker
