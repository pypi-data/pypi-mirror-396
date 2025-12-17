"""
Request Queue System for NC1709

Provides intelligent request queuing under load with:
- Priority-based queue management
- Concurrency control
- Request batching for efficiency
- Queue statistics and monitoring
- Automatic backpressure handling
"""

import asyncio
import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import deque
import heapq


class RequestPriority(Enum):
    """Priority levels for requests"""
    CRITICAL = 0    # System-critical, interactive user requests
    HIGH = 1        # Complex reasoning, architecture tasks
    NORMAL = 2      # Standard coding tasks
    LOW = 3         # Background tasks, suggestions
    BATCH = 4       # Bulk/batch processing


@dataclass(order=True)
class QueuedRequest:
    """A request waiting in the queue"""
    priority: int
    timestamp: float = field(compare=False)
    request_id: str = field(compare=False)
    prompt: str = field(compare=False)
    callback: Optional[Callable] = field(compare=False, default=None)
    context: Dict[str, Any] = field(compare=False, default_factory=dict)
    timeout: float = field(compare=False, default=300.0)  # 5 minutes default
    retries: int = field(compare=False, default=0)
    max_retries: int = field(compare=False, default=3)

    def __post_init__(self):
        if not self.request_id:
            self.request_id = f"req_{int(self.timestamp * 1000)}"


@dataclass
class QueueStats:
    """Statistics about the request queue"""
    total_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0
    active_requests: int = 0
    queued_requests: int = 0
    avg_wait_time: float = 0.0
    avg_processing_time: float = 0.0
    requests_per_minute: float = 0.0
    peak_queue_size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "completed_requests": self.completed_requests,
            "failed_requests": self.failed_requests,
            "active_requests": self.active_requests,
            "queued_requests": self.queued_requests,
            "avg_wait_time_ms": round(self.avg_wait_time * 1000, 2),
            "avg_processing_time_ms": round(self.avg_processing_time * 1000, 2),
            "requests_per_minute": round(self.requests_per_minute, 2),
            "peak_queue_size": self.peak_queue_size,
        }


