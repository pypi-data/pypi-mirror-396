"""
Layer 5: Anticipation Engine

Predicts user needs before they ask:
- Workflow prediction based on history
- Proactive suggestions (next files to edit, tests to run)
- Context pre-loading for faster responses
- Issue prediction (potential bugs, conflicts)
- Smart defaults based on patterns

This layer answers: "What will the user probably need next?"
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from collections import Counter, defaultdict
import threading
import heapq

logger = logging.getLogger(__name__)


class SuggestionType(Enum):
    """Types of proactive suggestions"""
    NEXT_FILE = "next_file"  # Files user might edit next
    RUN_TESTS = "run_tests"  # Suggest running tests
    GIT_COMMIT = "git_commit"  # Suggest committing changes
    FIX_ERROR = "fix_error"  # Potential error to address
    DOCUMENTATION = "documentation"  # Suggest adding docs
    REFACTOR = "refactor"  # Suggest refactoring
    SECURITY = "security"  # Security check suggestion
    PERFORMANCE = "performance"  # Performance improvement
    CONTEXT_PRELOAD = "context_preload"  # Pre-load relevant context
    WORKFLOW_STEP = "workflow_step"  # Next step in workflow


@dataclass
class Suggestion:
    """A proactive suggestion"""
    suggestion_type: SuggestionType
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    priority: int = 0  # Higher = more important
    action: Optional[str] = None  # Command or action to take
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None  # When suggestion becomes stale

    def is_valid(self) -> bool:
        """Check if suggestion is still valid"""
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True


@dataclass
class WorkflowPattern:
    """A detected workflow pattern"""
    name: str
    steps: List[str]  # Sequence of actions
    frequency: int  # How often this pattern occurs
    last_seen: datetime = field(default_factory=datetime.now)
    confidence: float = 0.5


@dataclass
class PredictionContext:
    """Context for making predictions"""
    current_file: Optional[str] = None
    recent_files: List[str] = field(default_factory=list)
    recent_tasks: List[str] = field(default_factory=list)
    recent_errors: List[str] = field(default_factory=list)
    uncommitted_changes: bool = False
    tests_passing: Optional[bool] = None
    time_of_day: int = 12  # Hour
    session_duration_minutes: int = 0


class WorkflowPredictor:
    """Predicts workflow patterns and next actions"""

    def __init__(self, min_pattern_frequency: int = 2):
        self.min_pattern_frequency = min_pattern_frequency
        self._action_sequences: List[List[str]] = []
        self._patterns: Dict[str, WorkflowPattern] = {}
        self._current_sequence: List[str] = []
        self._lock = threading.Lock()

    def record_action(self, action: str) -> None:
        """Record an action in the current sequence"""
        with self._lock:
            self._current_sequence.append(action)
            # Keep sequence length manageable
            if len(self._current_sequence) > 20:
                self._current_sequence = self._current_sequence[-20:]

    def end_sequence(self) -> None:
        """End the current action sequence"""
        with self._lock:
            if len(self._current_sequence) >= 2:
                self._action_sequences.append(self._current_sequence.copy())
                # Keep last 100 sequences
                if len(self._action_sequences) > 100:
                    self._action_sequences = self._action_sequences[-100:]
            self._current_sequence = []

    def detect_patterns(self) -> List[WorkflowPattern]:
        """Detect repeated patterns in action sequences"""
        patterns = []

        with self._lock:
            # Find common subsequences
            subsequence_counts: Dict[tuple, int] = defaultdict(int)

            for sequence in self._action_sequences:
                # Look for patterns of length 2-5
                for length in range(2, min(6, len(sequence) + 1)):
                    for i in range(len(sequence) - length + 1):
                        subseq = tuple(sequence[i:i + length])
                        subsequence_counts[subseq] += 1

            # Create patterns from frequent subsequences
            for subseq, count in subsequence_counts.items():
                if count >= self.min_pattern_frequency:
                    pattern_name = f"pattern_{'_'.join(subseq[:2])}"
                    patterns.append(WorkflowPattern(
                        name=pattern_name,
                        steps=list(subseq),
                        frequency=count,
                        confidence=min(1.0, count / 10),
                    ))

            # Store patterns
            for pattern in patterns:
                self._patterns[pattern.name] = pattern

        return patterns

    def predict_next_action(self, current_action: str) -> List[Tuple[str, float]]:
        """Predict the next likely action given the current one"""
        predictions = []

        with self._lock:
            # Look at the current sequence + all patterns
            next_action_counts: Counter = Counter()

            # From patterns
            for pattern in self._patterns.values():
                for i, step in enumerate(pattern.steps[:-1]):
                    if step == current_action:
                        next_action = pattern.steps[i + 1]
                        next_action_counts[next_action] += pattern.frequency

            # From recent sequences
            for sequence in self._action_sequences[-20:]:
                for i, action in enumerate(sequence[:-1]):
                    if action == current_action:
                        next_action_counts[sequence[i + 1]] += 1

            # Convert to probabilities
            total = sum(next_action_counts.values())
            if total > 0:
                predictions = [
                    (action, count / total)
                    for action, count in next_action_counts.most_common(5)
                ]

        return predictions


class FilePredictor:
    """Predicts which files user will work with next"""

    def __init__(self):
        self._file_transitions: Dict[str, Counter] = defaultdict(Counter)
        self._file_access_times: Dict[str, datetime] = {}
        self._file_clusters: Dict[str, set] = defaultdict(set)  # Files often edited together
        self._lock = threading.Lock()

    def record_file_access(self, file_path: str, previous_file: Optional[str] = None) -> None:
        """Record a file access"""
        with self._lock:
            self._file_access_times[file_path] = datetime.now()

            if previous_file:
                # Record transition
                self._file_transitions[previous_file][file_path] += 1
                # Record cluster (files edited in same session)
                self._file_clusters[previous_file].add(file_path)
                self._file_clusters[file_path].add(previous_file)

    def predict_next_files(
        self,
        current_file: str,
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """Predict next files to be accessed"""
        predictions = []

        with self._lock:
            # From transitions
            if current_file in self._file_transitions:
                transitions = self._file_transitions[current_file]
                total = sum(transitions.values())
                for file_path, count in transitions.most_common(limit):
                    predictions.append((file_path, count / total))

            # From clusters (if not enough from transitions)
            if len(predictions) < limit and current_file in self._file_clusters:
                cluster = self._file_clusters[current_file]
                for file_path in list(cluster)[:limit - len(predictions)]:
                    if file_path not in [p[0] for p in predictions]:
                        predictions.append((file_path, 0.3))  # Lower confidence

        return predictions[:limit]

    def get_related_files(self, file_path: str) -> List[str]:
        """Get files related to the given file"""
        with self._lock:
            related = set()

            # From clusters
            if file_path in self._file_clusters:
                related.update(self._file_clusters[file_path])

            # From transitions (both directions)
            if file_path in self._file_transitions:
                related.update(self._file_transitions[file_path].keys())

            for source, targets in self._file_transitions.items():
                if file_path in targets:
                    related.add(source)

            return list(related)[:10]


class IssuePredictor:
    """Predicts potential issues and problems"""

    # Patterns that often lead to bugs
    BUG_PATTERNS = [
        ("missing_error_handling", ["try", "except", "error"]),
        ("missing_null_check", ["None", "null", "undefined"]),
        ("hardcoded_values", ["localhost", "127.0.0.1", "password"]),
        ("missing_tests", ["def ", "class ", "test"]),
    ]

    def predict_issues(
        self,
        file_path: Optional[str] = None,
        recent_changes: Optional[List[str]] = None,
        context: Optional[PredictionContext] = None
    ) -> List[Suggestion]:
        """Predict potential issues"""
        issues = []

        # Check for uncommitted changes
        if context and context.uncommitted_changes:
            issues.append(Suggestion(
                suggestion_type=SuggestionType.GIT_COMMIT,
                title="Uncommitted changes detected",
                description="You have uncommitted changes. Consider committing or stashing them.",
                confidence=0.8,
                priority=2,
                action="/git commit",
            ))

        # Check for test suggestions
        if context and context.recent_tasks:
            code_tasks = [t for t in context.recent_tasks if "code" in t.lower() or "function" in t.lower()]
            if code_tasks and context.tests_passing is None:
                issues.append(Suggestion(
                    suggestion_type=SuggestionType.RUN_TESTS,
                    title="Tests may need updating",
                    description="You've made code changes. Consider running tests.",
                    confidence=0.7,
                    priority=3,
                    action="/test",
                ))

        # Check for documentation suggestions
        if context and len(context.recent_files) > 3:
            issues.append(Suggestion(
                suggestion_type=SuggestionType.DOCUMENTATION,
                title="Consider updating documentation",
                description=f"You've modified {len(context.recent_files)} files. Documentation may need updating.",
                confidence=0.5,
                priority=1,
            ))

        return issues


class SuggestionQueue:
    """Priority queue for managing suggestions"""

    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self._queue: List[Tuple[int, int, Suggestion]] = []  # (priority, id, suggestion)
        self._counter = 0
        self._lock = threading.Lock()

    def add(self, suggestion: Suggestion) -> None:
        """Add a suggestion to the queue"""
        with self._lock:
            # Use negative priority for max-heap behavior
            heapq.heappush(
                self._queue,
                (-suggestion.priority, self._counter, suggestion)
            )
            self._counter += 1

            # Keep queue size bounded
            while len(self._queue) > self.max_size:
                heapq.heappop(self._queue)

    def get_top(self, n: int = 5) -> List[Suggestion]:
        """Get top n suggestions"""
        with self._lock:
            # Filter valid suggestions
            valid = [
                (p, c, s) for p, c, s in self._queue
                if s.is_valid()
            ]

            # Sort and return top n
            valid.sort()  # Already negative priority, so smallest first = highest priority
            return [s for _, _, s in valid[:n]]

    def clear_expired(self) -> int:
        """Remove expired suggestions"""
        with self._lock:
            original_size = len(self._queue)
            self._queue = [
                (p, c, s) for p, c, s in self._queue
                if s.is_valid()
            ]
            heapq.heapify(self._queue)
            return original_size - len(self._queue)


class AnticipationEngine:
    """
    Layer 5: Anticipation Engine

    Predicts user needs and provides proactive suggestions
    to improve developer experience and productivity.
    """

    def __init__(
        self,
        learning_core: Optional[Any] = None,
        context_engine: Optional[Any] = None
    ):
        """
        Initialize the anticipation engine

        Args:
            learning_core: Reference to Layer 4 for pattern data
            context_engine: Reference to Layer 2 for code context
        """
        self._learning_core = learning_core
        self._context_engine = context_engine

        # Predictors
        self.workflow_predictor = WorkflowPredictor()
        self.file_predictor = FilePredictor()
        self.issue_predictor = IssuePredictor()

        # Suggestion management
        self.suggestion_queue = SuggestionQueue()

        # State
        self._current_context = PredictionContext()
        self._lock = threading.Lock()

    def update_context(
        self,
        current_file: Optional[str] = None,
        recent_files: Optional[List[str]] = None,
        current_task: Optional[str] = None,
        error: Optional[str] = None,
        uncommitted_changes: Optional[bool] = None,
        tests_passing: Optional[bool] = None
    ) -> None:
        """Update the prediction context"""
        with self._lock:
            if current_file:
                # Record file access for predictions
                self.file_predictor.record_file_access(
                    current_file,
                    self._current_context.current_file
                )
                self._current_context.current_file = current_file

            if recent_files is not None:
                self._current_context.recent_files = recent_files[-20:]

            if current_task:
                self._current_context.recent_tasks.append(current_task)
                self._current_context.recent_tasks = self._current_context.recent_tasks[-20:]
                # Record for workflow prediction
                self.workflow_predictor.record_action(current_task)

            if error:
                self._current_context.recent_errors.append(error)
                self._current_context.recent_errors = self._current_context.recent_errors[-10:]

            if uncommitted_changes is not None:
                self._current_context.uncommitted_changes = uncommitted_changes

            if tests_passing is not None:
                self._current_context.tests_passing = tests_passing

            self._current_context.time_of_day = datetime.now().hour

    def predict_next_files(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Predict which files user will work with next"""
        if self._current_context.current_file:
            return self.file_predictor.predict_next_files(
                self._current_context.current_file,
                limit=limit
            )
        return []

    def predict_next_actions(self) -> List[Tuple[str, float]]:
        """Predict next likely actions"""
        if self._current_context.recent_tasks:
            current_task = self._current_context.recent_tasks[-1]
            return self.workflow_predictor.predict_next_action(current_task)
        return []

    def get_suggestions(self, limit: int = 5) -> List[Suggestion]:
        """Get top proactive suggestions"""
        # Generate new suggestions based on current context
        self._generate_suggestions()

        # Clean up expired suggestions
        self.suggestion_queue.clear_expired()

        return self.suggestion_queue.get_top(limit)

    def _generate_suggestions(self) -> None:
        """Generate new suggestions based on current context"""
        # File suggestions
        next_files = self.predict_next_files(limit=3)
        for file_path, confidence in next_files:
            if confidence > 0.3:
                self.suggestion_queue.add(Suggestion(
                    suggestion_type=SuggestionType.NEXT_FILE,
                    title=f"You might work on: {file_path.split('/')[-1]}",
                    description=f"Based on your workflow, you often edit this file next.",
                    confidence=confidence,
                    priority=int(confidence * 5),
                    action=f"/read {file_path}",
                    metadata={"file_path": file_path},
                    expires_at=datetime.now() + timedelta(minutes=30),
                ))

        # Issue suggestions
        issues = self.issue_predictor.predict_issues(context=self._current_context)
        for issue in issues:
            self.suggestion_queue.add(issue)

        # Workflow suggestions
        next_actions = self.predict_next_actions()
        for action, confidence in next_actions[:2]:
            if confidence > 0.4:
                self.suggestion_queue.add(Suggestion(
                    suggestion_type=SuggestionType.WORKFLOW_STEP,
                    title=f"Next step: {action}",
                    description="Based on your usual workflow pattern",
                    confidence=confidence,
                    priority=int(confidence * 4),
                    expires_at=datetime.now() + timedelta(minutes=15),
                ))

        # Context preload suggestions
        if self._context_engine and self._current_context.current_file:
            related = self.file_predictor.get_related_files(
                self._current_context.current_file
            )
            if related:
                self.suggestion_queue.add(Suggestion(
                    suggestion_type=SuggestionType.CONTEXT_PRELOAD,
                    title="Related files loaded",
                    description=f"Pre-loaded context for {len(related)} related files",
                    confidence=0.7,
                    priority=1,
                    metadata={"files": related[:5]},
                    expires_at=datetime.now() + timedelta(minutes=60),
                ))

    def get_smart_defaults(self, task_type: str) -> Dict[str, Any]:
        """Get smart defaults based on learned patterns"""
        defaults = {}

        # Default model based on task type and user preference
        if self._learning_core:
            recommended_model = self._learning_core.get_recommended_model(task_type)
            if recommended_model:
                defaults["model"] = recommended_model

        # Default based on time of day
        hour = datetime.now().hour
        if hour < 9 or hour > 21:
            # Outside work hours - maybe quicker responses preferred
            defaults["verbosity"] = "concise"
        else:
            defaults["verbosity"] = "normal"

        # Task-specific defaults
        if "debug" in task_type.lower():
            defaults["show_reasoning"] = True
            defaults["include_context"] = True
        elif "test" in task_type.lower():
            defaults["include_examples"] = True

        return defaults

    def preload_context(self) -> Dict[str, Any]:
        """Preload context for faster responses"""
        context = {
            "files": [],
            "patterns": [],
            "suggestions": [],
        }

        # Get likely next files
        next_files = self.predict_next_files(limit=3)
        context["files"] = [f[0] for f in next_files]

        # Get workflow patterns
        patterns = self.workflow_predictor.detect_patterns()
        context["patterns"] = [
            {"name": p.name, "steps": p.steps, "confidence": p.confidence}
            for p in patterns[:5]
        ]

        # Get current suggestions
        context["suggestions"] = [
            {
                "type": s.suggestion_type.value,
                "title": s.title,
                "confidence": s.confidence,
            }
            for s in self.get_suggestions(limit=3)
        ]

        return context

    def end_session(self) -> None:
        """End the current session"""
        self.workflow_predictor.end_sequence()

    def get_anticipation_summary(self) -> Dict[str, Any]:
        """Get a summary of anticipation state"""
        return {
            "current_file": self._current_context.current_file,
            "recent_files_count": len(self._current_context.recent_files),
            "recent_tasks_count": len(self._current_context.recent_tasks),
            "workflow_patterns": len(self.workflow_predictor._patterns),
            "pending_suggestions": len(self.suggestion_queue._queue),
            "next_file_predictions": self.predict_next_files(limit=3),
            "next_action_predictions": self.predict_next_actions()[:3],
        }


# Convenience functions
_anticipation_engine: Optional[AnticipationEngine] = None


def get_anticipation_engine(
    learning_core: Optional[Any] = None,
    context_engine: Optional[Any] = None
) -> AnticipationEngine:
    """Get or create the anticipation engine instance"""
    global _anticipation_engine
    if _anticipation_engine is None:
        _anticipation_engine = AnticipationEngine(
            learning_core=learning_core,
            context_engine=context_engine
        )
    return _anticipation_engine


def suggest_next() -> List[Suggestion]:
    """Get proactive suggestions for the user"""
    engine = get_anticipation_engine()
    return engine.get_suggestions(limit=5)
