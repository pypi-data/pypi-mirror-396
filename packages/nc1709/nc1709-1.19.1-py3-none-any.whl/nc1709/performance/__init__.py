"""
NC1709 Performance Optimization Stack

A comprehensive performance optimization layer that provides:
- Multi-level intelligent caching (L1/L2/L3)
- Smart model tiering (3B → 7B → 32B → Council)
- Parallel processing pipeline

Expected improvements:
- Cache hits: <100ms (instant)
- Simple queries: 0.3-0.5s (was 5s)
- Medium queries: 1-2s (was 8s)
- Complex queries: 5-7s (was 15s)

Usage:
    from nc1709.performance import PerformanceOptimizer

    optimizer = PerformanceOptimizer()

    # Process with full optimization
    result = optimizer.process(
        prompt="explain decorators",
        context={"files": ["main.py"]}
    )

    print(f"Response in {result.latency_ms}ms (cache: {result.cache_hit})")
"""

from .cache import (
    LayeredCache,
    L1ExactCache,
    L2SemanticCache,
    L3TemplateCache,
    CacheEntry,
    CacheStats,
    CacheResult,
    get_cache,
    make_context_hash,
)

from .tiering import (
    ModelTier,
    TierConfig,
    TieringDecision,
    TieringStats,
    TieredModelOrchestrator,
    get_orchestrator,
    quick_tier,
    DEFAULT_TIERS,
)

from .pipeline import (
    PipelineStage,
    StageResult,
    PipelineResult,
    PipelineStats,
    ParallelPipeline,
    SyncPipeline,
    create_pipeline,
)

from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class OptimizedResult:
    """Result from the performance optimizer"""
    response: Optional[str]
    latency_ms: float
    cache_hit: bool
    cache_level: Optional[str]
    tier_used: Optional[str]
    model_used: Optional[str]
    stage_timings: Dict[str, float]

    @property
    def success(self) -> bool:
        return self.response is not None


