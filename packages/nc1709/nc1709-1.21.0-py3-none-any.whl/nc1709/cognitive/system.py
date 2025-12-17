"""
CognitiveSystem - The unified orchestrator for NC1709's cognitive architecture

This class integrates all 5 layers:
- Layer 1: Intelligent Router
- Layer 2: Deep Context Engine
- Layer 3: Multi-Agent Council
- Layer 4: Learning Core
- Layer 5: Anticipation Engine

Plus the Performance Optimization stack:
- Multi-level caching (L1/L2/L3)
- Smart model tiering
- Parallel processing pipeline

The CognitiveSystem is the main entry point for intelligent request processing.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class CognitiveRequest:
    """A request to the cognitive system"""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    target_files: Optional[List[str]] = None
    force_council: bool = False  # Force council convene even for simple tasks
    force_no_cache: bool = False  # Skip cache lookup
    stream: bool = False
    user_preferences: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CognitiveResponse:
    """Response from the cognitive system"""
    content: str
    model_used: str
    category: str
    complexity: float
    council_used: bool = False
    council_agents: Optional[List[str]] = None
    suggestions: Optional[List[Dict[str, Any]]] = None
    context_summary: Optional[str] = None
    processing_time_ms: Optional[int] = None
    cache_hit: bool = False
    cache_level: Optional[str] = None  # "L1", "L2", "L3"
    tier_used: Optional[str] = None  # "instant", "fast", "smart", "council"
    metadata: Dict[str, Any] = field(default_factory=dict)


class CognitiveSystem:
    """
    NC1709 Cognitive System

    The brain of NC1709 - orchestrates all 5 cognitive layers to provide
    intelligent, personalized, and proactive assistance.

    Flow:
    1. Request comes in
    2. Layer 1 (Router) analyzes intent and routes to appropriate model
    3. Layer 2 (Context) provides relevant codebase context
    4. Layer 3 (Council) convenes for complex tasks
    5. Layer 4 (Learning) records interaction and updates preferences
    6. Layer 5 (Anticipation) generates proactive suggestions

    Example:
        system = CognitiveSystem(llm_adapter=adapter)
        response = system.process("fix the authentication bug in login.py")
        print(response.content)
        print(f"Used model: {response.model_used}")
        print(f"Council used: {response.council_used}")
        for suggestion in response.suggestions:
            print(f"Suggestion: {suggestion['title']}")
    """

    def __init__(
        self,
        llm_adapter: Optional[Any] = None,
        project_root: Optional[Path] = None,
        learning_data_dir: Optional[Path] = None,
        council_threshold: float = 0.75,
        enable_anticipation: bool = True,
        enable_learning: bool = True,
        enable_cache: bool = True,
        enable_tiering: bool = True,
    ):
        """
        Initialize the cognitive system

        Args:
            llm_adapter: LLM adapter for model completions
            project_root: Root directory of the project for context
            learning_data_dir: Directory for storing learning data
            council_threshold: Complexity threshold for council convene
            enable_anticipation: Enable proactive suggestions
            enable_learning: Enable learning from interactions
            enable_cache: Enable multi-level caching
            enable_tiering: Enable smart model tiering
        """
        self._llm_adapter = llm_adapter
        self.project_root = project_root or Path.cwd()
        self.council_threshold = council_threshold
        self.enable_anticipation = enable_anticipation
        self.enable_learning = enable_learning
        self.enable_cache = enable_cache
        self.enable_tiering = enable_tiering

        # Initialize layers (lazy loading)
        self._router = None
        self._context_engine = None
        self._council = None
        self._learning_core = None
        self._anticipation_engine = None

        # Performance optimization (lazy loading)
        self._cache = None
        self._tier_orchestrator = None

        # Learning data directory
        self._learning_data_dir = learning_data_dir or (Path.home() / ".nc1709" / "learning")

        # Stats
        self._request_count = 0
        self._council_convenes = 0
        self._cache_hits = 0
        self._start_time = datetime.now()

    @property
    def router(self):
        """Layer 1: Intelligent Router"""
        if self._router is None:
            from .router import IntelligentRouter, IntentAnalyzer
            analyzer = IntentAnalyzer(llm_adapter=self._llm_adapter)
            self._router = IntelligentRouter(intent_analyzer=analyzer)
        return self._router

    @property
    def context_engine(self):
        """Layer 2: Deep Context Engine"""
        if self._context_engine is None:
            from .context_engine import DeepContextEngine
            self._context_engine = DeepContextEngine(project_root=self.project_root)
        return self._context_engine

    @property
    def council(self):
        """Layer 3: Multi-Agent Council"""
        if self._council is None:
            from .council import MultiAgentCouncil
            self._council = MultiAgentCouncil(
                llm_adapter=self._llm_adapter,
                council_threshold=self.council_threshold
            )
        return self._council

    @property
    def learning_core(self):
        """Layer 4: Learning Core"""
        if self._learning_core is None and self.enable_learning:
            from .learning import LearningCore
            self._learning_core = LearningCore(data_dir=self._learning_data_dir)
        return self._learning_core

    @property
    def anticipation_engine(self):
        """Layer 5: Anticipation Engine"""
        if self._anticipation_engine is None and self.enable_anticipation:
            from .anticipation import AnticipationEngine
            self._anticipation_engine = AnticipationEngine(
                learning_core=self.learning_core,
                context_engine=self.context_engine
            )
        return self._anticipation_engine

    @property
    def cache(self):
        """Performance: Multi-level Cache"""
        if self._cache is None and self.enable_cache:
            from ..performance import LayeredCache
            cache_path = Path.home() / ".nc1709" / "cache.json"
            self._cache = LayeredCache(persist_path=cache_path)
            self._cache.load()
        return self._cache

    @property
    def tier_orchestrator(self):
        """Performance: Model Tier Orchestrator"""
        if self._tier_orchestrator is None and self.enable_tiering:
            from ..performance import TieredModelOrchestrator
            self._tier_orchestrator = TieredModelOrchestrator()
        return self._tier_orchestrator

    def process(self, request: CognitiveRequest) -> CognitiveResponse:
        """
        Process a cognitive request through all layers

        Args:
            request: The cognitive request

        Returns:
            CognitiveResponse with the result
        """
        start_time = datetime.now()
        self._request_count += 1

        # Step 0: Check cache first (fastest path)
        cache_hit = False
        cache_level = None
        if self.enable_cache and not request.force_no_cache and self.cache:
            from ..performance import make_context_hash
            context_hash = make_context_hash(request.context or {})
            cache_result = self.cache.get(request.prompt, context_hash)

            if cache_result.hit:
                self._cache_hits += 1
                processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

                logger.info(f"Cache hit ({cache_result.level}) in {processing_time}ms")

                return CognitiveResponse(
                    content=cache_result.response,
                    model_used="cache",
                    category="cached",
                    complexity=0.0,
                    processing_time_ms=processing_time,
                    cache_hit=True,
                    cache_level=cache_result.level,
                    tier_used="cache",
                )

        # Step 1: Route the request (Layer 1)
        routing = self.router.route_sync(
            prompt=request.prompt,
            context=request.context
        )

        # Get category from intent if available
        category = routing.intent.primary_category if routing.intent else "unknown"
        category_value = category.value if hasattr(category, 'value') else str(category)

        logger.info(f"Routed to {routing.primary_model} ({category_value})")

        # Step 2: Build context (Layer 2)
        context = None
        if routing.context_budget > 0:
            context = self.context_engine.build_context_for_task(
                task_description=request.prompt,
                target_files=request.target_files,
            )

        # Get complexity from intent if available
        complexity = routing.intent.complexity if routing.intent else 0.5

        # Step 3: Determine if council needed (Layer 3)
        use_council = request.force_council or (
            routing.should_use_council and
            complexity > self.council_threshold
        )

        council_response = None
        council_agents = None

        if use_council:
            self._council_convenes += 1
            council_session = self.council.convene(
                task_description=request.prompt,
                task_category=category_value,
                complexity=complexity,
                context={
                    "code": context.get("code") if context else None,
                    "files": request.target_files,
                },
                agents=routing.agents_to_involve,
            )
            council_response = council_session.consensus
            council_agents = [a.value for a in council_session.agents_consulted]

        # Step 4: Select model tier (Performance)
        tier_used = None
        selected_model = routing.primary_model

        if self.enable_tiering and self.tier_orchestrator and not use_council:
            tier_decision = self.tier_orchestrator.select_tier(
                prompt=request.prompt,
                category=category_value,
                complexity=complexity,
            )
            tier_used = tier_decision.tier.value
            selected_model = tier_decision.model
            logger.info(f"Tier: {tier_used} -> {selected_model}")

        # Step 5: Get the actual completion
        if council_response:
            # Use council consensus
            content = council_response
            model_used = "council"
            tier_used = "council"
        else:
            # Get completion from selected model
            if self._llm_adapter:
                # Build enhanced prompt with context
                enhanced_prompt = request.prompt
                if context and context.get("summary"):
                    enhanced_prompt = f"Context: {context['summary']}\n\n{request.prompt}"

                content = self._llm_adapter.complete(
                    prompt=enhanced_prompt,
                    model=selected_model,
                )
            else:
                content = f"[Mock response for: {request.prompt[:100]}...]"
            model_used = selected_model

        # Step 5: Record interaction for learning (Layer 4)
        if self.learning_core:
            from .learning import InteractionType
            self.learning_core.record_interaction(
                interaction_type=InteractionType.COMPLETION,
                task_category=category_value,
                input_text=request.prompt,
                output_text=content,
                model_used=model_used,
                duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
            )

        # Step 6: Update anticipation and get suggestions (Layer 5)
        suggestions = []
        if self.anticipation_engine:
            # Update context
            self.anticipation_engine.update_context(
                current_file=request.target_files[0] if request.target_files else None,
                recent_files=request.target_files,
                current_task=category_value,
            )

            # Get suggestions
            suggestion_objects = self.anticipation_engine.get_suggestions(limit=3)
            suggestions = [
                {
                    "type": s.suggestion_type.value,
                    "title": s.title,
                    "description": s.description,
                    "confidence": s.confidence,
                    "action": s.action,
                }
                for s in suggestion_objects
            ]

        # Step 8: Cache the response (Performance)
        if self.enable_cache and self.cache and content:
            from ..performance import make_context_hash
            context_hash = make_context_hash(request.context or {})
            self.cache.set(
                prompt=request.prompt,
                context_hash=context_hash,
                response=content,
                model_used=model_used,
            )

        # Build response
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

        return CognitiveResponse(
            content=content,
            model_used=model_used,
            category=category_value,
            complexity=complexity,
            council_used=use_council,
            council_agents=council_agents,
            suggestions=suggestions if suggestions else None,
            context_summary=context.get("summary") if context else None,
            processing_time_ms=processing_time,
            cache_hit=False,
            cache_level=None,
            tier_used=tier_used,
            metadata={
                "routing_reasoning": routing.reasoning,
                "fallback_model": routing.fallback_model,
            }
        )

    async def process_async(self, request: CognitiveRequest) -> CognitiveResponse:
        """Async version of process"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.process(request))

    def quick_process(self, prompt: str, **kwargs) -> CognitiveResponse:
        """Quick helper for simple prompts"""
        request = CognitiveRequest(prompt=prompt, **kwargs)
        return self.process(request)

    def index_project(self, incremental: bool = True) -> Dict[str, Any]:
        """Index the project for context awareness"""
        return self.context_engine.index_project(incremental=incremental)

    def get_suggestions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get proactive suggestions"""
        if not self.anticipation_engine:
            return []

        suggestions = self.anticipation_engine.get_suggestions(limit=limit)
        return [
            {
                "type": s.suggestion_type.value,
                "title": s.title,
                "description": s.description,
                "confidence": s.confidence,
                "action": s.action,
            }
            for s in suggestions
        ]

    def get_user_insights(self) -> Dict[str, Any]:
        """Get insights about user patterns"""
        if not self.learning_core:
            return {"error": "Learning not enabled"}
        return self.learning_core.get_user_summary()

    def get_system_stats(self) -> Dict[str, Any]:
        """Get cognitive system statistics"""
        uptime = (datetime.now() - self._start_time).total_seconds()

        stats = {
            "uptime_seconds": uptime,
            "total_requests": self._request_count,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": self._cache_hits / self._request_count if self._request_count > 0 else 0,
            "council_convenes": self._council_convenes,
            "council_rate": self._council_convenes / self._request_count if self._request_count > 0 else 0,
            "layers_active": {
                "router": self._router is not None,
                "context_engine": self._context_engine is not None,
                "council": self._council is not None,
                "learning": self._learning_core is not None,
                "anticipation": self._anticipation_engine is not None,
            },
            "performance_active": {
                "cache": self._cache is not None,
                "tiering": self._tier_orchestrator is not None,
            }
        }

        # Add cache stats if available
        if self._cache:
            stats["cache_stats"] = self._cache.get_stats()

        # Add tiering stats if available
        if self._tier_orchestrator:
            stats["tiering_stats"] = self._tier_orchestrator.get_stats()

        # Add context stats if available
        if self._context_engine and hasattr(self._context_engine, '_indexed'):
            if self._context_engine._indexed:
                summary = self._context_engine.get_project_summary()
                stats["project"] = {
                    "files_indexed": summary.get("files_indexed", 0),
                    "total_lines": summary.get("total_lines", 0),
                    "patterns_detected": len(summary.get("patterns", [])),
                }

        return stats

    def shutdown(self) -> None:
        """Clean shutdown of the cognitive system"""
        logger.info("Shutting down cognitive system...")

        # Save performance cache
        if self._cache:
            self._cache.save()
            logger.info("Performance cache saved")

        # End learning session
        if self._learning_core:
            self._learning_core.end_session()

        # End anticipation session
        if self._anticipation_engine:
            self._anticipation_engine.end_session()

        # Save context cache
        if self._context_engine:
            self._context_engine.save_cache()

        logger.info("Cognitive system shutdown complete")


# Singleton instance
_cognitive_system: Optional[CognitiveSystem] = None


def get_cognitive_system(
    llm_adapter: Optional[Any] = None,
    project_root: Optional[Path] = None,
    **kwargs
) -> CognitiveSystem:
    """Get or create the cognitive system instance"""
    global _cognitive_system
    if _cognitive_system is None:
        _cognitive_system = CognitiveSystem(
            llm_adapter=llm_adapter,
            project_root=project_root,
            **kwargs
        )
    return _cognitive_system


def quick_cognitive(prompt: str, **kwargs) -> CognitiveResponse:
    """Quick helper for cognitive processing"""
    system = get_cognitive_system()
    return system.quick_process(prompt, **kwargs)