class RequestQueue:
    """
    Thread-safe priority queue for LLM requests

    Features:
    - Priority-based scheduling (critical > high > normal > low > batch)
    - Concurrency limiting to prevent model overload
    - Request timeout handling
    - Automatic retry with exponential backoff
    - Queue statistics and monitoring
    """

    def __init__(
        self,
        max_concurrent: int = 2,
        max_queue_size: int = 100,
        default_timeout: float = 300.0
    ):
        """
        Initialize the request queue

        Args:
            max_concurrent: Maximum concurrent requests to process
            max_queue_size: Maximum requests to queue before rejecting
            default_timeout: Default timeout for requests in seconds
        """
        self.max_concurrent = max_concurrent
        self.max_queue_size = max_queue_size
        self.default_timeout = default_timeout

        # Priority queue (min-heap based on priority)
        self._queue: List[QueuedRequest] = []
        self._queue_lock = threading.Lock()

        # Active request tracking
        self._active_requests: Dict[str, QueuedRequest] = {}
        self._active_lock = threading.Lock()

        # Statistics
        self._stats = QueueStats()
        self._wait_times: deque = deque(maxlen=100)
        self._processing_times: deque = deque(maxlen=100)
        self._request_timestamps: deque = deque(maxlen=100)

        # Control
        self._shutdown = False
        self._processor_thread: Optional[threading.Thread] = None
        self._completion_callbacks: Dict[str, Callable] = {}

        # Request processor function (to be set by LLM adapter)
        self._process_func: Optional[Callable] = None

    def set_processor(self, func: Callable) -> None:
        """Set the function that processes requests"""
        self._process_func = func

    def enqueue(
        self,
        prompt: str,
        priority: RequestPriority = RequestPriority.NORMAL,
        context: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable] = None,
        timeout: Optional[float] = None,
        request_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Add a request to the queue

        Args:
            prompt: The prompt to process
            priority: Request priority level
            context: Additional context for processing
            callback: Function to call with result
            timeout: Request timeout in seconds
            request_id: Optional custom request ID

        Returns:
            Tuple of (success, request_id or error message)
        """
        with self._queue_lock:
            # Check queue capacity
            if len(self._queue) >= self.max_queue_size:
                return False, "Queue full - try again later"

            # Create request
            request = QueuedRequest(
                priority=priority.value,
                timestamp=time.time(),
                request_id=request_id or f"req_{int(time.time() * 1000)}_{len(self._queue)}",
                prompt=prompt,
                callback=callback,
                context=context or {},
                timeout=timeout or self.default_timeout
            )

            # Add to priority queue
            heapq.heappush(self._queue, request)

            # Update stats
            self._stats.total_requests += 1
            self._stats.queued_requests = len(self._queue)
            if len(self._queue) > self._stats.peak_queue_size:
                self._stats.peak_queue_size = len(self._queue)

            return True, request.request_id

    def enqueue_sync(
        self,
        prompt: str,
        priority: RequestPriority = RequestPriority.NORMAL,
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> str:
        """
        Synchronously enqueue and wait for result

        This blocks until the request is processed or times out.

        Args:
            prompt: The prompt to process
            priority: Request priority level
            context: Additional context
            timeout: Timeout in seconds

        Returns:
            The processed result

        Raises:
            TimeoutError: If request times out
            RuntimeError: If processing fails
        """
        result_event = threading.Event()
        result_container: Dict[str, Any] = {}

        def on_complete(result: Any, error: Optional[Exception] = None):
            result_container["result"] = result
            result_container["error"] = error
            result_event.set()

        success, req_id = self.enqueue(
            prompt=prompt,
            priority=priority,
            context=context,
            callback=on_complete,
            timeout=timeout
        )

        if not success:
            raise RuntimeError(f"Failed to enqueue request: {req_id}")

        # Wait for completion
        effective_timeout = timeout or self.default_timeout
        if not result_event.wait(timeout=effective_timeout + 10):  # Extra buffer
            raise TimeoutError(f"Request {req_id} timed out after {effective_timeout}s")

        if result_container.get("error"):
            raise result_container["error"]

        return result_container.get("result", "")

    async def enqueue_async(
        self,
        prompt: str,
        priority: RequestPriority = RequestPriority.NORMAL,
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> str:
        """
        Async version of enqueue_sync

        Args:
            prompt: The prompt to process
            priority: Request priority level
            context: Additional context
            timeout: Timeout in seconds

        Returns:
            The processed result
        """
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def on_complete(result: Any, error: Optional[Exception] = None):
            if error:
                loop.call_soon_threadsafe(future.set_exception, error)
            else:
                loop.call_soon_threadsafe(future.set_result, result)

        success, req_id = self.enqueue(
            prompt=prompt,
            priority=priority,
            context=context,
            callback=on_complete,
            timeout=timeout
        )

        if not success:
            raise RuntimeError(f"Failed to enqueue request: {req_id}")

        effective_timeout = timeout or self.default_timeout
        try:
            return await asyncio.wait_for(future, timeout=effective_timeout + 10)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request {req_id} timed out")

    def _process_next(self) -> bool:
        """
        Process the next request in queue

        Returns:
            True if a request was processed, False if queue empty
        """
        # Check if we can process more
        with self._active_lock:
            if len(self._active_requests) >= self.max_concurrent:
                return False

        # Get next request
        request: Optional[QueuedRequest] = None
        with self._queue_lock:
            if not self._queue:
                return False

            # Check for expired requests
            now = time.time()
            while self._queue:
                req = heapq.heappop(self._queue)
                if now - req.timestamp < req.timeout:
                    request = req
                    break
                else:
                    # Request expired
                    self._stats.failed_requests += 1
                    if req.callback:
                        req.callback(None, TimeoutError("Request expired in queue"))

            self._stats.queued_requests = len(self._queue)

        if not request:
            return False

        # Mark as active
        with self._active_lock:
            self._active_requests[request.request_id] = request
            self._stats.active_requests = len(self._active_requests)

        # Calculate wait time
        wait_time = time.time() - request.timestamp
        self._wait_times.append(wait_time)

        # Process request
        start_time = time.time()
        try:
            if self._process_func:
                result = self._process_func(
                    request.prompt,
                    **request.context
                )
            else:
                result = f"[No processor set] {request.prompt}"

            # Success
            processing_time = time.time() - start_time
            self._processing_times.append(processing_time)
            self._request_timestamps.append(time.time())
            self._stats.completed_requests += 1

            if request.callback:
                request.callback(result, None)

        except Exception as e:
            # Failure - maybe retry
            if request.retries < request.max_retries:
                request.retries += 1
                # Re-enqueue with slight delay penalty
                request.timestamp = time.time()
                with self._queue_lock:
                    heapq.heappush(self._queue, request)
                    self._stats.queued_requests = len(self._queue)
            else:
                self._stats.failed_requests += 1
                if request.callback:
                    request.callback(None, e)

        finally:
            # Remove from active
            with self._active_lock:
                self._active_requests.pop(request.request_id, None)
                self._stats.active_requests = len(self._active_requests)

        return True

    def start_processing(self) -> None:
        """Start the background queue processor"""
        if self._processor_thread and self._processor_thread.is_alive():
            return

        self._shutdown = False
        self._processor_thread = threading.Thread(
            target=self._processor_loop,
            daemon=True,
            name="RequestQueueProcessor"
        )
        self._processor_thread.start()

    def stop_processing(self) -> None:
        """Stop the background queue processor"""
        self._shutdown = True
        if self._processor_thread:
            self._processor_thread.join(timeout=5.0)

    def _processor_loop(self) -> None:
        """Main processing loop"""
        while not self._shutdown:
            try:
                # Try to process requests
                processed = False
                for _ in range(self.max_concurrent):
                    if self._process_next():
                        processed = True

                if not processed:
                    # No work to do, sleep a bit
                    time.sleep(0.1)

            except Exception as e:
                print(f"⚠️  Queue processor error: {e}")
                time.sleep(1.0)  # Back off on error

    def get_stats(self) -> QueueStats:
        """Get current queue statistics"""
        # Update computed stats
        if self._wait_times:
            self._stats.avg_wait_time = sum(self._wait_times) / len(self._wait_times)
        if self._processing_times:
            self._stats.avg_processing_time = sum(self._processing_times) / len(self._processing_times)

        # Calculate requests per minute
        now = time.time()
        recent = [t for t in self._request_timestamps if now - t < 60]
        self._stats.requests_per_minute = len(recent)

        return self._stats

    def get_queue_position(self, request_id: str) -> Optional[int]:
        """Get position of a request in the queue (1-indexed)"""
        with self._queue_lock:
            sorted_queue = sorted(self._queue)
            for i, req in enumerate(sorted_queue):
                if req.request_id == request_id:
                    return i + 1

        # Check if active
        with self._active_lock:
            if request_id in self._active_requests:
                return 0  # Currently processing

        return None  # Not found

    def cancel_request(self, request_id: str) -> bool:
        """
        Cancel a queued request

        Args:
            request_id: The request to cancel

        Returns:
            True if request was found and cancelled
        """
        with self._queue_lock:
            for i, req in enumerate(self._queue):
                if req.request_id == request_id:
                    self._queue.pop(i)
                    heapq.heapify(self._queue)
                    self._stats.queued_requests = len(self._queue)

                    if req.callback:
                        req.callback(None, RuntimeError("Request cancelled"))

                    return True

        return False

    def clear_queue(self) -> int:
        """
        Clear all queued requests

        Returns:
            Number of requests cleared
        """
        with self._queue_lock:
            count = len(self._queue)

            # Notify callbacks
            for req in self._queue:
                if req.callback:
                    req.callback(None, RuntimeError("Queue cleared"))

            self._queue.clear()
            self._stats.queued_requests = 0

            return count

    def is_healthy(self) -> bool:
        """Check if the queue is healthy (not overloaded)"""
        with self._queue_lock:
            # Unhealthy if queue is > 80% full
            if len(self._queue) > self.max_queue_size * 0.8:
                return False

        # Unhealthy if avg wait time > 30 seconds
        if self._stats.avg_wait_time > 30:
            return False

        return True


class AdaptiveQueue(RequestQueue):
    """
    Adaptive request queue that adjusts concurrency based on load

    Features:
    - Auto-scales concurrent requests based on success rate
    - Implements circuit breaker pattern
    - Provides backpressure signaling
    """

    def __init__(
        self,
        min_concurrent: int = 1,
        max_concurrent: int = 4,
        **kwargs
    ):
        super().__init__(max_concurrent=min_concurrent, **kwargs)
        self.min_concurrent = min_concurrent
        self._max_concurrent_limit = max_concurrent

        # Circuit breaker state
        self._failure_count = 0
        self._failure_threshold = 5
        self._circuit_open = False
        self._circuit_open_time: Optional[float] = None
        self._circuit_cooldown = 30.0  # seconds

        # Success tracking for adaptive scaling
        self._recent_results: deque = deque(maxlen=20)

    def _process_next(self) -> bool:
        """Override to add circuit breaker and adaptive scaling"""
        # Check circuit breaker
        if self._circuit_open:
            if time.time() - (self._circuit_open_time or 0) > self._circuit_cooldown:
                # Try to close circuit
                self._circuit_open = False
                self._failure_count = 0
                print("🔌 Circuit breaker reset - resuming processing")
            else:
                return False

        # Call parent implementation
        result = super()._process_next()

        # Track success/failure for adaptive scaling
        if result:
            self._adapt_concurrency()

        return result

    def _adapt_concurrency(self) -> None:
        """Adjust concurrency based on recent performance"""
        if len(self._recent_results) < 10:
            return

        success_rate = sum(self._recent_results) / len(self._recent_results)

        if success_rate > 0.95 and self.max_concurrent < self._max_concurrent_limit:
            # Scale up
            self.max_concurrent = min(self.max_concurrent + 1, self._max_concurrent_limit)
            print(f"📈 Scaling up to {self.max_concurrent} concurrent requests")
        elif success_rate < 0.7 and self.max_concurrent > self.min_concurrent:
            # Scale down
            self.max_concurrent = max(self.max_concurrent - 1, self.min_concurrent)
            print(f"📉 Scaling down to {self.max_concurrent} concurrent requests")

        # Circuit breaker
        if success_rate < 0.5:
            self._failure_count += 1
            if self._failure_count >= self._failure_threshold:
                self._circuit_open = True
                self._circuit_open_time = time.time()
                print("🔴 Circuit breaker OPEN - too many failures")

    def record_success(self) -> None:
        """Record a successful request"""
        self._recent_results.append(1)
        self._failure_count = max(0, self._failure_count - 1)

    def record_failure(self) -> None:
        """Record a failed request"""
        self._recent_results.append(0)
        self._failure_count += 1


# Singleton instance for global queue
_global_queue: Optional[RequestQueue] = None


def get_request_queue() -> RequestQueue:
    """Get the global request queue instance"""
    global _global_queue
    if _global_queue is None:
        _global_queue = AdaptiveQueue(
            min_concurrent=1,
            max_concurrent=3,
            max_queue_size=50,
            default_timeout=300.0
        )
    return _global_queue


def configure_queue(
    max_concurrent: int = 2,
    max_queue_size: int = 100,
    adaptive: bool = True
) -> RequestQueue:
    """
    Configure and return the global request queue

    Args:
        max_concurrent: Maximum concurrent requests
        max_queue_size: Maximum queue size
        adaptive: Use adaptive queue with auto-scaling

    Returns:
        Configured RequestQueue instance
    """
    global _global_queue

    if adaptive:
        _global_queue = AdaptiveQueue(
            min_concurrent=1,
            max_concurrent=max_concurrent,
            max_queue_size=max_queue_size
        )
    else:
        _global_queue = RequestQueue(
            max_concurrent=max_concurrent,
            max_queue_size=max_queue_size
        )

    return _global_queue
