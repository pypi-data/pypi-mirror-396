"""
NC1709 Performance - Parallel Processing Pipeline

Runs independent operations concurrently instead of sequentially.
Cache lookup, intent analysis, and context building all happen
simultaneously, with cache hits short-circuiting the pipeline.

Before (Sequential):
    Cache → Intent → Context → Generate = 500ms + 200ms + 300ms + 4000ms = 5000ms

After (Parallel):
    ┌─ Cache lookup ─────┐
    │                    │
    ├─ Intent analysis ──┼─→ Short-circuit if cache hit
    │                    │
    └─ Context building ─┘
           ↓
        Generate (only if cache miss)

    = max(500ms, 200ms, 300ms) + 4000ms = 4500ms (+ cache hits save 100%)
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple, Coroutine
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
import threading

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Stages in the processing pipeline"""
    CACHE_LOOKUP = "cache_lookup"
    INTENT_ANALYSIS = "intent_analysis"
    CONTEXT_BUILDING = "context_building"
    TIER_SELECTION = "tier_selection"
    GENERATION = "generation"
    POST_PROCESS = "post_process"


@dataclass
class StageResult:
    """Result from a pipeline stage"""
    stage: PipelineStage
    success: bool
    result: Any
    duration_ms: float
    error: Optional[str] = None

    @property
    def failed(self) -> bool:
        return not self.success


@dataclass
class PipelineResult:
    """Final result from pipeline execution"""
    response: Optional[str]
    stage_results: Dict[PipelineStage, StageResult]
    total_duration_ms: float
    cache_hit: bool
    tier_used: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.response is not None

    def get_stage_timing(self) -> Dict[str, float]:
        """Get timing for each stage"""
        return {
            stage.value: result.duration_ms
            for stage, result in self.stage_results.items()
        }


@dataclass
class PipelineStats:
    """Statistics for pipeline execution"""
    total_executions: int = 0
    cache_hits: int = 0
    parallel_time_saved_ms: float = 0
    stage_times: Dict[str, List[float]] = field(default_factory=lambda: {
        stage.value: [] for stage in PipelineStage
    })

    def record_execution(
        self,
        result: PipelineResult,
        sequential_estimate_ms: float
    ):
        """Record a pipeline execution"""
        self.total_executions += 1
        if result.cache_hit:
            self.cache_hits += 1

        # Track time saved by parallel execution
        if result.total_duration_ms < sequential_estimate_ms:
            self.parallel_time_saved_ms += sequential_estimate_ms - result.total_duration_ms

        # Track stage timings
        for stage, stage_result in result.stage_results.items():
            self.stage_times[stage.value].append(stage_result.duration_ms)

    def get_avg_stage_times(self) -> Dict[str, float]:
        """Get average time for each stage"""
        return {
            stage: sum(times) / len(times) if times else 0
            for stage, times in self.stage_times.items()
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_executions": self.total_executions,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.cache_hits / self.total_executions if self.total_executions > 0 else 0,
            "parallel_time_saved_ms": round(self.parallel_time_saved_ms, 2),
            "avg_stage_times": {k: round(v, 2) for k, v in self.get_avg_stage_times().items()},
        }