class PerformanceOptimizer:
    """
    Unified performance optimization interface.

    Combines caching, tiering, and parallel pipeline into a single
    easy-to-use interface.

    Usage:
        optimizer = PerformanceOptimizer(
            project_root=Path.cwd(),
            enable_cache=True,
            enable_tiering=True,
            enable_parallel=True,
        )

        result = optimizer.process("explain decorators")

        if result.cache_hit:
            print(f"Cache hit ({result.cache_level})!")
        else:
            print(f"Generated with {result.model_used}")

        print(f"Total: {result.latency_ms}ms")
    """

    def __init__(
        self,
        llm_adapter=None,
        intent_analyzer=None,
        context_engine=None,
        project_root: Optional[Path] = None,
        cache_path: Optional[Path] = None,
        enable_cache: bool = True,
        enable_tiering: bool = True,
        enable_parallel: bool = True,
        l1_cache_size: int = 1000,
        l2_cache_size: int = 500,
        l2_threshold: float = 0.92,
        conservative_tiering: bool = False,
    ):
        self.llm_adapter = llm_adapter
        self.project_root = project_root or Path.cwd()
        self.enable_cache = enable_cache
        self.enable_tiering = enable_tiering
        self.enable_parallel = enable_parallel

        # Initialize cache
        self._cache = None
        if enable_cache:
            cache_path = cache_path or (Path.home() / ".nc1709" / "cache.json")
            self._cache = LayeredCache(
                l1_size=l1_cache_size,
                l2_size=l2_cache_size,
                l2_threshold=l2_threshold,
                persist_path=cache_path,
            )
            self._cache.load()

        # Initialize tiering
        self._tier_orchestrator = None
        if enable_tiering:
            self._tier_orchestrator = TieredModelOrchestrator(
                conservative=conservative_tiering
            )

        # Initialize pipeline
        self._pipeline = ParallelPipeline(
            cache=self._cache,
            intent_analyzer=intent_analyzer,
            context_engine=context_engine,
            tier_orchestrator=self._tier_orchestrator,
            llm_adapter=llm_adapter,
            enable_parallel=enable_parallel,
        )

        # Stats
        self._request_count = 0
        self._start_time = time.time()

    def process(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        force_no_cache: bool = False,
        force_tier: Optional[ModelTier] = None,
    ) -> OptimizedResult:
        """
        Process a request with full optimization.

        Args:
            prompt: User's prompt
            context: Additional context
            force_no_cache: Skip cache lookup
            force_tier: Force a specific tier

        Returns:
            OptimizedResult with response and performance info
        """
        start = time.time()
        self._request_count += 1
        context = context or {}

        # Quick cache check first (outside pipeline for speed)
        if self.enable_cache and not force_no_cache and self._cache:
            context_hash = make_context_hash(context)
            cache_result = self._cache.get(prompt, context_hash)

            if cache_result.hit:
                latency = (time.time() - start) * 1000
                logger.info(f"Cache hit ({cache_result.level}) in {latency:.1f}ms")

                return OptimizedResult(
                    response=cache_result.response,
                    latency_ms=latency,
                    cache_hit=True,
                    cache_level=cache_result.level,
                    tier_used="cache",
                    model_used="cache",
                    stage_timings={"cache_lookup": cache_result.time_ms},
                )

        # Use pipeline for full processing
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create sync wrapper
                sync_pipeline = SyncPipeline(self._pipeline)
                result = sync_pipeline.process(prompt, context, force_no_cache=True)
            else:
                result = loop.run_until_complete(
                    self._pipeline.process(prompt, context, force_no_cache=True)
                )
        except RuntimeError:
            result = asyncio.run(
                self._pipeline.process(prompt, context, force_no_cache=True)
            )

        latency = (time.time() - start) * 1000

        # Cache the result
        if self.enable_cache and self._cache and result.response:
            context_hash = make_context_hash(context)
            self._cache.set(
                prompt=prompt,
                context_hash=context_hash,
                response=result.response,
                model_used=result.tier_used or "unknown",
            )

        return OptimizedResult(
            response=result.response,
            latency_ms=latency,
            cache_hit=result.cache_hit,
            cache_level=None,
            tier_used=result.tier_used,
            model_used=result.tier_used,
            stage_timings=result.get_stage_timing(),
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        uptime = time.time() - self._start_time

        stats = {
            "uptime_seconds": round(uptime, 2),
            "total_requests": self._request_count,
            "requests_per_minute": round(self._request_count / (uptime / 60), 2) if uptime > 0 else 0,
        }

        if self._cache:
            stats["cache"] = self._cache.get_stats()

        if self._tier_orchestrator:
            stats["tiering"] = self._tier_orchestrator.get_stats()

        stats["pipeline"] = self._pipeline.get_stats()

        return stats

    def clear_cache(self) -> Dict[str, int]:
        """Clear all caches"""
        if self._cache:
            return self._cache.clear()
        return {}

    def save_cache(self) -> bool:
        """Persist cache to disk"""
        if self._cache:
            return self._cache.save()
        return False

    def shutdown(self) -> None:
        """Clean shutdown"""
        self.save_cache()
        self._pipeline.shutdown()
        logger.info("Performance optimizer shutdown complete")


# Singleton instance
_optimizer: Optional[PerformanceOptimizer] = None


def get_optimizer(**kwargs) -> PerformanceOptimizer:
    """Get or create the global optimizer"""
    global _optimizer
    if _optimizer is None:
        _optimizer = PerformanceOptimizer(**kwargs)
    return _optimizer


def quick_optimize(
    prompt: str,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> OptimizedResult:
    """Quick helper for optimized processing"""
    optimizer = get_optimizer(**kwargs)
    return optimizer.process(prompt, context)


__all__ = [
    # Cache
    "LayeredCache",
    "L1ExactCache",
    "L2SemanticCache",
    "L3TemplateCache",
    "CacheEntry",
    "CacheStats",
    "CacheResult",
    "get_cache",
    "make_context_hash",
    # Tiering
    "ModelTier",
    "TierConfig",
    "TieringDecision",
    "TieringStats",
    "TieredModelOrchestrator",
    "get_orchestrator",
    "quick_tier",
    "DEFAULT_TIERS",
    # Pipeline
    "PipelineStage",
    "StageResult",
    "PipelineResult",
    "PipelineStats",
    "ParallelPipeline",
    "SyncPipeline",
    "create_pipeline",
    # Unified
    "OptimizedResult",
    "PerformanceOptimizer",
    "get_optimizer",
    "quick_optimize",
]

__version__ = "0.1.0"
