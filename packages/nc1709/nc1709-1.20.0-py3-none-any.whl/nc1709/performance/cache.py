"""
NC1709 Performance - Multi-Level Intelligent Caching

Implements a 3-level cache system inspired by CPU cache architecture:
- L1: Exact match cache (<1ms lookup)
- L2: Semantic similarity cache (~10ms lookup)
- L3: Template/pattern cache (~50ms lookup)

Target: 30-40% cache hit rate for significant latency reduction.
"""

import hashlib
import time
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, NamedTuple
from dataclasses import dataclass, field
from collections import OrderedDict
import threading

logger = logging.getLogger(__name__)

# Optional: sentence-transformers for semantic cache
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    from sentence_transformers import SentenceTransformer
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    SentenceTransformer = None


@dataclass
class CacheEntry:
    """A cached response entry"""
    prompt: str
    context_hash: str
    response: str
    model_used: str
    created_at: float
    access_count: int = 0
    last_accessed: float = 0
    tokens_saved: int = 0
    embedding: Optional[Any] = None  # numpy array if available

    def touch(self):
        """Update access statistics"""
        self.access_count += 1
        self.last_accessed = time.time()


@dataclass
class CacheStats:
    """Cache performance statistics"""
    l1_hits: int = 0
    l2_hits: int = 0
    l3_hits: int = 0
    misses: int = 0
    total_time_saved_ms: float = 0
    total_tokens_saved: int = 0

    @property
    def total_queries(self) -> int:
        return self.l1_hits + self.l2_hits + self.l3_hits + self.misses

    @property
    def hit_rate(self) -> float:
        if self.total_queries == 0:
            return 0.0
        return (self.l1_hits + self.l2_hits + self.l3_hits) / self.total_queries

    @property
    def l1_rate(self) -> float:
        if self.total_queries == 0:
            return 0.0
        return self.l1_hits / self.total_queries

    def to_dict(self) -> Dict[str, Any]:
        return {
            "l1_hits": self.l1_hits,
            "l2_hits": self.l2_hits,
            "l3_hits": self.l3_hits,
            "misses": self.misses,
            "total_queries": self.total_queries,
            "hit_rate": round(self.hit_rate * 100, 2),
            "total_time_saved_ms": round(self.total_time_saved_ms, 2),
            "total_tokens_saved": self.total_tokens_saved,
        }


class CacheResult(NamedTuple):
    """Result from cache lookup"""
    hit: bool
    response: Optional[str]
    level: Optional[str]  # "L1", "L2", "L3", or None
    similarity: Optional[float]  # For L2/L3 hits
    time_ms: float


