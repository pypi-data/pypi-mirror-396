"""
LLM Adapter with Multi-Model Orchestration
Handles communication with local LLMs via Ollama using LiteLLM for routing

Features:
- Intelligent task classification and model routing
- Request queuing under load with priority support
- Cognitive architecture integration (5 layers)
- Fallback chain for model failures
"""
import sys
import time
from typing import List, Dict, Any, Optional, Union
from enum import Enum

try:
    from litellm import completion, acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("Warning: litellm not installed. Install with: pip install litellm")

from .config import get_config

# Import request queue system
try:
    from .request_queue import (
        RequestQueue, AdaptiveQueue, RequestPriority,
        get_request_queue, configure_queue, QueueStats
    )
    QUEUE_AVAILABLE = True
except ImportError:
    QUEUE_AVAILABLE = False

# Import cognitive router (Layer 1 of Cognitive Architecture)
try:
    from .cognitive.router import IntentAnalyzer, IntelligentRouter, RoutingDecision
    COGNITIVE_ROUTER_AVAILABLE = True
except ImportError:
    COGNITIVE_ROUTER_AVAILABLE = False

# Import multi-agent council (Layer 3 of Cognitive Architecture)
try:
    from .cognitive.council import MultiAgentCouncil
    COUNCIL_AVAILABLE = True
except ImportError:
    COUNCIL_AVAILABLE = False


class TaskType(Enum):
    """Types of tasks for model routing"""
    REASONING = "reasoning"      # Complex logic, planning, math
    CODING = "coding"            # Code generation, debugging
    TOOLS = "tools"              # File ops, command execution
    GENERAL = "general"          # Q&A, explanations
    FAST = "fast"                # Quick responses


class TaskClassifier:
    """Classifies user requests to determine appropriate model"""
    
    # Keywords that indicate specific task types
    REASONING_KEYWORDS = [
        "prove", "reason", "explain why", "logic", "analyze", "plan",
        "design", "architecture", "strategy", "solve", "calculate",
        "mathematical", "theorem", "proof", "deduce"
    ]
    
    CODING_KEYWORDS = [
        "code", "function", "class", "debug", "refactor", "implement",
        "write a", "create a", "build a", "fix", "bug", "error",
        "optimize", "algorithm", "program", "script", "api"
    ]
    
    TOOLS_KEYWORDS = [
        "create file", "write file", "read file", "delete file",
        "run command", "execute", "install", "git", "docker",
        "npm", "pip", "deploy", "build", "compile"
    ]
    
    FAST_KEYWORDS = [
        "quick", "simple", "just", "only", "briefly", "short"
    ]
    
    @classmethod
    def classify(cls, prompt: str) -> TaskType:
        """Classify a prompt to determine task type
        
        Args:
            prompt: User's input prompt
        
        Returns:
            TaskType enum value
        """
        prompt_lower = prompt.lower()
        
        # Count keyword matches for each category
        reasoning_score = sum(1 for kw in cls.REASONING_KEYWORDS if kw in prompt_lower)
        coding_score = sum(1 for kw in cls.CODING_KEYWORDS if kw in prompt_lower)
        tools_score = sum(1 for kw in cls.TOOLS_KEYWORDS if kw in prompt_lower)
        fast_score = sum(1 for kw in cls.FAST_KEYWORDS if kw in prompt_lower)
        
        # Determine task type based on scores
        if fast_score > 0 and len(prompt.split()) < 20:
            return TaskType.FAST
        
        if tools_score > 0:
            return TaskType.TOOLS
        
        if coding_score > reasoning_score and coding_score > 0:
            return TaskType.CODING
        
        if reasoning_score > 0:
            return TaskType.REASONING
        
        return TaskType.GENERAL
    
    @classmethod
    def classify_with_context(cls, prompt: str, context: Optional[Dict[str, Any]] = None) -> TaskType:
        """Classify with additional context
        
        Args:
            prompt: User's input prompt
            context: Additional context (e.g., file paths, previous task type)
        
        Returns:
            TaskType enum value
        """
        # Basic classification
        task_type = cls.classify(prompt)
        
        # Refine based on context
        if context:
            # If we're in a coding session, prefer coding model
            if context.get("previous_task") == TaskType.CODING and task_type == TaskType.GENERAL:
                task_type = TaskType.CODING
            
            # If file paths are mentioned, likely tools/coding
            if context.get("file_paths") and task_type == TaskType.GENERAL:
                task_type = TaskType.CODING
        
        return task_type


