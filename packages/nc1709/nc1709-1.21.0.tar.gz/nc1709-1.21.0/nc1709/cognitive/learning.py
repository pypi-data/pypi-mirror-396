"""
Layer 4: Learning Core

Learns from user patterns over time:
- Tracks user preferences (models, styles, workflows)
- Learns from successful and unsuccessful interactions
- Adapts responses based on past behavior
- Provides personalized suggestions
- Maintains privacy while learning

This layer answers: "What has NC1709 learned about this user?"
"""

import os
import json
import hashlib
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
from collections import Counter, defaultdict
import threading

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of user feedback"""
    ACCEPTED = "accepted"  # User accepted the suggestion
    REJECTED = "rejected"  # User rejected/undid the change
    MODIFIED = "modified"  # User modified the output
    IGNORED = "ignored"  # User didn't respond
    EXPLICIT_POSITIVE = "explicit_positive"  # User explicitly liked it
    EXPLICIT_NEGATIVE = "explicit_negative"  # User explicitly disliked it


class InteractionType(Enum):
    """Types of user interactions"""
    COMPLETION = "completion"
    AGENT_TASK = "agent_task"
    FILE_EDIT = "file_edit"
    CODE_GENERATION = "code_generation"
    EXPLANATION = "explanation"
    DEBUG_HELP = "debug_help"
    COMMAND = "command"
    SEARCH = "search"


@dataclass
class UserPreference:
    """A learned user preference"""
    key: str
    value: Any
    confidence: float  # 0.0 to 1.0
    observation_count: int
    last_updated: datetime = field(default_factory=datetime.now)
    category: str = "general"


@dataclass
class InteractionRecord:
    """Record of a user interaction"""
    interaction_id: str
    interaction_type: InteractionType
    timestamp: datetime
    task_category: str
    model_used: Optional[str]
    input_summary: str  # Hashed/summarized for privacy
    output_summary: str
    feedback: Optional[FeedbackType] = None
    duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PatternInsight:
    """An insight derived from usage patterns"""
    pattern_type: str
    description: str
    confidence: float
    evidence_count: int
    actionable_suggestion: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.now)


@dataclass
class UserProfile:
    """User profile with learned preferences and patterns"""
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    total_interactions: int = 0
    preferences: Dict[str, UserPreference] = field(default_factory=dict)
    patterns: List[PatternInsight] = field(default_factory=list)
    favorite_models: Dict[str, int] = field(default_factory=dict)
    task_distribution: Dict[str, int] = field(default_factory=dict)
    working_hours: Dict[int, int] = field(default_factory=dict)  # Hour -> count
    session_durations: List[int] = field(default_factory=list)  # In minutes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "total_interactions": self.total_interactions,
            "preferences": {k: asdict(v) for k, v in self.preferences.items()},
            "patterns": [asdict(p) for p in self.patterns],
            "favorite_models": self.favorite_models,
            "task_distribution": self.task_distribution,
            "working_hours": self.working_hours,
            "session_durations": self.session_durations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        """Create from dictionary"""
        profile = cls(user_id=data["user_id"])
        profile.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        profile.last_active = datetime.fromisoformat(data.get("last_active", datetime.now().isoformat()))
        profile.total_interactions = data.get("total_interactions", 0)
        profile.favorite_models = data.get("favorite_models", {})
        profile.task_distribution = data.get("task_distribution", {})
        profile.working_hours = {int(k): v for k, v in data.get("working_hours", {}).items()}
        profile.session_durations = data.get("session_durations", [])

        # Reconstruct preferences
        for key, pref_data in data.get("preferences", {}).items():
            pref_data["last_updated"] = datetime.fromisoformat(pref_data["last_updated"])
            profile.preferences[key] = UserPreference(**pref_data)

        # Reconstruct patterns
        for pattern_data in data.get("patterns", []):
            pattern_data["discovered_at"] = datetime.fromisoformat(pattern_data["discovered_at"])
            profile.patterns.append(PatternInsight(**pattern_data))

        return profile


class PreferenceLearner:
    """Learns user preferences from interactions"""

    # Preference keys
    PREF_CODE_STYLE = "code_style"
    PREF_VERBOSITY = "verbosity"
    PREF_EXPLANATION_DEPTH = "explanation_depth"
    PREF_MODEL = "preferred_model"
    PREF_LANGUAGE = "preferred_language"
    PREF_FRAMEWORK = "preferred_framework"
    PREF_AUTO_APPLY = "auto_apply_suggestions"
    PREF_COMMENT_STYLE = "comment_style"

    def __init__(self, min_observations: int = 3, confidence_threshold: float = 0.6):
        self.min_observations = min_observations
        self.confidence_threshold = confidence_threshold
        self._observation_buffer: Dict[str, List[Any]] = defaultdict(list)

    def observe(self, key: str, value: Any, weight: float = 1.0) -> None:
        """Record an observation for a preference"""
        self._observation_buffer[key].append((value, weight, datetime.now()))

    def learn_preference(self, key: str) -> Optional[UserPreference]:
        """Analyze observations and learn a preference"""
        observations = self._observation_buffer.get(key, [])

        if len(observations) < self.min_observations:
            return None

        # Count value occurrences with weights
        value_weights: Dict[Any, float] = defaultdict(float)
        total_weight = 0.0

        for value, weight, _ in observations:
            if isinstance(value, dict):
                value = json.dumps(value, sort_keys=True)
            value_weights[value] += weight
            total_weight += weight

        if total_weight == 0:
            return None

        # Find most common value
        best_value, best_weight = max(value_weights.items(), key=lambda x: x[1])
        confidence = best_weight / total_weight

        if confidence >= self.confidence_threshold:
            # Try to parse back if it was a dict
            try:
                if isinstance(best_value, str) and best_value.startswith('{'):
                    best_value = json.loads(best_value)
            except Exception:
                pass

            return UserPreference(
                key=key,
                value=best_value,
                confidence=confidence,
                observation_count=len(observations),
                category=self._categorize_preference(key),
            )

        return None

    def _categorize_preference(self, key: str) -> str:
        """Categorize a preference key"""
        if "model" in key:
            return "model"
        elif "style" in key or "format" in key:
            return "style"
        elif "language" in key or "framework" in key:
            return "tech"
        else:
            return "general"


class PatternAnalyzer:
    """Analyzes user behavior patterns"""

    def __init__(self):
        self._interaction_history: List[InteractionRecord] = []

    def add_interaction(self, record: InteractionRecord) -> None:
        """Add an interaction record"""
        self._interaction_history.append(record)
        # Keep last 1000 interactions
        if len(self._interaction_history) > 1000:
            self._interaction_history = self._interaction_history[-1000:]

    def analyze_patterns(self) -> List[PatternInsight]:
        """Analyze patterns from interaction history"""
        patterns = []

        if len(self._interaction_history) < 10:
            return patterns

        # Analyze time patterns
        time_pattern = self._analyze_time_patterns()
        if time_pattern:
            patterns.append(time_pattern)

        # Analyze task patterns
        task_pattern = self._analyze_task_patterns()
        if task_pattern:
            patterns.append(task_pattern)

        # Analyze model preferences
        model_pattern = self._analyze_model_patterns()
        if model_pattern:
            patterns.append(model_pattern)

        # Analyze feedback patterns
        feedback_pattern = self._analyze_feedback_patterns()
        if feedback_pattern:
            patterns.append(feedback_pattern)

        return patterns

    def _analyze_time_patterns(self) -> Optional[PatternInsight]:
        """Analyze when user is most active"""
        if not self._interaction_history:
            return None

        hour_counts = Counter(r.timestamp.hour for r in self._interaction_history)
        if not hour_counts:
            return None

        peak_hour, count = hour_counts.most_common(1)[0]
        total = sum(hour_counts.values())
        confidence = count / total if total > 0 else 0

        # Check if there's a clear peak
        if confidence > 0.15:  # At least 15% of activity in one hour
            # Determine time of day
            if 5 <= peak_hour < 12:
                time_period = "morning"
            elif 12 <= peak_hour < 17:
                time_period = "afternoon"
            elif 17 <= peak_hour < 21:
                time_period = "evening"
            else:
                time_period = "night"

            return PatternInsight(
                pattern_type="time_preference",
                description=f"User is most active in the {time_period} (peak at {peak_hour}:00)",
                confidence=confidence,
                evidence_count=count,
                actionable_suggestion=f"Schedule complex tasks during {time_period} for best results",
            )

        return None

    def _analyze_task_patterns(self) -> Optional[PatternInsight]:
        """Analyze what types of tasks user does most"""
        if not self._interaction_history:
            return None

        task_counts = Counter(r.task_category for r in self._interaction_history)
        if not task_counts:
            return None

        top_task, count = task_counts.most_common(1)[0]
        total = sum(task_counts.values())
        confidence = count / total if total > 0 else 0

        if confidence > 0.2:
            return PatternInsight(
                pattern_type="task_preference",
                description=f"User frequently works on {top_task} tasks ({count} of {total})",
                confidence=confidence,
                evidence_count=count,
                actionable_suggestion=f"Optimize for {top_task} workflows",
            )

        return None

    def _analyze_model_patterns(self) -> Optional[PatternInsight]:
        """Analyze model usage patterns"""
        model_counts = Counter(
            r.model_used for r in self._interaction_history
            if r.model_used
        )
        if not model_counts:
            return None

        top_model, count = model_counts.most_common(1)[0]
        total = sum(model_counts.values())
        confidence = count / total if total > 0 else 0

        if confidence > 0.3:
            return PatternInsight(
                pattern_type="model_preference",
                description=f"User prefers {top_model} ({int(confidence * 100)}% of usage)",
                confidence=confidence,
                evidence_count=count,
                actionable_suggestion=f"Default to {top_model} for similar tasks",
            )

        return None

    def _analyze_feedback_patterns(self) -> Optional[PatternInsight]:
        """Analyze feedback patterns"""
        feedback_counts = Counter(
            r.feedback for r in self._interaction_history
            if r.feedback
        )
        if not feedback_counts:
            return None

        total = sum(feedback_counts.values())
        accepted = feedback_counts.get(FeedbackType.ACCEPTED, 0)
        rejected = feedback_counts.get(FeedbackType.REJECTED, 0)
        modified = feedback_counts.get(FeedbackType.MODIFIED, 0)

        acceptance_rate = accepted / total if total > 0 else 0
        modification_rate = modified / total if total > 0 else 0

        if acceptance_rate > 0.7:
            return PatternInsight(
                pattern_type="satisfaction",
                description=f"High acceptance rate ({int(acceptance_rate * 100)}%)",
                confidence=acceptance_rate,
                evidence_count=accepted,
            )
        elif modification_rate > 0.4:
            return PatternInsight(
                pattern_type="customization_needed",
                description=f"User often modifies outputs ({int(modification_rate * 100)}%)",
                confidence=modification_rate,
                evidence_count=modified,
                actionable_suggestion="Consider asking for more preferences upfront",
            )

        return None


class LearningCore:
    """
    Layer 4: Learning Core

    Learns from user patterns over time to provide
    personalized and adaptive assistance.
    """

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        user_id: Optional[str] = None,
        anonymize: bool = True
    ):
        """
        Initialize learning core

        Args:
            data_dir: Directory to store learning data
            user_id: User identifier (generated if not provided)
            anonymize: Whether to anonymize stored data
        """
        self.data_dir = data_dir or Path.home() / ".nc1709" / "learning"
        self.anonymize = anonymize
        self._lock = threading.Lock()

        # Initialize or load user profile
        self.user_id = user_id or self._get_or_create_user_id()
        self.profile = self._load_profile()

        # Initialize components
        self.preference_learner = PreferenceLearner()
        self.pattern_analyzer = PatternAnalyzer()

        # Session tracking
        self._session_start = datetime.now()
        self._session_interactions = 0

    def _get_or_create_user_id(self) -> str:
        """Get or create a stable user ID"""
        id_file = self.data_dir / "user_id"

        if id_file.exists():
            return id_file.read_text().strip()

        # Generate new ID
        import uuid
        user_id = f"user_{uuid.uuid4().hex[:12]}"

        # Save it
        self.data_dir.mkdir(parents=True, exist_ok=True)
        id_file.write_text(user_id)

        return user_id

    def _load_profile(self) -> UserProfile:
        """Load user profile from disk"""
        profile_file = self.data_dir / f"{self.user_id}_profile.json"

        if profile_file.exists():
            try:
                with open(profile_file) as f:
                    data = json.load(f)
                return UserProfile.from_dict(data)
            except Exception as e:
                logger.warning(f"Error loading profile: {e}")

        return UserProfile(user_id=self.user_id)

    def _save_profile(self) -> None:
        """Save user profile to disk"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            profile_file = self.data_dir / f"{self.user_id}_profile.json"

            with open(profile_file, "w") as f:
                json.dump(self.profile.to_dict(), f, indent=2, default=str)

        except Exception as e:
            logger.warning(f"Error saving profile: {e}")

    def _hash_content(self, content: str) -> str:
        """Hash content for privacy"""
        if not self.anonymize:
            return content[:200]  # Truncate instead
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def record_interaction(
        self,
        interaction_type: InteractionType,
        task_category: str,
        input_text: str,
        output_text: str,
        model_used: Optional[str] = None,
        duration_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a user interaction

        Args:
            interaction_type: Type of interaction
            task_category: Category of the task
            input_text: User input (will be hashed if anonymize=True)
            output_text: AI output (will be hashed if anonymize=True)
            model_used: Model that was used
            duration_ms: Duration in milliseconds
            tokens_used: Tokens consumed
            metadata: Additional metadata

        Returns:
            Interaction ID
        """
        import uuid

        interaction_id = f"int_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

        record = InteractionRecord(
            interaction_id=interaction_id,
            interaction_type=interaction_type,
            timestamp=datetime.now(),
            task_category=task_category,
            model_used=model_used,
            input_summary=self._hash_content(input_text),
            output_summary=self._hash_content(output_text),
            duration_ms=duration_ms,
            tokens_used=tokens_used,
            metadata=metadata or {},
        )

        with self._lock:
            # Update pattern analyzer
            self.pattern_analyzer.add_interaction(record)

            # Update profile stats
            self.profile.total_interactions += 1
            self.profile.last_active = datetime.now()

            # Track model usage
            if model_used:
                self.profile.favorite_models[model_used] = \
                    self.profile.favorite_models.get(model_used, 0) + 1

            # Track task distribution
            self.profile.task_distribution[task_category] = \
                self.profile.task_distribution.get(task_category, 0) + 1

            # Track working hours
            hour = datetime.now().hour
            self.profile.working_hours[hour] = \
                self.profile.working_hours.get(hour, 0) + 1

            # Learn preferences from model choice
            if model_used:
                self.preference_learner.observe(
                    PreferenceLearner.PREF_MODEL,
                    model_used,
                    weight=1.0
                )

            self._session_interactions += 1

        return interaction_id

    def record_feedback(
        self,
        interaction_id: str,
        feedback: FeedbackType,
        details: Optional[str] = None
    ) -> None:
        """
        Record feedback for an interaction

        Args:
            interaction_id: ID of the interaction
            feedback: Type of feedback
            details: Optional details
        """
        with self._lock:
            # Find and update the interaction in pattern analyzer
            for record in self.pattern_analyzer._interaction_history:
                if record.interaction_id == interaction_id:
                    record.feedback = feedback
                    if details:
                        record.metadata["feedback_details"] = self._hash_content(details)
                    break

            # Learn from feedback
            if feedback == FeedbackType.ACCEPTED:
                self.preference_learner.observe("satisfaction", 1.0, weight=1.0)
            elif feedback == FeedbackType.REJECTED:
                self.preference_learner.observe("satisfaction", 0.0, weight=1.0)
            elif feedback == FeedbackType.MODIFIED:
                self.preference_learner.observe("needs_customization", 1.0, weight=0.5)

    def observe_preference(
        self,
        key: str,
        value: Any,
        weight: float = 1.0
    ) -> None:
        """
        Observe a user preference

        Args:
            key: Preference key
            value: Observed value
            weight: Weight of this observation
        """
        with self._lock:
            self.preference_learner.observe(key, value, weight)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a learned preference

        Args:
            key: Preference key
            default: Default value if not learned

        Returns:
            Learned preference value or default
        """
        with self._lock:
            if key in self.profile.preferences:
                pref = self.profile.preferences[key]
                if pref.confidence >= 0.6:
                    return pref.value

            # Try to learn it now
            learned = self.preference_learner.learn_preference(key)
            if learned:
                self.profile.preferences[key] = learned
                return learned.value

        return default

    def get_all_preferences(self) -> Dict[str, UserPreference]:
        """Get all learned preferences"""
        with self._lock:
            # Update with any newly learned preferences
            for key in list(self.preference_learner._observation_buffer.keys()):
                if key not in self.profile.preferences:
                    learned = self.preference_learner.learn_preference(key)
                    if learned:
                        self.profile.preferences[key] = learned

            return self.profile.preferences.copy()

    def analyze_patterns(self) -> List[PatternInsight]:
        """Analyze and return usage patterns"""
        with self._lock:
            patterns = self.pattern_analyzer.analyze_patterns()
            self.profile.patterns = patterns
            return patterns

    def get_recommended_model(self, task_category: str) -> Optional[str]:
        """
        Get recommended model for a task based on learning

        Args:
            task_category: Category of the task

        Returns:
            Recommended model or None
        """
        # Check explicit preference
        preferred = self.get_preference(PreferenceLearner.PREF_MODEL)
        if preferred:
            return preferred

        # Check most successful model for this task type
        with self._lock:
            # Get successful interactions for this task type
            successful = [
                r for r in self.pattern_analyzer._interaction_history
                if r.task_category == task_category
                and r.feedback == FeedbackType.ACCEPTED
                and r.model_used
            ]

            if successful:
                model_counts = Counter(r.model_used for r in successful)
                return model_counts.most_common(1)[0][0]

            # Fall back to overall favorite
            if self.profile.favorite_models:
                return max(self.profile.favorite_models, key=self.profile.favorite_models.get)

        return None

    def get_user_summary(self) -> Dict[str, Any]:
        """Get a summary of learned user behavior"""
        with self._lock:
            patterns = self.analyze_patterns()

            # Calculate session stats
            session_duration = (datetime.now() - self._session_start).total_seconds() / 60

            summary = {
                "user_id": self.user_id,
                "total_interactions": self.profile.total_interactions,
                "session_interactions": self._session_interactions,
                "session_duration_minutes": round(session_duration, 1),
                "favorite_model": max(self.profile.favorite_models, key=self.profile.favorite_models.get)
                    if self.profile.favorite_models else None,
                "top_task_type": max(self.profile.task_distribution, key=self.profile.task_distribution.get)
                    if self.profile.task_distribution else None,
                "peak_hour": max(self.profile.working_hours, key=self.profile.working_hours.get)
                    if self.profile.working_hours else None,
                "preferences": {
                    k: {"value": p.value, "confidence": p.confidence}
                    for k, p in self.profile.preferences.items()
                },
                "insights": [
                    {"type": p.pattern_type, "description": p.description, "suggestion": p.actionable_suggestion}
                    for p in patterns
                ],
            }

            return summary

    def end_session(self) -> None:
        """End the current session and save data"""
        with self._lock:
            # Record session duration
            duration_minutes = int((datetime.now() - self._session_start).total_seconds() / 60)
            self.profile.session_durations.append(duration_minutes)

            # Keep last 100 session durations
            if len(self.profile.session_durations) > 100:
                self.profile.session_durations = self.profile.session_durations[-100:]

            # Update patterns
            self.profile.patterns = self.pattern_analyzer.analyze_patterns()

            # Save profile
            self._save_profile()

        logger.info(f"Session ended: {self._session_interactions} interactions, {duration_minutes} minutes")

    def reset(self) -> None:
        """Reset all learned data (use with caution)"""
        with self._lock:
            self.profile = UserProfile(user_id=self.user_id)
            self.preference_learner = PreferenceLearner()
            self.pattern_analyzer = PatternAnalyzer()
            self._save_profile()

        logger.info("Learning data reset")


# Convenience functions
_learning_core: Optional[LearningCore] = None


def get_learning_core(data_dir: Optional[Path] = None) -> LearningCore:
    """Get or create the learning core instance"""
    global _learning_core
    if _learning_core is None:
        _learning_core = LearningCore(data_dir=data_dir)
    return _learning_core


def record_interaction(
    interaction_type: str,
    task_category: str,
    input_text: str,
    output_text: str,
    **kwargs
) -> str:
    """Quick helper to record an interaction"""
    core = get_learning_core()
    int_type = InteractionType(interaction_type) if isinstance(interaction_type, str) else interaction_type
    return core.record_interaction(
        interaction_type=int_type,
        task_category=task_category,
        input_text=input_text,
        output_text=output_text,
        **kwargs
    )