class ParallelPipeline:
    """
    Parallel processing pipeline for request handling.

    Executes independent stages concurrently and short-circuits
    on cache hits to minimize latency.

    Usage:
        pipeline = ParallelPipeline(
            cache=layered_cache,
            intent_analyzer=analyzer,
            context_engine=context_engine,
            tier_orchestrator=orchestrator,
        )

        result = await pipeline.process(
            prompt="explain decorators in Python",
            context={"files": ["main.py"]}
        )

        if result.cache_hit:
            print("Instant response from cache!")
        print(result.response)
    """

    def __init__(
        self,
        cache=None,
        intent_analyzer=None,
        context_engine=None,
        tier_orchestrator=None,
        llm_adapter=None,
        max_workers: int = 4,
        enable_parallel: bool = True
    ):
        self.cache = cache
        self.intent_analyzer = intent_analyzer
        self.context_engine = context_engine
        self.tier_orchestrator = tier_orchestrator
        self.llm_adapter = llm_adapter

        self.max_workers = max_workers
        self.enable_parallel = enable_parallel
        self.stats = PipelineStats()

        # Thread pool for sync operations
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    async def process(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        force_no_cache: bool = False
    ) -> PipelineResult:
        """
        Process a request through the parallel pipeline.

        Args:
            prompt: User's prompt
            context: Additional context
            force_no_cache: Skip cache lookup

        Returns:
            PipelineResult with response and timing info
        """
        start_time = time.time()
        context = context or {}
        stage_results: Dict[PipelineStage, StageResult] = {}

        # Phase 1: Parallel initial stages
        # These are independent and can run concurrently
        if self.enable_parallel:
            phase1_results = await self._run_parallel_phase1(
                prompt, context, force_no_cache
            )
        else:
            phase1_results = await self._run_sequential_phase1(
                prompt, context, force_no_cache
            )

        stage_results.update(phase1_results)

        # Check for cache hit (short-circuit)
        cache_result = stage_results.get(PipelineStage.CACHE_LOOKUP)
        if cache_result and cache_result.success and cache_result.result:
            cache_data = cache_result.result
            if cache_data.get("hit"):
                total_ms = (time.time() - start_time) * 1000

                # Record stats
                result = PipelineResult(
                    response=cache_data["response"],
                    stage_results=stage_results,
                    total_duration_ms=total_ms,
                    cache_hit=True,
                    tier_used="cache",
                )
                self.stats.record_execution(result, self._estimate_sequential_time())
                return result

        # Phase 2: Tier selection (depends on intent)
        intent_result = stage_results.get(PipelineStage.INTENT_ANALYSIS)
        intent_data = intent_result.result if intent_result and intent_result.success else None

        tier_result = await self._run_stage(
            PipelineStage.TIER_SELECTION,
            self._select_tier,
            prompt, intent_data
        )
        stage_results[PipelineStage.TIER_SELECTION] = tier_result

        # Phase 3: Generate response
        context_result = stage_results.get(PipelineStage.CONTEXT_BUILDING)
        context_data = context_result.result if context_result and context_result.success else None
        tier_data = tier_result.result if tier_result.success else None

        gen_result = await self._run_stage(
            PipelineStage.GENERATION,
            self._generate_response,
            prompt, tier_data, context_data, intent_data
        )
        stage_results[PipelineStage.GENERATION] = gen_result

        # Phase 4: Post-process and cache
        response = gen_result.result if gen_result.success else None

        if response and self.cache:
            post_result = await self._run_stage(
                PipelineStage.POST_PROCESS,
                self._post_process,
                prompt, context, response, tier_data
            )
            stage_results[PipelineStage.POST_PROCESS] = post_result

        total_ms = (time.time() - start_time) * 1000

        result = PipelineResult(
            response=response,
            stage_results=stage_results,
            total_duration_ms=total_ms,
            cache_hit=False,
            tier_used=tier_data.get("model") if tier_data else None,
        )

        self.stats.record_execution(result, self._estimate_sequential_time())
        return result

    async def _run_parallel_phase1(
        self,
        prompt: str,
        context: Dict[str, Any],
        force_no_cache: bool
    ) -> Dict[PipelineStage, StageResult]:
        """Run Phase 1 stages in parallel"""
        tasks = []

        # Cache lookup
        if not force_no_cache and self.cache:
            tasks.append(
                self._run_stage(
                    PipelineStage.CACHE_LOOKUP,
                    self._lookup_cache,
                    prompt, context
                )
            )

        # Intent analysis
        if self.intent_analyzer:
            tasks.append(
                self._run_stage(
                    PipelineStage.INTENT_ANALYSIS,
                    self._analyze_intent,
                    prompt, context
                )
            )

        # Context building
        if self.context_engine:
            tasks.append(
                self._run_stage(
                    PipelineStage.CONTEXT_BUILDING,
                    self._build_context,
                    prompt, context
                )
            )

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        stage_results = {}
        for result in results:
            if isinstance(result, StageResult):
                stage_results[result.stage] = result
            elif isinstance(result, Exception):
                logger.error(f"Stage failed with exception: {result}")

        return stage_results

    async def _run_sequential_phase1(
        self,
        prompt: str,
        context: Dict[str, Any],
        force_no_cache: bool
    ) -> Dict[PipelineStage, StageResult]:
        """Run Phase 1 stages sequentially (for comparison/fallback)"""
        stage_results = {}

        # Cache lookup first (can short-circuit)
        if not force_no_cache and self.cache:
            result = await self._run_stage(
                PipelineStage.CACHE_LOOKUP,
                self._lookup_cache,
                prompt, context
            )
            stage_results[PipelineStage.CACHE_LOOKUP] = result

            # Short-circuit on cache hit
            if result.success and result.result and result.result.get("hit"):
                return stage_results

        # Intent analysis
        if self.intent_analyzer:
            result = await self._run_stage(
                PipelineStage.INTENT_ANALYSIS,
                self._analyze_intent,
                prompt, context
            )
            stage_results[PipelineStage.INTENT_ANALYSIS] = result

        # Context building
        if self.context_engine:
            result = await self._run_stage(
                PipelineStage.CONTEXT_BUILDING,
                self._build_context,
                prompt, context
            )
            stage_results[PipelineStage.CONTEXT_BUILDING] = result

        return stage_results

    async def _run_stage(
        self,
        stage: PipelineStage,
        func: Callable,
        *args, **kwargs
    ) -> StageResult:
        """Run a single pipeline stage with timing"""
        start = time.time()

        try:
            # Check if function is async
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self._executor,
                    lambda: func(*args, **kwargs)
                )

            duration = (time.time() - start) * 1000

            return StageResult(
                stage=stage,
                success=True,
                result=result,
                duration_ms=duration,
            )

        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"Stage {stage.value} failed: {e}")

            return StageResult(
                stage=stage,
                success=False,
                result=None,
                duration_ms=duration,
                error=str(e),
            )

    # Stage implementations

    def _lookup_cache(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Look up in cache"""
        if not self.cache:
            return {"hit": False}

        from .cache import make_context_hash
        context_hash = make_context_hash(context)

        result = self.cache.get(prompt, context_hash)

        return {
            "hit": result.hit,
            "response": result.response,
            "level": result.level,
            "similarity": result.similarity,
        }

    def _analyze_intent(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user intent"""
        if not self.intent_analyzer:
            return {}

        # Use sync method
        if hasattr(self.intent_analyzer, 'analyze_sync'):
            intent = self.intent_analyzer.analyze_sync(prompt)
        else:
            intent = self.intent_analyzer.analyze(prompt)

        return {
            "category": intent.primary_category.value if hasattr(intent.primary_category, 'value') else str(intent.primary_category),
            "complexity": intent.complexity,
            "confidence": intent.confidence,
            "requires_context": intent.requires_context,
        }

    def _build_context(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build context for the request"""
        if not self.context_engine:
            return {}

        # Get relevant context
        target_files = context.get("target_files", [])

        try:
            built_context = self.context_engine.build_context_for_task(
                task_description=prompt,
                target_files=target_files,
            )
            return built_context or {}
        except Exception as e:
            logger.warning(f"Context building failed: {e}")
            return {}

    def _select_tier(
        self,
        prompt: str,
        intent_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select model tier"""
        if not self.tier_orchestrator:
            return {"model": "default", "tier": "smart"}

        category = intent_data.get("category") if intent_data else None
        complexity = intent_data.get("complexity") if intent_data else None

        decision = self.tier_orchestrator.select_tier(
            prompt=prompt,
            category=category,
            complexity=complexity,
        )

        return {
            "tier": decision.tier.value,
            "model": decision.model,
            "reasoning": decision.reasoning,
            "confidence": decision.confidence,
        }

    def _generate_response(
        self,
        prompt: str,
        tier_data: Optional[Dict[str, Any]],
        context_data: Optional[Dict[str, Any]],
        intent_data: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Generate LLM response"""
        if not self.llm_adapter:
            # Mock response for testing
            return f"[Mock response for: {prompt[:50]}...]"

        model = tier_data.get("model") if tier_data else None

        # Build enhanced prompt with context
        enhanced_prompt = prompt
        if context_data and context_data.get("summary"):
            enhanced_prompt = f"Context: {context_data['summary']}\n\n{prompt}"

        try:
            response = self.llm_adapter.complete(
                prompt=enhanced_prompt,
                model=model,
            )
            return response
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None

    def _post_process(
        self,
        prompt: str,
        context: Dict[str, Any],
        response: str,
        tier_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Post-process and cache response"""
        if self.cache and response:
            from .cache import make_context_hash
            context_hash = make_context_hash(context)

            model_used = tier_data.get("model", "unknown") if tier_data else "unknown"

            self.cache.set(
                prompt=prompt,
                context_hash=context_hash,
                response=response,
                model_used=model_used,
                tokens_saved=len(response.split()) * 2,  # Rough estimate
            )

        return {"cached": True}

    def _estimate_sequential_time(self) -> float:
        """Estimate time for sequential execution"""
        # Based on typical stage times
        return 5000  # 5 seconds

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return self.stats.to_dict()

    def shutdown(self):
        """Shutdown the pipeline"""
        self._executor.shutdown(wait=False)


class SyncPipeline:
    """
    Synchronous wrapper for ParallelPipeline.

    For use in non-async contexts.
    """

    def __init__(self, pipeline: ParallelPipeline):
        self._pipeline = pipeline
        self._loop = None

    def process(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        force_no_cache: bool = False
    ) -> PipelineResult:
        """Process synchronously"""
        try:
            # Try to get existing loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, use run_coroutine_threadsafe
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(
                    self._pipeline.process(prompt, context, force_no_cache),
                    loop
                )
                return future.result(timeout=120)
            else:
                return loop.run_until_complete(
                    self._pipeline.process(prompt, context, force_no_cache)
                )
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(
                self._pipeline.process(prompt, context, force_no_cache)
            )


# Convenience functions
def create_pipeline(
    cache=None,
    intent_analyzer=None,
    context_engine=None,
    tier_orchestrator=None,
    llm_adapter=None,
    **kwargs
) -> ParallelPipeline:
    """Create a configured pipeline"""
    return ParallelPipeline(
        cache=cache,
        intent_analyzer=intent_analyzer,
        context_engine=context_engine,
        tier_orchestrator=tier_orchestrator,
        llm_adapter=llm_adapter,
        **kwargs
    )