class L1ExactCache:
    """
    Level 1: Exact Match Cache

    Fastest lookup - requires identical prompt + context hash.
    Uses LRU eviction policy.

    Lookup time: <1ms
    """

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()

    def _make_key(self, prompt: str, context_hash: str) -> str:
        """Create cache key from prompt and context"""
        combined = f"{prompt.strip().lower()}:{context_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    def get(self, prompt: str, context_hash: str) -> Optional[CacheEntry]:
        """Look up exact match"""
        key = self._make_key(prompt, context_hash)

        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                entry.touch()
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                return entry

        return None

    def set(self, prompt: str, context_hash: str, response: str,
            model_used: str, tokens_saved: int = 0) -> None:
        """Store in cache"""
        key = self._make_key(prompt, context_hash)

        with self._lock:
            # Evict if at capacity
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)  # Remove oldest

            self._cache[key] = CacheEntry(
                prompt=prompt,
                context_hash=context_hash,
                response=response,
                model_used=model_used,
                created_at=time.time(),
                last_accessed=time.time(),
                tokens_saved=tokens_saved,
            )

    def clear(self) -> int:
        """Clear cache, return number of entries cleared"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def __len__(self) -> int:
        return len(self._cache)


class L2SemanticCache:
    """
    Level 2: Semantic Similarity Cache

    Finds cached responses for semantically similar prompts.
    Uses sentence embeddings and cosine similarity.

    Example matches:
    - "write a function to reverse a string" ≈ "create a string reversal function"
    - "fix the bug in login" ≈ "debug the authentication issue"

    Lookup time: ~10ms
    """

    def __init__(
        self,
        similarity_threshold: float = 0.92,
        max_size: int = 500,
        model_name: str = 'all-MiniLM-L6-v2'
    ):
        self.threshold = similarity_threshold
        self.max_size = max_size
        self._lock = threading.RLock()

        # Initialize encoder if available
        self._encoder = None
        self._encoder_ready = False

        if SEMANTIC_AVAILABLE and NUMPY_AVAILABLE:
            try:
                self._encoder = SentenceTransformer(model_name)
                self._encoder_ready = True
                logger.info(f"L2 semantic cache initialized with {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer: {e}")
        else:
            logger.info("L2 semantic cache disabled (sentence-transformers not installed)")

        self._entries: List[CacheEntry] = []
        self._embeddings: Optional[Any] = None  # numpy array

    @property
    def available(self) -> bool:
        return self._encoder_ready

    def get(self, prompt: str, context_hash: str) -> Optional[Tuple[CacheEntry, float]]:
        """
        Find semantically similar cached response.
        Returns (entry, similarity_score) or None.
        """
        if not self._encoder_ready or not self._entries:
            return None

        with self._lock:
            try:
                # Encode query
                query_embedding = self._encoder.encode(
                    prompt,
                    convert_to_numpy=True,
                    show_progress_bar=False
                )

                # Compute cosine similarities
                # Normalize query
                query_norm = query_embedding / np.linalg.norm(query_embedding)

                # Compute dot products (embeddings are already normalized)
                similarities = np.dot(self._embeddings, query_norm)

                # Find best match
                best_idx = np.argmax(similarities)
                best_score = float(similarities[best_idx])

                if best_score >= self.threshold:
                    entry = self._entries[best_idx]

                    # Verify context also matches
                    if entry.context_hash == context_hash:
                        entry.touch()
                        return (entry, best_score)

            except Exception as e:
                logger.warning(f"L2 cache lookup error: {e}")

        return None

    def set(self, prompt: str, context_hash: str, response: str,
            model_used: str, tokens_saved: int = 0) -> None:
        """Store in semantic cache"""
        if not self._encoder_ready:
            return

        with self._lock:
            try:
                # Evict if at capacity
                while len(self._entries) >= self.max_size:
                    self._evict_lru()

                # Compute and normalize embedding
                embedding = self._encoder.encode(
                    prompt,
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
                embedding = embedding / np.linalg.norm(embedding)

                entry = CacheEntry(
                    prompt=prompt,
                    context_hash=context_hash,
                    response=response,
                    model_used=model_used,
                    created_at=time.time(),
                    last_accessed=time.time(),
                    tokens_saved=tokens_saved,
                    embedding=embedding,
                )

                self._entries.append(entry)

                # Update embeddings matrix
                if self._embeddings is None:
                    self._embeddings = embedding.reshape(1, -1)
                else:
                    self._embeddings = np.vstack([self._embeddings, embedding])

            except Exception as e:
                logger.warning(f"L2 cache set error: {e}")

    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self._entries:
            return

        # Find LRU entry
        lru_idx = min(
            range(len(self._entries)),
            key=lambda i: self._entries[i].last_accessed
        )

        # Remove entry and corresponding embedding row
        del self._entries[lru_idx]
        if self._embeddings is not None:
            self._embeddings = np.delete(self._embeddings, lru_idx, axis=0)

    def clear(self) -> int:
        """Clear cache"""
        with self._lock:
            count = len(self._entries)
            self._entries.clear()
            self._embeddings = None
            return count

    def __len__(self) -> int:
        return len(self._entries)


class L3TemplateCache:
    """
    Level 3: Template/Pattern Cache

    Caches responses for common patterns that can be parameterized.
    Useful for repetitive tasks with slight variations.

    Examples:
    - "write tests for {function}" → cached test template
    - "explain {concept}" → cached explanation pattern
    - "add logging to {file}" → cached modification pattern

    Lookup time: ~50ms
    """

    # Common templates to detect
    TEMPLATES = [
        # Test writing
        (r"(write|create|add)\s+(unit\s+)?tests?\s+for\s+(.+)", "test_function"),
        (r"test\s+(.+)\s+(function|class|module)", "test_function"),

        # Explanations
        (r"(explain|describe|what\s+is)\s+(.+)", "explanation"),
        (r"how\s+does\s+(.+)\s+work", "explanation"),

        # Documentation
        (r"(document|add\s+docs?\s+to|docstring\s+for)\s+(.+)", "documentation"),

        # Refactoring
        (r"refactor\s+(.+)", "refactoring"),
        (r"(clean\s+up|improve)\s+(.+)", "refactoring"),

        # Type hints
        (r"add\s+type\s+hints?\s+to\s+(.+)", "type_hints"),

        # Logging
        (r"add\s+logging\s+to\s+(.+)", "logging"),

        # Error handling
        (r"add\s+error\s+handling\s+to\s+(.+)", "error_handling"),
    ]

    def __init__(self, max_size: int = 200):
        self.max_size = max_size
        self._cache: Dict[str, List[CacheEntry]] = {}  # template_type -> entries
        self._lock = threading.RLock()

        # Compile regex patterns
        import re
        self._patterns = [
            (re.compile(pattern, re.IGNORECASE), template_type)
            for pattern, template_type in self.TEMPLATES
        ]

    def _detect_template(self, prompt: str) -> Optional[Tuple[str, str]]:
        """
        Detect if prompt matches a template pattern.
        Returns (template_type, extracted_entity) or None.
        """
        for pattern, template_type in self._patterns:
            match = pattern.search(prompt)
            if match:
                # Extract the variable part (last group)
                entity = match.groups()[-1] if match.groups() else ""
                return (template_type, entity.strip())
        return None

    def get(self, prompt: str, context_hash: str) -> Optional[Tuple[CacheEntry, float]]:
        """
        Find template-matched cached response.
        Returns (entry, confidence) or None.
        """
        template_match = self._detect_template(prompt)
        if not template_match:
            return None

        template_type, entity = template_match

        with self._lock:
            if template_type not in self._cache:
                return None

            entries = self._cache[template_type]

            # Find best match by context similarity
            for entry in entries:
                if entry.context_hash == context_hash:
                    entry.touch()
                    return (entry, 0.85)  # Template match confidence

            # If no exact context match, return most recent with lower confidence
            if entries:
                entry = max(entries, key=lambda e: e.last_accessed)
                entry.touch()
                return (entry, 0.70)

        return None

    def set(self, prompt: str, context_hash: str, response: str,
            model_used: str, tokens_saved: int = 0) -> None:
        """Store in template cache if prompt matches a template"""
        template_match = self._detect_template(prompt)
        if not template_match:
            return

        template_type, _ = template_match

        with self._lock:
            if template_type not in self._cache:
                self._cache[template_type] = []

            entries = self._cache[template_type]

            # Limit entries per template
            max_per_template = self.max_size // len(self.TEMPLATES)
            while len(entries) >= max_per_template:
                # Remove oldest
                entries.sort(key=lambda e: e.last_accessed)
                entries.pop(0)

            entries.append(CacheEntry(
                prompt=prompt,
                context_hash=context_hash,
                response=response,
                model_used=model_used,
                created_at=time.time(),
                last_accessed=time.time(),
                tokens_saved=tokens_saved,
            ))

    def clear(self) -> int:
        """Clear cache"""
        with self._lock:
            count = sum(len(entries) for entries in self._cache.values())
            self._cache.clear()
            return count

    def __len__(self) -> int:
        return sum(len(entries) for entries in self._cache.values())


class LayeredCache:
    """
    Unified multi-level cache manager.

    Queries flow through L1 → L2 → L3 until a hit is found.
    Responses are stored in all applicable cache levels.

    Usage:
        cache = LayeredCache()

        # Lookup
        result = cache.get(prompt, context_hash)
        if result.hit:
            return result.response  # Cache hit!

        # After generating response
        cache.set(prompt, context_hash, response, model_used)
    """

    def __init__(
        self,
        l1_size: int = 1000,
        l2_size: int = 500,
        l2_threshold: float = 0.92,
        l3_size: int = 200,
        persist_path: Optional[Path] = None
    ):
        self.l1 = L1ExactCache(max_size=l1_size)
        self.l2 = L2SemanticCache(
            similarity_threshold=l2_threshold,
            max_size=l2_size
        )
        self.l3 = L3TemplateCache(max_size=l3_size)

        self.stats = CacheStats()
        self.persist_path = persist_path

        # Average response time for savings calculation (ms)
        self._avg_response_time = 5000  # 5 seconds default

    def get(self, prompt: str, context_hash: str = "") -> CacheResult:
        """
        Look up in all cache levels.
        Returns CacheResult with hit status and response.
        """
        start = time.time()

        # L1: Exact match (fastest)
        entry = self.l1.get(prompt, context_hash)
        if entry:
            elapsed = (time.time() - start) * 1000
            self.stats.l1_hits += 1
            self.stats.total_time_saved_ms += self._avg_response_time
            self.stats.total_tokens_saved += entry.tokens_saved

            logger.debug(f"L1 cache hit in {elapsed:.2f}ms")
            return CacheResult(
                hit=True,
                response=entry.response,
                level="L1",
                similarity=1.0,
                time_ms=elapsed
            )

        # L2: Semantic match
        if self.l2.available:
            result = self.l2.get(prompt, context_hash)
            if result:
                entry, similarity = result
                elapsed = (time.time() - start) * 1000
                self.stats.l2_hits += 1
                self.stats.total_time_saved_ms += self._avg_response_time
                self.stats.total_tokens_saved += entry.tokens_saved

                logger.debug(f"L2 cache hit (sim={similarity:.3f}) in {elapsed:.2f}ms")
                return CacheResult(
                    hit=True,
                    response=entry.response,
                    level="L2",
                    similarity=similarity,
                    time_ms=elapsed
                )

        # L3: Template match
        result = self.l3.get(prompt, context_hash)
        if result:
            entry, confidence = result
            elapsed = (time.time() - start) * 1000
            self.stats.l3_hits += 1
            self.stats.total_time_saved_ms += self._avg_response_time * 0.5  # Partial savings
            self.stats.total_tokens_saved += entry.tokens_saved

            logger.debug(f"L3 cache hit (conf={confidence:.3f}) in {elapsed:.2f}ms")
            return CacheResult(
                hit=True,
                response=entry.response,
                level="L3",
                similarity=confidence,
                time_ms=elapsed
            )

        # Cache miss
        elapsed = (time.time() - start) * 1000
        self.stats.misses += 1

        return CacheResult(
            hit=False,
            response=None,
            level=None,
            similarity=None,
            time_ms=elapsed
        )

    def set(
        self,
        prompt: str,
        context_hash: str,
        response: str,
        model_used: str,
        tokens_saved: int = 0
    ) -> None:
        """Store response in all applicable cache levels"""
        # Always store in L1
        self.l1.set(prompt, context_hash, response, model_used, tokens_saved)

        # Store in L2 if available
        if self.l2.available:
            self.l2.set(prompt, context_hash, response, model_used, tokens_saved)

        # Store in L3 if matches a template
        self.l3.set(prompt, context_hash, response, model_used, tokens_saved)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.stats.to_dict()
        stats["sizes"] = {
            "l1": len(self.l1),
            "l2": len(self.l2),
            "l3": len(self.l3),
        }
        stats["l2_available"] = self.l2.available
        return stats

    def clear(self) -> Dict[str, int]:
        """Clear all caches"""
        return {
            "l1_cleared": self.l1.clear(),
            "l2_cleared": self.l2.clear(),
            "l3_cleared": self.l3.clear(),
        }

    def save(self) -> bool:
        """Persist L1 cache to disk"""
        if not self.persist_path:
            return False

        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)

            # Serialize L1 cache (L2/L3 are rebuilt from L1)
            data = {
                "entries": [
                    {
                        "prompt": entry.prompt,
                        "context_hash": entry.context_hash,
                        "response": entry.response,
                        "model_used": entry.model_used,
                        "created_at": entry.created_at,
                        "access_count": entry.access_count,
                        "tokens_saved": entry.tokens_saved,
                    }
                    for entry in self.l1._cache.values()
                ],
                "stats": self.stats.to_dict(),
            }

            with open(self.persist_path, 'w') as f:
                json.dump(data, f)

            logger.info(f"Cache saved to {self.persist_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            return False

    def load(self) -> bool:
        """Load cache from disk"""
        if not self.persist_path or not self.persist_path.exists():
            return False

        try:
            with open(self.persist_path) as f:
                data = json.load(f)

            for entry_data in data.get("entries", []):
                self.l1.set(
                    entry_data["prompt"],
                    entry_data["context_hash"],
                    entry_data["response"],
                    entry_data["model_used"],
                    entry_data.get("tokens_saved", 0)
                )

            logger.info(f"Loaded {len(self.l1)} entries from cache")
            return True

        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return False


# Convenience functions
def make_context_hash(context: Dict[str, Any]) -> str:
    """Create hash from context dictionary"""
    # Sort keys for consistent hashing
    serialized = json.dumps(context, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


# Singleton instance
_cache: Optional[LayeredCache] = None


def get_cache(
    persist_path: Optional[Path] = None,
    **kwargs
) -> LayeredCache:
    """Get or create the global cache instance"""
    global _cache
    if _cache is None:
        _cache = LayeredCache(
            persist_path=persist_path or Path.home() / ".nc1709" / "cache.json",
            **kwargs
        )
        _cache.load()  # Try to load persisted cache
    return _cache