class LLMAdapter:
    """Adapter for interacting with LLMs via LiteLLM and Ollama"""

    def __init__(self, skip_health_check: bool = False):
        """Initialize the LLM adapter

        Args:
            skip_health_check: Skip Ollama connectivity check (useful for testing)
        """
        self.config = get_config()
        self.conversation_history: List[Dict[str, str]] = []
        self._ollama_available = False

        if not LITELLM_AVAILABLE:
            raise ImportError(
                "LiteLLM is required but not installed. "
                "Install with: pip install litellm"
            )

        if not skip_health_check:
            self._check_ollama_connection()

    def _check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible

        Returns:
            True if Ollama is available
        """
        import urllib.request
        import urllib.error

        base_url = self.config.get("ollama.base_url", "http://localhost:11434")
        health_url = f"{base_url}/api/tags"

        try:
            with urllib.request.urlopen(health_url, timeout=5) as response:
                if response.status == 200:
                    self._ollama_available = True
                    return True
        except urllib.error.URLError as e:
            print(f"⚠️  Warning: Cannot connect to Ollama at {base_url}")
            print(f"   Error: {e.reason}")
            print(f"   Please ensure Ollama is running: ollama serve")
            self._ollama_available = False
        except Exception as e:
            print(f"⚠️  Warning: Ollama health check failed: {e}")
            self._ollama_available = False

        return self._ollama_available

    def is_ollama_available(self) -> bool:
        """Check if Ollama is available

        Returns:
            True if Ollama was reachable during init or last check
        """
        return self._ollama_available
    
    def _get_model_for_task(self, task_type: TaskType) -> str:
        """Get the appropriate model for a task type
        
        Args:
            task_type: Type of task
        
        Returns:
            Model identifier for Ollama
        """
        model_name = self.config.get_model_for_task(task_type.value)
        return f"ollama/{model_name}"
    
    def _build_messages(self, prompt: str, system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """Build message list for the LLM
        
        Args:
            prompt: User's prompt
            system_prompt: Optional system prompt
        
        Returns:
            List of message dictionaries
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history (last N messages)
        max_history = self.config.get("memory.conversation_history", 10)
        messages.extend(self.conversation_history[-max_history:])
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def complete(
        self,
        prompt: str,
        task_type: Optional[TaskType] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        model: Optional[str] = None
    ) -> str:
        """Get completion from LLM

        Args:
            prompt: User's prompt
            task_type: Type of task (auto-detected if None)
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            model: Optional specific model to use (overrides task_type routing)

        Returns:
            LLM response text
        """
        # Use explicit model if provided, otherwise route by task type
        if model:
            pass  # Use the provided model directly
        else:
            # Auto-classify if task type not provided
            if task_type is None:
                task_type = TaskClassifier.classify(prompt)
            # Get appropriate model
            model = self._get_model_for_task(task_type)

        # Build messages
        messages = self._build_messages(prompt, system_prompt)

        # Get Ollama base URL and retry config
        api_base = self.config.get("ollama.base_url")
        max_retries = self.config.get("execution.max_retries", 3)

        last_error = None
        for attempt in range(max_retries):
            try:
                if stream:
                    return self._stream_completion(model, messages, temperature, max_tokens, api_base, prompt)
                else:
                    response = completion(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        api_base=api_base
                    )

                    response_text = response.choices[0].message.content

                    # Update conversation history
                    self.conversation_history.append({"role": "user", "content": prompt})
                    self.conversation_history.append({"role": "assistant", "content": response_text})

                    return response_text

            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Identify recoverable vs non-recoverable errors
                is_network_error = any(x in error_str for x in [
                    "connection", "timeout", "refused", "reset", "network",
                    "503", "502", "504", "429", "rate limit", "overloaded"
                ])

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds

                    if is_network_error:
                        print(f"⚠️  Network error (attempt {attempt + 1}/{max_retries}): {e}")
                        print(f"   This may be a temporary issue. Retrying in {wait_time} seconds...")
                    else:
                        print(f"⚠️  LLM request failed (attempt {attempt + 1}/{max_retries}): {e}")
                        print(f"   Retrying in {wait_time} seconds...")

                    time.sleep(wait_time)
                    continue

        # Provide helpful error message based on error type
        error_str = str(last_error).lower()
        if "connection refused" in error_str or "cannot connect" in error_str:
            raise RuntimeError(
                f"Cannot connect to Ollama at {api_base}. "
                f"Please ensure Ollama is running: 'ollama serve'"
            )
        elif "timeout" in error_str:
            raise RuntimeError(
                f"Request timed out after {max_retries} attempts. "
                f"The model may be loading or the server is overloaded."
            )
        elif "429" in error_str or "rate limit" in error_str:
            raise RuntimeError(
                f"Rate limited after {max_retries} attempts. "
                f"Please wait a moment before trying again."
            )

        raise RuntimeError(f"LLM completion failed after {max_retries} attempts: {last_error}")
    
    def _stream_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        api_base: str,
        original_prompt: str
    ) -> str:
        """Stream completion from LLM and print chunks in real-time

        Args:
            model: Model identifier
            messages: Message list
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            api_base: Ollama base URL
            original_prompt: Original user prompt for history

        Returns:
            Complete response text
        """
        response = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_base=api_base,
            stream=True
        )

        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                # Print chunk in real-time
                sys.stdout.write(content)
                sys.stdout.flush()

        # Print newline after streaming completes
        print()

        # Update conversation history after streaming completes
        self.conversation_history.append({"role": "user", "content": original_prompt})
        self.conversation_history.append({"role": "assistant", "content": full_response})

        return full_response
    
    def complete_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        task_type: Optional[TaskType] = None
    ) -> Dict[str, Any]:
        """Get completion with tool/function calling support
        
        Args:
            prompt: User's prompt
            tools: List of available tools (function definitions)
            task_type: Type of task (auto-detected if None)
        
        Returns:
            Response with potential tool calls
        """
        # Use tools-optimized model
        if task_type is None:
            task_type = TaskType.TOOLS
        
        model = self._get_model_for_task(task_type)
        messages = self._build_messages(prompt)
        api_base = self.config.get("ollama.base_url")
        
        try:
            response = completion(
                model=model,
                messages=messages,
                tools=tools,
                api_base=api_base
            )
            
            return {
                "content": response.choices[0].message.content,
                "tool_calls": getattr(response.choices[0].message, "tool_calls", None)
            }
        
        except Exception as e:
            raise RuntimeError(f"LLM completion with tools failed: {e}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        task_type: Optional[TaskType] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Chat with the LLM using a message list (for agent use)

        This method is designed for the Agent class which manages its own
        conversation history and passes complete message lists.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            task_type: Type of task (defaults to TOOLS for agent use)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            LLM response text
        """
        # Default to TOOLS task type for agent operations
        if task_type is None:
            task_type = TaskType.TOOLS

        # Get appropriate model
        model = self._get_model_for_task(task_type)
        api_base = self.config.get("ollama.base_url")
        max_retries = self.config.get("execution.max_retries", 3)

        last_error = None
        for attempt in range(max_retries):
            try:
                response = completion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_base=api_base
                )

                return response.choices[0].message.content

            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Identify recoverable errors
                is_recoverable = any(x in error_str for x in [
                    "connection", "timeout", "refused", "reset", "network",
                    "503", "502", "504", "429", "rate limit", "overloaded"
                ])

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt

                    if is_recoverable:
                        print(f"⚠️  Network error (attempt {attempt + 1}/{max_retries}): {e}")
                        print(f"   Retrying in {wait_time} seconds...")
                    else:
                        print(f"⚠️  LLM request failed (attempt {attempt + 1}/{max_retries}): {e}")
                        print(f"   Retrying in {wait_time} seconds...")

                    time.sleep(wait_time)
                    continue

        # Provide helpful error message
        error_str = str(last_error).lower()
        if "connection refused" in error_str or "cannot connect" in error_str:
            raise RuntimeError(
                f"Cannot connect to Ollama at {api_base}. "
                f"Please ensure Ollama is running: 'ollama serve'"
            )
        elif "timeout" in error_str:
            raise RuntimeError(
                f"Request timed out. The model may be loading or overloaded."
            )

        raise RuntimeError(f"LLM chat failed after {max_retries} attempts: {last_error}")

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []

    def get_model_info(self, task_type: TaskType) -> Dict[str, str]:
        """Get information about the model used for a task type
        
        Args:
            task_type: Type of task
        
        Returns:
            Dictionary with model information
        """
        model = self._get_model_for_task(task_type)
        return {
            "task_type": task_type.value,
            "model": model,
            "base_url": self.config.get("ollama.base_url")
        }

    # ==================== Cognitive Architecture Integration ====================

    def _init_cognitive_router(self) -> None:
        """Initialize the cognitive router (lazy initialization)"""
        if not hasattr(self, '_cognitive_router'):
            self._cognitive_router = None
            self._intent_analyzer = None

        if self._cognitive_router is None and COGNITIVE_ROUTER_AVAILABLE:
            self._intent_analyzer = IntentAnalyzer(self)
            self._cognitive_router = IntelligentRouter(self._intent_analyzer)

    @property
    def cognitive_router(self) -> Optional["IntelligentRouter"]:
        """Get the cognitive router (lazy initialization)"""
        self._init_cognitive_router()
        return self._cognitive_router

    @property
    def has_cognitive_routing(self) -> bool:
        """Check if cognitive routing is available"""
        return COGNITIVE_ROUTER_AVAILABLE

    def _get_or_create_council(self) -> "MultiAgentCouncil":
        """Get or create the multi-agent council (lazy initialization)"""
        if not hasattr(self, '_council'):
            self._council = None
        if self._council is None and COUNCIL_AVAILABLE:
            self._council = MultiAgentCouncil(llm_adapter=self)
        return self._council

    def complete_with_routing(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        use_cognitive: bool = True
    ) -> str:
        """Complete with intelligent routing from cognitive architecture

        This is the new primary method for completions that uses Layer 1
        of the cognitive architecture for intelligent model selection.

        Args:
            prompt: User's prompt
            context: Context for routing decisions (cwd, recent_files, etc.)
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            use_cognitive: Whether to use cognitive routing (falls back to basic if False)

        Returns:
            LLM response text
        """
        # Try cognitive routing first
        if use_cognitive and self.has_cognitive_routing:
            self._init_cognitive_router()

            # Get routing decision (sync version for now)
            decision = self._cognitive_router.route_sync(prompt, context)

            # Log routing decision
            print(f"🧭 {decision.reasoning}")

            # Use the model selected by cognitive router
            model = decision.primary_model

            # If council should be used, activate multi-agent deliberation (Layer 3)
            if decision.should_use_council and COUNCIL_AVAILABLE:
                print(f"   📋 Convening council with agents: {decision.agents_to_involve}")
                try:
                    council = self._get_or_create_council()
                    session = council.convene(
                        task_description=prompt,
                        task_category=decision.intent.primary_category.value if decision.intent else "general",
                        complexity=decision.intent.complexity if decision.intent else 0.5,
                        context=context,
                        agents=decision.agents_to_involve,
                        parallel=True
                    )

                    if session.consensus:
                        print(f"   ✅ Council consensus reached (confidence: {session.consensus_confidence:.0%})")
                        # Combine consensus with model response for best result
                        # The council provides analysis, the model generates final response
                        enhanced_prompt = f"{prompt}\n\n[Council Analysis]\n{session.consensus}"
                        messages = self._build_messages(enhanced_prompt, system_prompt)
                    else:
                        print(f"   ⚠️ Council did not reach consensus, using standard completion")
                        messages = self._build_messages(prompt, system_prompt)
                except Exception as e:
                    print(f"   ⚠️ Council error: {e}, falling back to standard completion")
                    messages = self._build_messages(prompt, system_prompt)
            else:
                # Build messages for standard completion
                messages = self._build_messages(prompt, system_prompt)

            api_base = self.config.get("ollama.base_url")

            try:
                if stream:
                    return self._stream_completion_with_model(
                        model, messages, temperature, max_tokens, api_base, prompt
                    )
                else:
                    response = completion(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        api_base=api_base
                    )

                    response_text = response.choices[0].message.content

                    # Update conversation history
                    self.conversation_history.append({"role": "user", "content": prompt})
                    self.conversation_history.append({"role": "assistant", "content": response_text})

                    return response_text

            except Exception as e:
                # Fallback to decision's fallback model
                if decision.fallback_model:
                    print(f"⚠️  Primary model failed, trying fallback: {decision.fallback_model}")
                    return self._complete_with_fallback(
                        decision.fallback_model, messages, temperature,
                        max_tokens, api_base, prompt, stream
                    )
                raise

        # Fallback to basic routing
        return self.complete(
            prompt=prompt,
            task_type=None,  # Auto-classify
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )

    def _stream_completion_with_model(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        api_base: str,
        original_prompt: str
    ) -> str:
        """Stream completion with specific model (for cognitive routing)"""
        response = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_base=api_base,
            stream=True
        )

        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                sys.stdout.write(content)
                sys.stdout.flush()

        print()  # Newline after streaming

        self.conversation_history.append({"role": "user", "content": original_prompt})
        self.conversation_history.append({"role": "assistant", "content": full_response})

        return full_response

    def _complete_with_fallback(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        api_base: str,
        original_prompt: str,
        stream: bool
    ) -> str:
        """Complete with a fallback model"""
        if stream:
            return self._stream_completion_with_model(
                model, messages, temperature, max_tokens, api_base, original_prompt
            )

        response = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_base=api_base
        )

        response_text = response.choices[0].message.content
        self.conversation_history.append({"role": "user", "content": original_prompt})
        self.conversation_history.append({"role": "assistant", "content": response_text})

        return response_text

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get statistics about cognitive routing decisions"""
        if not self.has_cognitive_routing or self._cognitive_router is None:
            return {"error": "Cognitive routing not available"}
        return self._cognitive_router.get_routing_stats()

    async def complete_async(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Async completion for cognitive router use

        Args:
            prompt: The prompt
            model: Specific model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Response text
        """
        if model is None:
            model = "ollama/qwen2.5:32b"

        messages = [{"role": "user", "content": prompt}]
        api_base = self.config.get("ollama.base_url")

        try:
            response = await acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                api_base=api_base
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Async completion failed: {e}")

    # ==================== Request Queue Integration ====================

    def _init_request_queue(self) -> None:
        """Initialize the request queue (lazy initialization)"""
        if not hasattr(self, '_request_queue'):
            self._request_queue = None

        if self._request_queue is None and QUEUE_AVAILABLE:
            self._request_queue = get_request_queue()
            # Set the processor function
            self._request_queue.set_processor(self._process_queued_request)
            self._request_queue.start_processing()

    @property
    def request_queue(self) -> Optional["RequestQueue"]:
        """Get the request queue (lazy initialization)"""
        self._init_request_queue()
        return self._request_queue

    @property
    def has_queue(self) -> bool:
        """Check if request queuing is available"""
        return QUEUE_AVAILABLE

    def _process_queued_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_cognitive: bool = True,
        **kwargs
    ) -> str:
        """
        Process a request from the queue

        This is the function called by the queue processor.
        """
        if use_cognitive and self.has_cognitive_routing:
            return self.complete_with_routing(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                use_cognitive=True
            )
        else:
            return self.complete(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

    def enqueue_completion(
        self,
        prompt: str,
        priority: str = "normal",
        context: Optional[Dict[str, Any]] = None,
        callback: Optional[callable] = None,
        timeout: Optional[float] = None
    ) -> tuple:
        """
        Enqueue a completion request for async processing

        Args:
            prompt: The prompt to process
            priority: Priority level (critical, high, normal, low, batch)
            context: Additional context for processing
            callback: Function to call with result (result, error)
            timeout: Request timeout in seconds

        Returns:
            Tuple of (success, request_id or error message)
        """
        if not self.has_queue:
            return False, "Request queuing not available"

        self._init_request_queue()

        # Map priority string to enum
        priority_map = {
            "critical": RequestPriority.CRITICAL,
            "high": RequestPriority.HIGH,
            "normal": RequestPriority.NORMAL,
            "low": RequestPriority.LOW,
            "batch": RequestPriority.BATCH
        }
        req_priority = priority_map.get(priority.lower(), RequestPriority.NORMAL)

        return self._request_queue.enqueue(
            prompt=prompt,
            priority=req_priority,
            context=context or {},
            callback=callback,
            timeout=timeout
        )

    def complete_queued(
        self,
        prompt: str,
        priority: str = "normal",
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> str:
        """
        Synchronously enqueue and wait for completion

        This is useful when you want queue priority but still need
        to wait for the result.

        Args:
            prompt: The prompt to process
            priority: Priority level (critical, high, normal, low, batch)
            context: Additional context for processing
            timeout: Request timeout in seconds

        Returns:
            The completion result

        Raises:
            TimeoutError: If request times out
            RuntimeError: If processing fails or queue unavailable
        """
        if not self.has_queue:
            # Fallback to direct completion if queue not available
            return self.complete_with_routing(prompt)

        self._init_request_queue()

        # Map priority string to enum
        priority_map = {
            "critical": RequestPriority.CRITICAL,
            "high": RequestPriority.HIGH,
            "normal": RequestPriority.NORMAL,
            "low": RequestPriority.LOW,
            "batch": RequestPriority.BATCH
        }
        req_priority = priority_map.get(priority.lower(), RequestPriority.NORMAL)

        return self._request_queue.enqueue_sync(
            prompt=prompt,
            priority=req_priority,
            context=context or {},
            timeout=timeout
        )

    async def complete_queued_async(
        self,
        prompt: str,
        priority: str = "normal",
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> str:
        """
        Async version of complete_queued

        Args:
            prompt: The prompt to process
            priority: Priority level (critical, high, normal, low, batch)
            context: Additional context for processing
            timeout: Request timeout in seconds

        Returns:
            The completion result
        """
        if not self.has_queue:
            # Fallback to async completion
            return await self.complete_async(prompt)

        self._init_request_queue()

        # Map priority string to enum
        priority_map = {
            "critical": RequestPriority.CRITICAL,
            "high": RequestPriority.HIGH,
            "normal": RequestPriority.NORMAL,
            "low": RequestPriority.LOW,
            "batch": RequestPriority.BATCH
        }
        req_priority = priority_map.get(priority.lower(), RequestPriority.NORMAL)

        return await self._request_queue.enqueue_async(
            prompt=prompt,
            priority=req_priority,
            context=context or {},
            timeout=timeout
        )

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get request queue statistics"""
        if not self.has_queue:
            return {"error": "Request queue not available"}

        # Initialize if needed
        self._init_request_queue()
        if self._request_queue is None:
            return {"error": "Request queue not initialized"}

        stats = self._request_queue.get_stats()
        return stats.to_dict()

    def get_queue_position(self, request_id: str) -> Optional[int]:
        """Get position of a request in the queue"""
        if not self.has_queue:
            return None
        if not hasattr(self, '_request_queue') or self._request_queue is None:
            return None
        return self._request_queue.get_queue_position(request_id)

    def cancel_request(self, request_id: str) -> bool:
        """Cancel a queued request"""
        if not self.has_queue:
            return False
        if not hasattr(self, '_request_queue') or self._request_queue is None:
            return False
        return self._request_queue.cancel_request(request_id)

    def is_queue_healthy(self) -> bool:
        """Check if the queue is healthy"""
        if not self.has_queue:
            return True  # No queue = no backpressure issues
        if not hasattr(self, '_request_queue') or self._request_queue is None:
            return True  # Queue not initialized yet = healthy
        return self._request_queue.is_healthy()

    def shutdown_queue(self) -> None:
        """Shutdown the request queue"""
        if hasattr(self, '_request_queue') and self._request_queue is not None:
            self._request_queue.stop_processing()
