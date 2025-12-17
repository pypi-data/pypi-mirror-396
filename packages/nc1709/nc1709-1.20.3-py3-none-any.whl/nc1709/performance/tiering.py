"""
NC1709 Performance - Smart Model Tiering

Routes requests to the smallest model capable of handling them.
Dramatically reduces latency for simple queries while maintaining
quality for complex tasks.

Tiers:
- Tier 1: Instant (3B) - Simple questions, quick answers (~300ms)
- Tier 2: Fast (7B) - Standard coding tasks (~1-2s)
- Tier 3: Smart (32B) - Complex tasks (~3-5s)
- Tier 4: Council - Multi-agent for very complex tasks (~10s+)

Integration with Model Registry:
- Uses nc1709.models to get model names and specs
- Falls back to hardcoded defaults if registry not available
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


def _get_model_from_registry(task: str, default: str) -> str:
    """
    Get model name from registry, with fallback.

    Args:
        task: Task name (instant, fast, coding, etc.)
        default: Default model if registry unavailable

    Returns:
        Model name in ollama/name format
    """
    try:
        from nc1709.models import get_best_model_for_task, get_model_spec

        # Try to get best model for task
        spec = get_best_model_for_task(task)
        if spec:
            return f"ollama/{spec.ollama_name}"

        # Fallback to default
        return default
    except ImportError:
        # Registry not available
        return default


class ModelTier(Enum):
    """Model tiers by capability/speed trade-off"""
    INSTANT = "instant"  # Tier 1: 3B models
    FAST = "fast"        # Tier 2: 7B models
    SMART = "smart"      # Tier 3: 32B models
    COUNCIL = "council"  # Tier 4: Multi-agent

    @property
    def level(self) -> int:
        """Numeric level for comparison"""
        return {
            ModelTier.INSTANT: 1,
            ModelTier.FAST: 2,
            ModelTier.SMART: 3,
            ModelTier.COUNCIL: 4,
        }[self]


@dataclass
class TierConfig:
    """Configuration for a model tier"""
    model: str
    max_tokens: int
    timeout_seconds: int
    cost_factor: float  # Relative cost (1.0 = baseline)

    # Task types this tier can handle
    supported_complexity: float  # Max complexity (0.0-1.0)
    supported_categories: List[str]


@dataclass
class TieringDecision:
    """Result of tiering decision"""
    tier: ModelTier
    model: str
    reasoning: str
    confidence: float
    fallback_tier: Optional[ModelTier] = None
    fallback_model: Optional[str] = None
    estimated_latency_ms: int = 0


@dataclass
class TieringStats:
    """Statistics for model tiering"""
    tier_usage: Dict[str, int] = field(default_factory=lambda: {
        "instant": 0,
        "fast": 0,
        "smart": 0,
        "council": 0,
    })
    tier_success: Dict[str, int] = field(default_factory=lambda: {
        "instant": 0,
        "fast": 0,
        "smart": 0,
        "council": 0,
    })
    escalations: int = 0  # Times we had to escalate to higher tier
    total_latency_saved_ms: float = 0

    def record_usage(self, tier: ModelTier, success: bool = True):
        """Record tier usage"""
        self.tier_usage[tier.value] += 1
        if success:
            self.tier_success[tier.value] += 1

    def record_escalation(self):
        """Record when we escalated to higher tier"""
        self.escalations += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier_usage": self.tier_usage,
            "tier_success": self.tier_success,
            "escalations": self.escalations,
            "total_latency_saved_ms": round(self.total_latency_saved_ms, 2),
            "success_rates": {
                tier: (self.tier_success[tier] / self.tier_usage[tier] * 100)
                if self.tier_usage[tier] > 0 else 0
                for tier in self.tier_usage
            }
        }


# Default tier configurations
# Models are retrieved from the registry when available
def _build_default_tiers() -> Dict[ModelTier, TierConfig]:
    """Build default tier configurations using registry when available"""
    return {
        ModelTier.INSTANT: TierConfig(
            model=_get_model_from_registry("instant", "ollama/qwen2.5-coder:32b"),
            max_tokens=500,
            timeout_seconds=10,
            cost_factor=0.1,
            supported_complexity=0.3,
            supported_categories=[
                "quick_answer",
                "explanation",  # Simple explanations
            ],
        ),
        ModelTier.FAST: TierConfig(
            model=_get_model_from_registry("fast", "ollama/qwen2.5-coder:7b"),
            max_tokens=2000,
            timeout_seconds=30,
            cost_factor=0.3,
            supported_complexity=0.5,
            supported_categories=[
                "quick_answer",
                "explanation",
                "code_generation",  # Simple code
                "code_modification",  # Simple edits
                "documentation",
                "file_operations",
                "git_operations",
            ],
        ),
        ModelTier.SMART: TierConfig(
            model=_get_model_from_registry("coding", "ollama/qwen2.5-coder:32b"),
            max_tokens=4000,
            timeout_seconds=120,
            cost_factor=1.0,
            supported_complexity=0.8,
            supported_categories=[
                # All categories
                "quick_answer", "explanation", "code_generation",
                "code_modification", "code_review", "refactoring",
                "testing", "documentation", "debugging",
                "devops", "database", "file_operations",
                "git_operations", "project_setup", "command_execution",
            ],
        ),
        ModelTier.COUNCIL: TierConfig(
            model="council",  # Special: triggers multi-agent
            max_tokens=8000,
            timeout_seconds=300,
            cost_factor=3.0,
            supported_complexity=1.0,
            supported_categories=[
                # Complex tasks
                "reasoning", "security", "performance",
                "architecture",
            ],
        ),
    }


# Build tiers at module load time
DEFAULT_TIERS: Dict[ModelTier, TierConfig] = _build_default_tiers()

# Categories that always need higher tiers
HIGH_COMPLEXITY_CATEGORIES = {
    "reasoning",
    "security",
    "performance",
    "debugging",  # Complex debugging
}

# Categories that can use lower tiers
LOW_COMPLEXITY_CATEGORIES = {
    "quick_answer",
    "explanation",
    "documentation",
    "file_operations",
    "git_operations",
}

# Keywords suggesting complexity
COMPLEXITY_KEYWORDS = {
    "high": [
        "architect", "design", "security", "vulnerability", "optimize",
        "performance", "complex", "refactor entire", "redesign",
        "distributed", "microservice", "concurrency", "race condition",
        "memory leak", "deadlock",
    ],
    "medium": [
        "implement", "create", "build", "add feature", "integrate",
        "test", "debug", "fix bug", "refactor",
    ],
    "low": [
        "explain", "what is", "how to", "simple", "quick",
        "list", "show", "display", "print", "hello world",
    ],
}


class TieredModelOrchestrator:
    """
    Intelligent model tier selection.

    Analyzes requests and routes to the optimal model tier based on:
    - Task complexity
    - Task category
    - Prompt characteristics
    - Historical performance

    Usage:
        orchestrator = TieredModelOrchestrator()

        decision = orchestrator.select_tier(
            prompt="explain what a decorator is",
            category="explanation",
            complexity=0.3
        )

        print(f"Using {decision.model} ({decision.tier.value})")
    """

    def __init__(
        self,
        tiers: Optional[Dict[ModelTier, TierConfig]] = None,
        enable_escalation: bool = True,
        conservative: bool = False  # If True, prefer higher tiers
    ):
        self.tiers = tiers or DEFAULT_TIERS
        self.enable_escalation = enable_escalation
        self.conservative = conservative
        self.stats = TieringStats()

        # Model availability cache
        self._available_models: Dict[str, bool] = {}

    def select_tier(
        self,
        prompt: str,
        category: Optional[str] = None,
        complexity: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        force_tier: Optional[ModelTier] = None
    ) -> TieringDecision:
        """
        Select the optimal model tier for a request.

        Args:
            prompt: User's prompt
            category: Task category from intent analysis
            complexity: Complexity score (0.0-1.0) from intent analysis
            context: Additional context
            force_tier: Force a specific tier (for testing)

        Returns:
            TieringDecision with model and reasoning
        """
        # Force tier if specified
        if force_tier:
            config = self.tiers[force_tier]
            return TieringDecision(
                tier=force_tier,
                model=config.model,
                reasoning="Forced tier selection",
                confidence=1.0,
                estimated_latency_ms=self._estimate_latency(force_tier),
            )

        # Estimate complexity if not provided
        if complexity is None:
            complexity = self._estimate_complexity(prompt, category)

        # Determine minimum tier needed
        selected_tier = self._determine_tier(prompt, category, complexity)

        # Apply conservative mode
        if self.conservative and selected_tier.level < ModelTier.SMART.level:
            selected_tier = ModelTier(min(selected_tier.level + 1, 3))

        config = self.tiers[selected_tier]

        # Determine fallback
        fallback_tier = None
        fallback_model = None
        if selected_tier.level < ModelTier.COUNCIL.level:
            fallback_tier = ModelTier.SMART
            fallback_model = self.tiers[ModelTier.SMART].model

        decision = TieringDecision(
            tier=selected_tier,
            model=config.model,
            reasoning=self._generate_reasoning(selected_tier, category, complexity),
            confidence=self._calculate_confidence(selected_tier, complexity),
            fallback_tier=fallback_tier,
            fallback_model=fallback_model,
            estimated_latency_ms=self._estimate_latency(selected_tier),
        )

        logger.debug(f"Tier decision: {decision.tier.value} ({decision.reasoning})")
        return decision

    def _determine_tier(
        self,
        prompt: str,
        category: Optional[str],
        complexity: float
    ) -> ModelTier:
        """Determine the appropriate tier"""
        prompt_lower = prompt.lower()

        # Check for high complexity keywords
        for keyword in COMPLEXITY_KEYWORDS["high"]:
            if keyword in prompt_lower:
                return ModelTier.COUNCIL if complexity > 0.8 else ModelTier.SMART

        # Check category requirements
        if category in HIGH_COMPLEXITY_CATEGORIES:
            return ModelTier.SMART if complexity < 0.8 else ModelTier.COUNCIL

        # Check for low complexity scenarios
        if category in LOW_COMPLEXITY_CATEGORIES and complexity < 0.4:
            # Check prompt length - very short prompts can use instant
            if len(prompt.split()) < 20:
                return ModelTier.INSTANT
            return ModelTier.FAST

        # Medium complexity keywords
        for keyword in COMPLEXITY_KEYWORDS["medium"]:
            if keyword in prompt_lower:
                return ModelTier.FAST if complexity < 0.6 else ModelTier.SMART

        # Low complexity keywords
        for keyword in COMPLEXITY_KEYWORDS["low"]:
            if keyword in prompt_lower:
                return ModelTier.INSTANT if complexity < 0.3 else ModelTier.FAST

        # Default based on complexity score
        if complexity < 0.3:
            return ModelTier.INSTANT
        elif complexity < 0.5:
            return ModelTier.FAST
        elif complexity < 0.8:
            return ModelTier.SMART
        else:
            return ModelTier.COUNCIL

    def _estimate_complexity(
        self,
        prompt: str,
        category: Optional[str]
    ) -> float:
        """Estimate complexity when not provided by intent analyzer"""
        score = 0.5  # Default medium

        prompt_lower = prompt.lower()

        # Adjust by keywords
        for keyword in COMPLEXITY_KEYWORDS["high"]:
            if keyword in prompt_lower:
                score += 0.15

        for keyword in COMPLEXITY_KEYWORDS["low"]:
            if keyword in prompt_lower:
                score -= 0.15

        # Adjust by prompt length
        word_count = len(prompt.split())
        if word_count > 100:
            score += 0.2
        elif word_count < 10:
            score -= 0.2

        # Adjust by category
        if category in HIGH_COMPLEXITY_CATEGORIES:
            score += 0.2
        elif category in LOW_COMPLEXITY_CATEGORIES:
            score -= 0.2

        return max(0.0, min(1.0, score))

    def _generate_reasoning(
        self,
        tier: ModelTier,
        category: Optional[str],
        complexity: float
    ) -> str:
        """Generate human-readable reasoning"""
        reasons = []

        if tier == ModelTier.INSTANT:
            reasons.append("Simple query")
            if complexity < 0.3:
                reasons.append(f"low complexity ({complexity:.2f})")
        elif tier == ModelTier.FAST:
            reasons.append("Standard task")
            if category:
                reasons.append(f"category: {category}")
        elif tier == ModelTier.SMART:
            reasons.append("Complex task")
            if complexity > 0.6:
                reasons.append(f"high complexity ({complexity:.2f})")
        else:  # COUNCIL
            reasons.append("Very complex task requiring multi-agent")
            if complexity > 0.8:
                reasons.append(f"very high complexity ({complexity:.2f})")

        return "; ".join(reasons)

    def _calculate_confidence(self, tier: ModelTier, complexity: float) -> float:
        """Calculate confidence in tier selection"""
        # Higher confidence when complexity clearly matches tier
        tier_ranges = {
            ModelTier.INSTANT: (0.0, 0.3),
            ModelTier.FAST: (0.3, 0.5),
            ModelTier.SMART: (0.5, 0.8),
            ModelTier.COUNCIL: (0.8, 1.0),
        }

        low, high = tier_ranges[tier]
        if low <= complexity <= high:
            return 0.9  # High confidence
        elif abs(complexity - (low + high) / 2) < 0.2:
            return 0.75  # Medium confidence
        else:
            return 0.6  # Lower confidence

    def _estimate_latency(self, tier: ModelTier) -> int:
        """Estimate latency in milliseconds"""
        latencies = {
            ModelTier.INSTANT: 300,
            ModelTier.FAST: 1500,
            ModelTier.SMART: 4000,
            ModelTier.COUNCIL: 15000,
        }
        return latencies.get(tier, 5000)

    def record_result(
        self,
        tier: ModelTier,
        success: bool,
        actual_latency_ms: Optional[int] = None
    ) -> None:
        """Record the result of using a tier"""
        self.stats.record_usage(tier, success)

        if not success and self.enable_escalation:
            self.stats.record_escalation()

        # Track latency savings
        if actual_latency_ms and tier != ModelTier.SMART:
            # Compare to what SMART tier would have taken
            expected_smart = self._estimate_latency(ModelTier.SMART)
            if actual_latency_ms < expected_smart:
                self.stats.total_latency_saved_ms += expected_smart - actual_latency_ms

    def escalate(self, current_tier: ModelTier) -> Optional[TieringDecision]:
        """Escalate to next higher tier"""
        if current_tier.level >= ModelTier.COUNCIL.level:
            return None  # Can't escalate further

        next_tier = {
            ModelTier.INSTANT: ModelTier.FAST,
            ModelTier.FAST: ModelTier.SMART,
            ModelTier.SMART: ModelTier.COUNCIL,
        }[current_tier]

        self.stats.record_escalation()
        config = self.tiers[next_tier]

        return TieringDecision(
            tier=next_tier,
            model=config.model,
            reasoning=f"Escalated from {current_tier.value}",
            confidence=0.8,
            estimated_latency_ms=self._estimate_latency(next_tier),
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get tiering statistics"""
        return self.stats.to_dict()

    def get_tier_config(self, tier: ModelTier) -> TierConfig:
        """Get configuration for a tier"""
        return self.tiers[tier]


# Singleton instance
_orchestrator: Optional[TieredModelOrchestrator] = None


def get_orchestrator(**kwargs) -> TieredModelOrchestrator:
    """Get or create the global orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TieredModelOrchestrator(**kwargs)
    return _orchestrator


def quick_tier(
    prompt: str,
    category: Optional[str] = None,
    complexity: Optional[float] = None
) -> TieringDecision:
    """Quick helper for tier selection"""
    return get_orchestrator().select_tier(prompt, category, complexity)
