"""
LLM-Based Task Classifier
Uses a small, fast LLM call to intelligently classify user requests.

Features:
- LLM-powered classification with keyword fallback
- Tool suggestions based on task type
- Classification caching for performance
- Async support for non-blocking operation
"""
import json
import re
import asyncio
import hashlib
from typing import Optional, Dict, Any, List, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from functools import lru_cache
import time


class TaskCategory(Enum):
    """Categories for task classification"""
    CODE_GENERATION = "code_generation"      # Write new code
    CODE_EXPLANATION = "code_explanation"    # Explain existing code
    CODE_REFACTORING = "code_refactoring"    # Improve/refactor code
    CODE_DEBUGGING = "code_debugging"        # Fix bugs/errors
    FILE_OPERATIONS = "file_operations"      # Read/write/modify files
    SHELL_COMMANDS = "shell_commands"        # Execute terminal commands
    GIT_OPERATIONS = "git_operations"        # Git-related tasks
    DOCKER_OPERATIONS = "docker_operations"  # Docker-related tasks
    PROJECT_SETUP = "project_setup"          # Create/scaffold projects
    DOCUMENTATION = "documentation"          # Write docs, comments
    TESTING = "testing"                      # Generate/run tests
    ARCHITECTURE = "architecture"            # Design, planning
    GENERAL_QA = "general_qa"                # General questions
    QUICK_ANSWER = "quick_answer"            # Simple, fast responses


class TaskComplexity(Enum):
    """Complexity levels for tasks"""
    TRIVIAL = "trivial"      # Single-step, instant
    SIMPLE = "simple"        # Few steps, quick
    MODERATE = "moderate"    # Multiple steps
    COMPLEX = "complex"      # Many steps, planning needed
    EXPERT = "expert"        # Requires deep analysis


@dataclass
class ClassificationResult:
    """Result of task classification"""
    category: TaskCategory
    complexity: TaskComplexity
    confidence: float
    suggested_model: str
    requires_tools: bool
    estimated_steps: int
    reasoning: str
    suggested_tools: List[str] = field(default_factory=list)
    classification_time_ms: float = 0.0
    used_llm: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "complexity": self.complexity.value,
            "confidence": self.confidence,
            "suggested_model": self.suggested_model,
            "requires_tools": self.requires_tools,
            "estimated_steps": self.estimated_steps,
            "reasoning": self.reasoning,
            "suggested_tools": self.suggested_tools,
            "classification_time_ms": self.classification_time_ms,
            "used_llm": self.used_llm
        }

    @property
    def primary_tool(self) -> Optional[str]:
        """Get the primary suggested tool"""
        return self.suggested_tools[0] if self.suggested_tools else None


# Tool suggestions by category
TOOL_SUGGESTIONS: Dict[TaskCategory, List[str]] = {
    TaskCategory.CODE_GENERATION: ["Write", "Edit"],
    TaskCategory.CODE_EXPLANATION: ["Read", "Grep"],
    TaskCategory.CODE_REFACTORING: ["Read", "Edit", "MultiEdit"],
    TaskCategory.CODE_DEBUGGING: ["Read", "Edit", "Bash"],
    TaskCategory.FILE_OPERATIONS: ["Read", "Write", "Edit", "Glob"],
    TaskCategory.SHELL_COMMANDS: ["Bash"],
    TaskCategory.GIT_OPERATIONS: ["Bash"],
    TaskCategory.DOCKER_OPERATIONS: ["Bash"],
    TaskCategory.PROJECT_SETUP: ["Write", "Bash", "Glob"],
    TaskCategory.DOCUMENTATION: ["Read", "Write", "Edit"],
    TaskCategory.TESTING: ["Write", "Bash"],
    TaskCategory.ARCHITECTURE: ["Read", "Glob", "Grep"],
    TaskCategory.GENERAL_QA: [],
    TaskCategory.QUICK_ANSWER: [],
}


