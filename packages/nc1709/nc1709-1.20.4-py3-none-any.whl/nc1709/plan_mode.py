"""
Plan Mode for NC1709

Provides planning capabilities similar to Claude Code's plan mode:
- Think through tasks before executing
- Generate step-by-step plans
- Review and approve plans before execution
- Iterate on plans with user feedback
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PlanStatus(Enum):
    """Status of a plan"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanStep:
    """A single step in a plan"""
    id: int
    description: str
    details: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, skipped, failed
    result: Optional[str] = None
    files_affected: List[str] = field(default_factory=list)


@dataclass
class Plan:
    """A complete execution plan"""
    id: str
    title: str
    description: str
    steps: List[PlanStep]
    status: PlanStatus = PlanStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_feedback: Optional[str] = None
    estimated_files: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)


class PlanManager:
    """
    Manages plan mode operations.

    Features:
    - Create and store plans
    - Track plan status and progress
    - Support plan approval workflow
    - Persist plans for review
    """

    def __init__(self):
        self._current_plan: Optional[Plan] = None
        self._plan_history: List[Plan] = []
        self._plan_mode_active: bool = False
        self._plan_counter: int = 0

    @property
    def is_plan_mode(self) -> bool:
        """Check if plan mode is active"""
        return self._plan_mode_active

    @property
    def current_plan(self) -> Optional[Plan]:
        """Get the current plan"""
        return self._current_plan

    def enter_plan_mode(self) -> None:
        """Enter plan mode"""
        self._plan_mode_active = True

    def exit_plan_mode(self) -> None:
        """Exit plan mode"""
        self._plan_mode_active = False

    def create_plan(
        self,
        title: str,
        description: str,
        steps: List[Dict[str, Any]],
        estimated_files: Optional[List[str]] = None,
        risks: Optional[List[str]] = None,
        alternatives: Optional[List[str]] = None
    ) -> Plan:
        """
        Create a new plan.

        Args:
            title: Plan title
            description: Plan description
            steps: List of step dictionaries with description and optional details
            estimated_files: List of files that may be affected
            risks: List of potential risks
            alternatives: List of alternative approaches

        Returns:
            The created Plan
        """
        self._plan_counter += 1
        plan_id = f"plan_{self._plan_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        plan_steps = []
        for i, step_data in enumerate(steps, 1):
            step = PlanStep(
                id=i,
                description=step_data.get("description", ""),
                details=step_data.get("details"),
                files_affected=step_data.get("files", [])
            )
            plan_steps.append(step)

        plan = Plan(
            id=plan_id,
            title=title,
            description=description,
            steps=plan_steps,
            status=PlanStatus.PENDING_APPROVAL,
            estimated_files=estimated_files or [],
            risks=risks or [],
            alternatives=alternatives or []
        )

        self._current_plan = plan
        return plan

    def approve_plan(self) -> bool:
        """Approve the current plan for execution"""
        if not self._current_plan:
            return False

        self._current_plan.status = PlanStatus.APPROVED
        self._current_plan.approved_at = datetime.now()
        return True

    def reject_plan(self, feedback: Optional[str] = None) -> bool:
        """Reject the current plan"""
        if not self._current_plan:
            return False

        self._current_plan.status = PlanStatus.REJECTED
        self._current_plan.user_feedback = feedback
        self._plan_history.append(self._current_plan)
        self._current_plan = None
        return True

    def start_execution(self) -> bool:
        """Start executing the approved plan"""
        if not self._current_plan or self._current_plan.status != PlanStatus.APPROVED:
            return False

        self._current_plan.status = PlanStatus.IN_PROGRESS
        return True

    def update_step(self, step_id: int, status: str, result: Optional[str] = None) -> bool:
        """Update a step's status"""
        if not self._current_plan:
            return False

        for step in self._current_plan.steps:
            if step.id == step_id:
                step.status = status
                step.result = result
                return True

        return False

    def complete_plan(self, success: bool = True) -> None:
        """Mark the plan as complete"""
        if not self._current_plan:
            return

        self._current_plan.status = PlanStatus.COMPLETED if success else PlanStatus.FAILED
        self._current_plan.completed_at = datetime.now()
        self._plan_history.append(self._current_plan)
        self._current_plan = None
        self._plan_mode_active = False

    def get_plan_summary(self) -> Optional[str]:
        """Get a formatted summary of the current plan"""
        if not self._current_plan:
            return None

        plan = self._current_plan
        lines = []

        # Header
        lines.append(f"\n\033[1m{plan.title}\033[0m")
        lines.append(f"\033[90mStatus: {plan.status.value}\033[0m")
        lines.append("")
        lines.append(plan.description)
        lines.append("")

        # Steps
        lines.append("\033[1mSteps:\033[0m")
        for step in plan.steps:
            status_icon = {
                "pending": "○",
                "in_progress": "◐",
                "completed": "●",
                "skipped": "○",
                "failed": "✗"
            }.get(step.status, "○")

            lines.append(f"  {status_icon} {step.id}. {step.description}")
            if step.details:
                lines.append(f"      \033[90m{step.details}\033[0m")
            if step.files_affected:
                lines.append(f"      \033[36mFiles: {', '.join(step.files_affected)}\033[0m")

        lines.append("")

        # Files
        if plan.estimated_files:
            lines.append("\033[1mFiles that may be affected:\033[0m")
            for f in plan.estimated_files:
                lines.append(f"  • {f}")
            lines.append("")

        # Risks
        if plan.risks:
            lines.append("\033[1;33mPotential Risks:\033[0m")
            for risk in plan.risks:
                lines.append(f"  ⚠ {risk}")
            lines.append("")

        # Alternatives
        if plan.alternatives:
            lines.append("\033[1mAlternative Approaches:\033[0m")
            for alt in plan.alternatives:
                lines.append(f"  → {alt}")
            lines.append("")

        return "\n".join(lines)

    def get_execution_prompt(self) -> Optional[str]:
        """Get the prompt text for executing the plan"""
        if not self._current_plan:
            return None

        steps_text = "\n".join([
            f"{step.id}. {step.description}"
            + (f"\n   Details: {step.details}" if step.details else "")
            for step in self._current_plan.steps
        ])

        return f"""Execute the following plan:

**{self._current_plan.title}**

{self._current_plan.description}

Steps to follow:
{steps_text}

Files that may be affected: {', '.join(self._current_plan.estimated_files) if self._current_plan.estimated_files else 'TBD based on steps'}

Please execute each step in order, updating progress as you go.
"""

    def get_plan_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent plan history"""
        return [
            {
                "id": plan.id,
                "title": plan.title,
                "status": plan.status.value,
                "created": plan.created_at.isoformat(),
                "steps_count": len(plan.steps)
            }
            for plan in self._plan_history[-limit:]
        ]


# Global plan manager
_plan_manager: Optional[PlanManager] = None


def get_plan_manager() -> PlanManager:
    """Get or create the global plan manager"""
    global _plan_manager
    if _plan_manager is None:
        _plan_manager = PlanManager()
    return _plan_manager


def generate_plan_from_task(task: str) -> Dict[str, Any]:
    """
    Generate a plan structure from a task description.

    This is a template that would be filled in by the LLM.

    Args:
        task: The task description

    Returns:
        A plan structure dict
    """
    return {
        "title": f"Plan: {task[:50]}{'...' if len(task) > 50 else ''}",
        "description": f"Implementation plan for: {task}",
        "steps": [],
        "estimated_files": [],
        "risks": [],
        "alternatives": []
    }


# Plan mode prompt template
PLAN_MODE_SYSTEM_PROMPT = """You are in PLAN MODE. Before making any changes, you must:

1. **Analyze** the task thoroughly
2. **Create a plan** with clear, numbered steps
3. **Identify** files that will be affected
4. **Consider** potential risks or issues
5. **Present alternatives** if applicable

Format your plan as:

## Plan: [Title]

### Description
[Brief description of what this plan accomplishes]

### Steps
1. [First step]
2. [Second step]
...

### Files Affected
- file1.py
- file2.ts

### Potential Risks
- [Risk 1]
- [Risk 2]

### Alternative Approaches
- [Alternative 1]
- [Alternative 2]

After presenting the plan, ask the user if they want to:
- **Approve** the plan and proceed with execution
- **Modify** the plan with their feedback
- **Reject** the plan and start over

Do NOT make any file changes until the plan is approved.
"""
