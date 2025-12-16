"""
NC1709 Cognitive Architecture

A 5-layer cognitive system that provides:
- Layer 1: Intelligent Router - LLM-powered intent analysis and routing
- Layer 2: Deep Context Engine - Semantic understanding of codebase
- Layer 3: Multi-Agent Council - Multiple AI experts collaborate
- Layer 4: Learning Core - Learns user patterns over time
- Layer 5: Anticipation Engine - Predicts needs before asked

This architecture is what differentiates NC1709 from other AI coding tools.
"""

from .router import (
    TaskCategory,
    IntentAnalysis,
    RoutingDecision,
    IntentAnalyzer,
    IntelligentRouter,
    quick_route,
)

from .context_engine import (
    NodeType,
    CodeNode,
    CodePattern,
    FileContext,
    ContextBudget,
    CodeGraphBuilder,
    PatternDetector,
    SemanticIndex,
    DeepContextEngine,
    get_context_engine,
    quick_context,
)

from .council import (
    AgentRole,
    AgentPersona,
    AgentResponse,
    CouncilSession,
    AgentSelector,
    ConsensusBuilder,
    MultiAgentCouncil,
    DEFAULT_AGENTS,
    get_council,
    quick_council,
)

from .learning import (
    FeedbackType,
    InteractionType,
    UserPreference,
    InteractionRecord,
    PatternInsight,
    UserProfile,
    PreferenceLearner,
    PatternAnalyzer,
    LearningCore,
    get_learning_core,
    record_interaction,
)

from .anticipation import (
    SuggestionType,
    Suggestion,
    WorkflowPattern,
    PredictionContext,
    WorkflowPredictor,
    FilePredictor,
    IssuePredictor,
    SuggestionQueue,
    AnticipationEngine,
    get_anticipation_engine,
    suggest_next,
)

from .system import (
    CognitiveRequest,
    CognitiveResponse,
    CognitiveSystem,
    get_cognitive_system,
    quick_cognitive,
)

__all__ = [
    # Layer 1: Router
    "TaskCategory",
    "IntentAnalysis",
    "RoutingDecision",
    "IntentAnalyzer",
    "IntelligentRouter",
    "quick_route",
    # Layer 2: Context Engine
    "NodeType",
    "CodeNode",
    "CodePattern",
    "FileContext",
    "ContextBudget",
    "CodeGraphBuilder",
    "PatternDetector",
    "SemanticIndex",
    "DeepContextEngine",
    "get_context_engine",
    "quick_context",
    # Layer 3: Multi-Agent Council
    "AgentRole",
    "AgentPersona",
    "AgentResponse",
    "CouncilSession",
    "AgentSelector",
    "ConsensusBuilder",
    "MultiAgentCouncil",
    "DEFAULT_AGENTS",
    "get_council",
    "quick_council",
    # Layer 4: Learning Core
    "FeedbackType",
    "InteractionType",
    "UserPreference",
    "InteractionRecord",
    "PatternInsight",
    "UserProfile",
    "PreferenceLearner",
    "PatternAnalyzer",
    "LearningCore",
    "get_learning_core",
    "record_interaction",
    # Layer 5: Anticipation Engine
    "SuggestionType",
    "Suggestion",
    "WorkflowPattern",
    "PredictionContext",
    "WorkflowPredictor",
    "FilePredictor",
    "IssuePredictor",
    "SuggestionQueue",
    "AnticipationEngine",
    "get_anticipation_engine",
    "suggest_next",
    # CognitiveSystem Orchestrator
    "CognitiveRequest",
    "CognitiveResponse",
    "CognitiveSystem",
    "get_cognitive_system",
    "quick_cognitive",
]

__version__ = "0.1.0"