class ClassificationCache:
    """Simple in-memory cache for classification results"""

    def __init__(self, max_size: int = 100, ttl_seconds: float = 300):
        self._cache: Dict[str, Tuple[ClassificationResult, float]] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds

    def _hash_task(self, task: str) -> str:
        """Create cache key from task"""
        return hashlib.md5(task.lower().strip().encode()).hexdigest()[:16]

    def get(self, task: str) -> Optional[ClassificationResult]:
        """Get cached result if valid"""
        key = self._hash_task(task)
        if key in self._cache:
            result, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return result
            del self._cache[key]
        return None

    def set(self, task: str, result: ClassificationResult):
        """Cache a classification result"""
        if len(self._cache) >= self._max_size:
            # Remove oldest entries
            sorted_items = sorted(self._cache.items(), key=lambda x: x[1][1])
            for key, _ in sorted_items[:self._max_size // 4]:
                del self._cache[key]

        key = self._hash_task(task)
        self._cache[key] = (result, time.time())

    def clear(self):
        """Clear the cache"""
        self._cache.clear()


class SmartTaskClassifier:
    """LLM-powered task classifier with fallback to keyword matching

    Features:
    - LLM-based classification with confidence scoring
    - Keyword-based fallback for fast classification
    - Classification caching for repeated queries
    - Tool suggestions based on task category
    - Async support for non-blocking operations
    """

    # Fast classification prompt - optimized for small models
    CLASSIFICATION_PROMPT = """Classify this task. Respond with ONLY a JSON object, no other text.

Task: {task}

JSON format:
{{
  "category": "code_generation|code_explanation|code_refactoring|code_debugging|file_operations|shell_commands|git_operations|docker_operations|project_setup|documentation|testing|architecture|general_qa|quick_answer",
  "complexity": "trivial|simple|moderate|complex|expert",
  "confidence": 0.0-1.0,
  "requires_tools": true|false,
  "steps": 1-10,
  "tools": ["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
  "reason": "brief explanation"
}}"""

    # Keyword patterns for fast fallback classification
    PATTERNS = {
        TaskCategory.CODE_GENERATION: [
            r"\b(write|create|generate|implement|build|make)\b.*\b(function|class|code|script|program|api|module)\b",
            r"\b(code|function|class|script)\b.*\b(for|that|to|which)\b"
        ],
        TaskCategory.CODE_EXPLANATION: [
            r"\b(explain|what does|how does|understand|clarify)\b.*\b(code|function|this|it)\b",
            r"\bwhat\s+is\b.*\b(doing|for|purpose)\b"
        ],
        TaskCategory.CODE_REFACTORING: [
            r"\b(refactor|improve|optimize|clean up|simplify|rewrite)\b",
            r"\bmake\b.*\b(better|cleaner|faster|readable)\b"
        ],
        TaskCategory.CODE_DEBUGGING: [
            r"\b(fix|debug|error|bug|issue|problem|broken|not working)\b",
            r"\bwhy\b.*\b(fail|error|crash|wrong)\b"
        ],
        TaskCategory.FILE_OPERATIONS: [
            r"\b(read|write|create|delete|modify|edit|save)\b.*\b(file|directory|folder)\b",
            r"\bfile\s+(content|path|name)\b"
        ],
        TaskCategory.SHELL_COMMANDS: [
            r"\b(run|execute|command|terminal|shell|bash)\b",
            r"\b(npm|pip|yarn|cargo|make|apt|brew)\b"
        ],
        TaskCategory.GIT_OPERATIONS: [
            r"\b(git|commit|push|pull|branch|merge|clone|diff|status)\b"
        ],
        TaskCategory.DOCKER_OPERATIONS: [
            r"\b(docker|container|image|compose|kubernetes|k8s)\b"
        ],
        TaskCategory.PROJECT_SETUP: [
            r"\b(setup|scaffold|initialize|bootstrap|create project|new project)\b",
            r"\b(fastapi|django|flask|next\.?js|react|vue)\b.*\b(project|app)\b"
        ],
        TaskCategory.DOCUMENTATION: [
            r"\b(document|docstring|readme|comment|annotate)\b",
            r"\badd\b.*\b(docs|documentation|comments)\b"
        ],
        TaskCategory.TESTING: [
            r"\b(test|unittest|pytest|jest|spec|coverage)\b",
            r"\bgenerate\b.*\btests?\b"
        ],
        TaskCategory.ARCHITECTURE: [
            r"\b(design|architect|plan|structure|organize)\b",
            r"\bhow\s+should\s+i\b"
        ],
        TaskCategory.QUICK_ANSWER: [
            r"^(what is|who is|when|where|how many|yes or no)\b",
            r"^.{0,30}\?$"  # Short questions
        ]
    }

    # Complexity indicators
    COMPLEXITY_PATTERNS = {
        TaskComplexity.TRIVIAL: [
            r"^(what is|define|list)\b",
            r"\bjust\b",
            r"\bsimple\b"
        ],
        TaskComplexity.SIMPLE: [
            r"\b(quick|brief|short)\b",
            r"\bone\b.*\b(function|file|class)\b"
        ],
        TaskComplexity.MODERATE: [
            r"\b(several|few|some)\b",
            r"\band\b.*\band\b"  # Multiple requirements
        ],
        TaskComplexity.COMPLEX: [
            r"\b(entire|whole|full|complete)\b.*\b(app|application|system)\b",
            r"\brefactor\b.*\b(entire|whole|all)\b"
        ],
        TaskComplexity.EXPERT: [
            r"\b(migrate|architecture|redesign|scale)\b",
            r"\bfrom scratch\b"
        ]
    }

    # Model recommendations by category and complexity
    MODEL_RECOMMENDATIONS = {
        (TaskCategory.QUICK_ANSWER, TaskComplexity.TRIVIAL): "fast",
        (TaskCategory.QUICK_ANSWER, TaskComplexity.SIMPLE): "fast",
        (TaskCategory.CODE_GENERATION, TaskComplexity.TRIVIAL): "fast",
        (TaskCategory.CODE_GENERATION, TaskComplexity.SIMPLE): "coding",
        (TaskCategory.CODE_GENERATION, TaskComplexity.MODERATE): "coding",
        (TaskCategory.CODE_GENERATION, TaskComplexity.COMPLEX): "coding",
        (TaskCategory.CODE_GENERATION, TaskComplexity.EXPERT): "reasoning",
        (TaskCategory.ARCHITECTURE, TaskComplexity.MODERATE): "reasoning",
        (TaskCategory.ARCHITECTURE, TaskComplexity.COMPLEX): "reasoning",
        (TaskCategory.ARCHITECTURE, TaskComplexity.EXPERT): "reasoning",
    }

    def __init__(self, llm_adapter=None, cache_enabled: bool = True):
        """Initialize classifier with optional LLM for smart classification

        Args:
            llm_adapter: LLMAdapter instance for LLM-based classification
            cache_enabled: Whether to cache classification results
        """
        self.llm = llm_adapter
        self._use_llm = llm_adapter is not None
        self._cache = ClassificationCache() if cache_enabled else None

    def classify(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        use_llm: bool = True,
        use_cache: bool = True
    ) -> ClassificationResult:
        """Classify a task using LLM or keyword matching

        Args:
            task: User's task/request
            context: Additional context (file paths, history, etc.)
            use_llm: Whether to attempt LLM classification
            use_cache: Whether to use cached results

        Returns:
            ClassificationResult with category, complexity, and recommendations
        """
        start_time = time.time()

        # Check cache first
        if use_cache and self._cache:
            cached = self._cache.get(task)
            if cached:
                return cached

        # Try LLM classification first if available and enabled
        result = None
        if use_llm and self._use_llm and self.llm:
            try:
                result = self._classify_with_llm(task)
                if result and result.confidence >= 0.7:
                    result.used_llm = True
            except Exception:
                result = None  # Fall back to keyword matching

        # Fall back to keyword matching
        if not result:
            result = self._classify_with_keywords(task, context)

        # Add timing and cache
        result.classification_time_ms = (time.time() - start_time) * 1000

        if use_cache and self._cache:
            self._cache.set(task, result)

        return result

    async def classify_async(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        use_llm: bool = True,
        use_cache: bool = True
    ) -> ClassificationResult:
        """Async version of classify - runs LLM call in thread pool

        Args:
            task: User's task/request
            context: Additional context
            use_llm: Whether to attempt LLM classification
            use_cache: Whether to use cached results

        Returns:
            ClassificationResult
        """
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.classify(task, context, use_llm, use_cache)
        )

    def _classify_with_llm(self, task: str) -> Optional[ClassificationResult]:
        """Classify task using LLM

        Args:
            task: User's task

        Returns:
            ClassificationResult or None if classification fails
        """
        from .llm_adapter import TaskType

        prompt = self.CLASSIFICATION_PROMPT.format(task=task)

        # Use fast model for classification
        response = self.llm.complete(prompt, task_type=TaskType.FAST, max_tokens=250)

        # Parse JSON response
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]+\}', response, re.DOTALL)
            if not json_match:
                return None

            data = json.loads(json_match.group())

            category = TaskCategory(data.get("category", "general_qa"))
            complexity = TaskComplexity(data.get("complexity", "moderate"))
            confidence = float(data.get("confidence", 0.8))
            requires_tools = bool(data.get("requires_tools", False))
            steps = int(data.get("steps", 1))
            reason = data.get("reason", "LLM classification")

            # Get tools from response or use defaults
            tools = data.get("tools", [])
            if not tools:
                tools = TOOL_SUGGESTIONS.get(category, [])

            # Get model recommendation
            suggested_model = self._get_model_recommendation(category, complexity)

            return ClassificationResult(
                category=category,
                complexity=complexity,
                confidence=confidence,
                suggested_model=suggested_model,
                requires_tools=requires_tools,
                estimated_steps=steps,
                reasoning=reason,
                suggested_tools=tools
            )

        except (json.JSONDecodeError, ValueError, KeyError):
            return None

    def _classify_with_keywords(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ClassificationResult:
        """Classify task using keyword patterns

        Args:
            task: User's task
            context: Additional context

        Returns:
            ClassificationResult
        """
        task_lower = task.lower()

        # Find best matching category
        best_category = TaskCategory.GENERAL_QA
        best_score = 0

        for category, patterns in self.PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, task_lower, re.IGNORECASE):
                    score += 1

            if score > best_score:
                best_score = score
                best_category = category

        # Determine complexity
        complexity = TaskComplexity.MODERATE
        for comp_level, patterns in self.COMPLEXITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, task_lower, re.IGNORECASE):
                    complexity = comp_level
                    break

        # Estimate based on task length and keywords
        word_count = len(task.split())
        if word_count < 10:
            complexity = TaskComplexity.SIMPLE
        elif word_count > 50:
            complexity = TaskComplexity.COMPLEX

        # Determine if tools are required
        requires_tools = best_category in [
            TaskCategory.FILE_OPERATIONS,
            TaskCategory.SHELL_COMMANDS,
            TaskCategory.GIT_OPERATIONS,
            TaskCategory.DOCKER_OPERATIONS,
            TaskCategory.PROJECT_SETUP,
            TaskCategory.TESTING
        ]

        # Estimate steps
        steps_map = {
            TaskComplexity.TRIVIAL: 1,
            TaskComplexity.SIMPLE: 2,
            TaskComplexity.MODERATE: 4,
            TaskComplexity.COMPLEX: 7,
            TaskComplexity.EXPERT: 10
        }
        estimated_steps = steps_map.get(complexity, 3)

        # Get model recommendation
        suggested_model = self._get_model_recommendation(best_category, complexity)

        # Calculate confidence based on match score
        confidence = min(0.5 + (best_score * 0.15), 0.95)

        # Get suggested tools for the category
        suggested_tools = TOOL_SUGGESTIONS.get(best_category, [])

        return ClassificationResult(
            category=best_category,
            complexity=complexity,
            confidence=confidence,
            suggested_model=suggested_model,
            requires_tools=requires_tools,
            estimated_steps=estimated_steps,
            reasoning=f"Keyword match (score: {best_score})",
            suggested_tools=suggested_tools
        )

    def _get_model_recommendation(
        self,
        category: TaskCategory,
        complexity: TaskComplexity
    ) -> str:
        """Get recommended model for task

        Args:
            category: Task category
            complexity: Task complexity

        Returns:
            Model name (fast, coding, reasoning, general)
        """
        # Check specific recommendations
        key = (category, complexity)
        if key in self.MODEL_RECOMMENDATIONS:
            return self.MODEL_RECOMMENDATIONS[key]

        # Default recommendations by category
        category_defaults = {
            TaskCategory.CODE_GENERATION: "coding",
            TaskCategory.CODE_EXPLANATION: "general",
            TaskCategory.CODE_REFACTORING: "coding",
            TaskCategory.CODE_DEBUGGING: "coding",
            TaskCategory.FILE_OPERATIONS: "tools",
            TaskCategory.SHELL_COMMANDS: "tools",
            TaskCategory.GIT_OPERATIONS: "tools",
            TaskCategory.DOCKER_OPERATIONS: "tools",
            TaskCategory.PROJECT_SETUP: "coding",
            TaskCategory.DOCUMENTATION: "general",
            TaskCategory.TESTING: "coding",
            TaskCategory.ARCHITECTURE: "reasoning",
            TaskCategory.GENERAL_QA: "general",
            TaskCategory.QUICK_ANSWER: "fast"
        }

        return category_defaults.get(category, "general")

    def get_task_summary(self, task: str) -> str:
        """Get a brief summary of task classification

        Args:
            task: User's task

        Returns:
            Human-readable summary
        """
        result = self.classify(task, use_llm=False)  # Fast keyword classification

        complexity_icons = {
            TaskComplexity.TRIVIAL: "⚡",
            TaskComplexity.SIMPLE: "🟢",
            TaskComplexity.MODERATE: "🟡",
            TaskComplexity.COMPLEX: "🟠",
            TaskComplexity.EXPERT: "🔴"
        }

        icon = complexity_icons.get(result.complexity, "⚪")

        return f"{icon} {result.category.value.replace('_', ' ').title()} ({result.complexity.value})"
