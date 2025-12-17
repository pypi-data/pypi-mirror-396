"""
NC1709 Cognitive Architecture - Layer 1: Intelligent Router

Replaces keyword-based task classification with LLM-powered intent analysis.
Uses a fast model to understand user intent and route to the best model/agent.

Features:
- LLM-based intent detection (not keywords)
- 18 task categories for fine-grained routing
- Confidence scoring
- Multi-model routing with fallbacks
- Council activation for complex tasks
"""

import json
import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from ..llm_adapter import LLMAdapter


class TaskCategory(Enum):
    """Expanded task categories for intelligent routing (18 vs old 5)"""

    # Complex reasoning tasks
    REASONING = "reasoning"
    DEBUGGING = "debugging"
    SECURITY = "security"
    PERFORMANCE = "performance"

    # Code-focused tasks
    CODE_GENERATION = "code_generation"
    CODE_MODIFICATION = "code_modification"
    CODE_REVIEW = "code_review"
    REFACTORING = "refactoring"
    TESTING = "testing"

    # Documentation & explanation
    EXPLANATION = "explanation"
    DOCUMENTATION = "documentation"

    # Operations
    DEVOPS = "devops"
    DATABASE = "database"
    FILE_OPERATIONS = "file_operations"
    COMMAND_EXECUTION = "command_execution"
    GIT_OPERATIONS = "git_operations"
    PROJECT_SETUP = "project_setup"

    # Quick tasks
    QUICK_ANSWER = "quick_answer"


@dataclass
class IntentAnalysis:
    """Result of analyzing user intent"""

    primary_category: TaskCategory
    secondary_categories: List[TaskCategory] = field(default_factory=list)
    confidence: float = 0.7  # 0.0 to 1.0
    complexity: float = 0.5  # 0.0 to 1.0 (how complex is this task)
    requires_context: bool = True  # Does this need codebase context?
    requires_execution: bool = False  # Does this need to run commands?
    requires_file_access: bool = True  # Does this need to read/write files?
    estimated_tokens: int = 1000  # Rough estimate of response size
    key_entities: List[str] = field(default_factory=list)  # Files, functions, classes mentioned
    user_goal: str = ""  # One-sentence summary of what user wants
    analysis_time_ms: float = 0  # How long analysis took


@dataclass
class RoutingDecision:
    """Final routing decision"""

    primary_model: str
    fallback_model: Optional[str] = None
    should_use_council: bool = False  # Use multi-agent for complex tasks
    context_budget: int = 4000  # How many tokens for context
    agents_to_involve: List[str] = field(default_factory=list)  # Which council agents
    confidence: float = 0.7
    reasoning: str = ""  # Why this routing was chosen
    intent: Optional[IntentAnalysis] = None  # The underlying analysis


class IntentAnalyzer:
    """
    Uses a fast model to analyze user intent before routing.
    This replaces the keyword-based TaskClassifier.
    """

    ANALYSIS_PROMPT = '''Analyze this user request and respond with JSON only.

User Request: {prompt}

Current Context:
- Working Directory: {cwd}
- Recent Files: {recent_files}
- Recent Actions: {recent_actions}

Analyze and respond with this exact JSON structure:
{{
    "primary_category": "<one of: reasoning, code_generation, code_modification, code_review, debugging, explanation, refactoring, testing, documentation, devops, database, security, performance, quick_answer, file_operations, command_execution, git_operations, project_setup>",
    "secondary_categories": ["<list of other relevant categories>"],
    "confidence": <0.0-1.0>,
    "complexity": <0.0-1.0>,
    "requires_context": <true/false>,
    "requires_execution": <true/false>,
    "requires_file_access": <true/false>,
    "estimated_tokens": <number>,
    "key_entities": ["<files, functions, classes mentioned>"],
    "user_goal": "<one sentence summary>"
}}

Respond with JSON only, no other text.'''

    def __init__(self, llm_adapter: Optional["LLMAdapter"] = None):
        self.llm = llm_adapter
        self.analysis_model = "ollama/qwen2.5-coder:7b"  # Fast model for analysis
        self._cache: Dict[str, IntentAnalysis] = {}  # Simple cache
        self._cache_ttl = 300  # 5 minutes

    def set_llm_adapter(self, llm_adapter: "LLMAdapter") -> None:
        """Set the LLM adapter (for deferred initialization)"""
        self.llm = llm_adapter

    async def analyze(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentAnalysis:
        """Analyze user intent using LLM"""

        start_time = datetime.now()
        context = context or {}

        # Check cache first (simple string hash)
        cache_key = f"{prompt[:100]}:{context.get('cwd', '')}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            return cached

        # If no LLM available, use fallback
        if self.llm is None:
            return self._fallback_analysis(prompt)

        analysis_prompt = self.ANALYSIS_PROMPT.format(
            prompt=prompt,
            cwd=context.get("cwd", "unknown"),
            recent_files=str(context.get("recent_files", [])[:5]),
            recent_actions=str(context.get("recent_actions", [])[:3])
        )

        try:
            # Call fast model for analysis
            response = await self._call_llm(analysis_prompt)

            # Parse JSON response
            data = self._parse_json_response(response)

            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

            result = IntentAnalysis(
                primary_category=TaskCategory(data.get("primary_category", "code_generation")),
                secondary_categories=[
                    TaskCategory(c) for c in data.get("secondary_categories", [])
                    if c in [e.value for e in TaskCategory]
                ],
                confidence=float(data.get("confidence", 0.7)),
                complexity=float(data.get("complexity", 0.5)),
                requires_context=bool(data.get("requires_context", True)),
                requires_execution=bool(data.get("requires_execution", False)),
                requires_file_access=bool(data.get("requires_file_access", True)),
                estimated_tokens=int(data.get("estimated_tokens", 1000)),
                key_entities=data.get("key_entities", []),
                user_goal=data.get("user_goal", prompt[:100]),
                analysis_time_ms=elapsed_ms
            )

            # Cache the result
            self._cache[cache_key] = result

            return result

        except Exception as e:
            # Fallback to keyword-based analysis
            return self._fallback_analysis(prompt)

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM for analysis"""
        if hasattr(self.llm, 'complete_async'):
            return await self.llm.complete_async(
                prompt,
                model=self.analysis_model,
                temperature=0.1,
                max_tokens=500
            )
        elif hasattr(self.llm, 'complete'):
            # Sync fallback
            return self.llm.complete(
                prompt,
                model=self.analysis_model,
                temperature=0.1,
                max_tokens=500
            )
        else:
            raise RuntimeError("LLM adapter has no complete method")

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling various formats"""
        # Try direct JSON parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding JSON object in text
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Return empty dict if all parsing fails
        return {}

    def _fallback_analysis(self, prompt: str) -> IntentAnalysis:
        """Fallback keyword-based analysis if LLM fails"""
        prompt_lower = prompt.lower()

        # Keyword patterns for each category
        category_keywords = {
            TaskCategory.EXPLANATION: ["explain", "what is", "what does", "how does", "why", "describe"],
            TaskCategory.DEBUGGING: ["bug", "error", "fix", "broken", "crash", "issue", "problem", "debug"],
            TaskCategory.CODE_GENERATION: ["write", "create", "implement", "build", "generate", "make", "add"],
            TaskCategory.CODE_MODIFICATION: ["change", "modify", "update", "edit", "alter"],
            TaskCategory.REFACTORING: ["refactor", "clean", "improve", "restructure", "reorganize"],
            TaskCategory.TESTING: ["test", "unittest", "pytest", "spec", "coverage"],
            TaskCategory.CODE_REVIEW: ["review", "check", "audit", "inspect"],
            TaskCategory.DOCUMENTATION: ["document", "docstring", "readme", "comment"],
            TaskCategory.SECURITY: ["security", "vulnerability", "auth", "password", "encrypt"],
            TaskCategory.PERFORMANCE: ["optimize", "performance", "speed", "slow", "memory", "efficient"],
            TaskCategory.GIT_OPERATIONS: ["git", "commit", "push", "pull", "branch", "merge"],
            TaskCategory.DEVOPS: ["docker", "deploy", "ci/cd", "kubernetes", "container"],
            TaskCategory.DATABASE: ["sql", "database", "query", "migration", "schema"],
            TaskCategory.FILE_OPERATIONS: ["file", "read", "write", "copy", "move", "delete"],
            TaskCategory.COMMAND_EXECUTION: ["run", "execute", "shell", "terminal", "command"],
            TaskCategory.PROJECT_SETUP: ["setup", "init", "scaffold", "bootstrap", "new project"],
            TaskCategory.QUICK_ANSWER: ["?", "what", "which", "where", "when"],
        }

        # Find matching category
        category = TaskCategory.CODE_GENERATION  # Default
        for cat, keywords in category_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                category = cat
                break

        # Estimate complexity based on prompt length and keywords
        complexity = min(len(prompt) / 500, 1.0)
        if any(kw in prompt_lower for kw in ["complex", "entire", "all", "whole", "complete"]):
            complexity = min(complexity + 0.3, 1.0)

        return IntentAnalysis(
            primary_category=category,
            secondary_categories=[],
            confidence=0.5,  # Lower confidence for fallback
            complexity=complexity,
            requires_context=True,
            requires_execution=any(kw in prompt_lower for kw in ["run", "execute", "test"]),
            requires_file_access=True,
            estimated_tokens=1000,
            key_entities=[],
            user_goal=prompt[:100]
        )

    def analyze_sync(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentAnalysis:
        """Synchronous version of analyze"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're already in an async context, use fallback
                return self._fallback_analysis(prompt)
            return loop.run_until_complete(self.analyze(prompt, context))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.analyze(prompt, context))


class IntelligentRouter:
    """
    Makes intelligent routing decisions based on intent analysis.
    Replaces simple task-to-model mapping with dynamic routing.
    """

    # Model assignments for different task types
    # Using 7B models by default for speed - 32B available via SMART_MODE
    MODEL_MAPPING = {
        # Complex reasoning tasks → DeepSeek-R1 (7B for speed)
        TaskCategory.REASONING: "ollama/deepseek-r1:7b",
        TaskCategory.DEBUGGING: "ollama/deepseek-r1:7b",
        TaskCategory.SECURITY: "ollama/deepseek-r1:7b",
        TaskCategory.PERFORMANCE: "ollama/deepseek-r1:7b",

        # Code-heavy tasks → Qwen2.5-Coder (7B for speed)
        TaskCategory.CODE_GENERATION: "ollama/qwen2.5-coder:7b",
        TaskCategory.CODE_MODIFICATION: "ollama/qwen2.5-coder:7b",
        TaskCategory.REFACTORING: "ollama/qwen2.5-coder:7b",
        TaskCategory.TESTING: "ollama/qwen2.5-coder:7b",

        # General tasks → Qwen2.5 (7B for speed)
        TaskCategory.EXPLANATION: "ollama/qwen2.5-coder:7b",
        TaskCategory.DOCUMENTATION: "ollama/qwen2.5-coder:7b",
        TaskCategory.CODE_REVIEW: "ollama/qwen2.5-coder:7b",

        # Operations → Qwen2.5 (7B for speed)
        TaskCategory.DEVOPS: "ollama/qwen2.5-coder:7b",
        TaskCategory.DATABASE: "ollama/qwen2.5-coder:7b",
        TaskCategory.FILE_OPERATIONS: "ollama/qwen2.5-coder:7b",
        TaskCategory.COMMAND_EXECUTION: "ollama/qwen2.5-coder:7b",
        TaskCategory.GIT_OPERATIONS: "ollama/qwen2.5-coder:7b",
        TaskCategory.PROJECT_SETUP: "ollama/qwen2.5-coder:7b",

        # Quick tasks → Fast model
        TaskCategory.QUICK_ANSWER: "ollama/qwen2.5-coder:7b",
    }

    # 32B model mappings for SMART_MODE (higher quality, slower)
    MODEL_MAPPING_32B = {
        TaskCategory.REASONING: "ollama/deepseek-r1:latest",
        TaskCategory.DEBUGGING: "ollama/deepseek-r1:latest",
        TaskCategory.SECURITY: "ollama/deepseek-r1:latest",
        TaskCategory.PERFORMANCE: "ollama/deepseek-r1:latest",
        TaskCategory.CODE_GENERATION: "ollama/qwen2.5-coder:32b",
        TaskCategory.CODE_MODIFICATION: "ollama/qwen2.5-coder:32b",
        TaskCategory.REFACTORING: "ollama/qwen2.5-coder:32b",
        TaskCategory.TESTING: "ollama/qwen2.5-coder:32b",
        TaskCategory.EXPLANATION: "ollama/qwen2.5:32b",
        TaskCategory.DOCUMENTATION: "ollama/qwen2.5:32b",
        TaskCategory.CODE_REVIEW: "ollama/qwen2.5:32b",
        TaskCategory.DEVOPS: "ollama/qwen2.5:32b",
        TaskCategory.DATABASE: "ollama/qwen2.5:32b",
        TaskCategory.FILE_OPERATIONS: "ollama/qwen2.5:32b",
        TaskCategory.COMMAND_EXECUTION: "ollama/qwen2.5:32b",
        TaskCategory.GIT_OPERATIONS: "ollama/qwen2.5:32b",
        TaskCategory.PROJECT_SETUP: "ollama/qwen2.5:32b",
        TaskCategory.QUICK_ANSWER: "ollama/qwen2.5-coder:7b",
    }

    # Fallback chain for each model
    FALLBACK_CHAIN = {
        "ollama/deepseek-r1:7b": "ollama/qwen2.5-coder:7b",
        "ollama/deepseek-r1:latest": "ollama/qwen2.5:32b",
        "ollama/qwen2.5-coder:32b": "ollama/qwen2.5:32b",
        "ollama/qwen2.5:32b": "ollama/qwen2.5-coder:7b",
        "ollama/qwen2.5-coder:7b": "ollama/qwen2.5-coder:7b",
        "ollama/qwen2.5-coder:7b": None,
    }

    # Complexity threshold for using multi-agent council
    COUNCIL_THRESHOLD = 0.75

    # Categories that always benefit from council
    COUNCIL_CATEGORIES = {
        TaskCategory.REASONING,
        TaskCategory.SECURITY,
        TaskCategory.REFACTORING,
        TaskCategory.PERFORMANCE,
    }

    def __init__(self, intent_analyzer: Optional[IntentAnalyzer] = None, smart_mode: bool = False):
        self.analyzer = intent_analyzer or IntentAnalyzer()
        self._routing_history: List[RoutingDecision] = []
        self.smart_mode = smart_mode  # Use 32B models for higher quality

    def set_analyzer(self, analyzer: IntentAnalyzer) -> None:
        """Set the intent analyzer"""
        self.analyzer = analyzer

    async def route(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """Make routing decision for a prompt"""

        # Step 1: Analyze intent
        intent = await self.analyzer.analyze(prompt, context)

        # Step 2: Select primary model (use 32B in smart_mode for higher quality)
        model_mapping = self.MODEL_MAPPING_32B if self.smart_mode else self.MODEL_MAPPING
        primary_model = model_mapping.get(
            intent.primary_category,
            "ollama/qwen2.5-coder:7b" if not self.smart_mode else "ollama/qwen2.5:32b"
        )

        # Step 3: Determine if council should be used
        should_use_council = self._should_use_council(intent)

        # Step 4: Select which agents if using council
        agents = []
        if should_use_council:
            agents = self._select_agents(intent)

        # Step 5: Calculate context budget
        context_budget = self._calculate_context_budget(intent)

        # Step 6: Build decision
        decision = RoutingDecision(
            primary_model=primary_model,
            fallback_model=self.FALLBACK_CHAIN.get(primary_model),
            should_use_council=should_use_council,
            context_budget=context_budget,
            agents_to_involve=agents,
            confidence=intent.confidence,
            reasoning=self._build_reasoning(intent, primary_model, should_use_council),
            intent=intent
        )

        # Track history
        self._routing_history.append(decision)
        if len(self._routing_history) > 100:
            self._routing_history = self._routing_history[-50:]

        return decision

    def route_sync(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """Synchronous version of route"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Use fallback analysis
                intent = self.analyzer._fallback_analysis(prompt)
                return self._build_decision_from_intent(intent)
            return loop.run_until_complete(self.route(prompt, context))
        except RuntimeError:
            return asyncio.run(self.route(prompt, context))

    def _build_decision_from_intent(self, intent: IntentAnalysis) -> RoutingDecision:
        """Build a routing decision from an intent analysis"""
        model_mapping = self.MODEL_MAPPING_32B if self.smart_mode else self.MODEL_MAPPING
        primary_model = model_mapping.get(
            intent.primary_category,
            "ollama/qwen2.5-coder:7b" if not self.smart_mode else "ollama/qwen2.5:32b"
        )
        should_use_council = self._should_use_council(intent)
        agents = self._select_agents(intent) if should_use_council else []

        return RoutingDecision(
            primary_model=primary_model,
            fallback_model=self.FALLBACK_CHAIN.get(primary_model),
            should_use_council=should_use_council,
            context_budget=self._calculate_context_budget(intent),
            agents_to_involve=agents,
            confidence=intent.confidence,
            reasoning=self._build_reasoning(intent, primary_model, should_use_council),
            intent=intent
        )

    def _should_use_council(self, intent: IntentAnalysis) -> bool:
        """Determine if multi-agent council should be used"""
        return (
            intent.complexity >= self.COUNCIL_THRESHOLD or
            len(intent.secondary_categories) >= 3 or
            intent.primary_category in self.COUNCIL_CATEGORIES
        )

    def _select_agents(self, intent: IntentAnalysis) -> List[str]:
        """Select which council agents to involve"""
        agents = ["implementer"]  # Always include implementer

        category_to_agents = {
            TaskCategory.REASONING: ["architect"],
            TaskCategory.CODE_REVIEW: ["reviewer"],
            TaskCategory.SECURITY: ["security"],
            TaskCategory.PERFORMANCE: ["performance"],
            TaskCategory.DEBUGGING: ["debugger"],
            TaskCategory.REFACTORING: ["architect", "reviewer"],
            TaskCategory.CODE_GENERATION: ["reviewer"],
            TaskCategory.TESTING: ["reviewer"],
        }

        # Add agents for primary category
        if intent.primary_category in category_to_agents:
            agents.extend(category_to_agents[intent.primary_category])

        # Add agents for secondary categories
        for cat in intent.secondary_categories:
            if cat in category_to_agents:
                agents.extend(category_to_agents[cat])

        # Remove duplicates while preserving order
        seen = set()
        unique_agents = []
        for agent in agents:
            if agent not in seen:
                seen.add(agent)
                unique_agents.append(agent)

        return unique_agents[:4]  # Max 4 agents

    def _calculate_context_budget(self, intent: IntentAnalysis) -> int:
        """Calculate how many tokens to allocate for context"""
        base_budget = 4000

        # Increase for complex tasks
        if intent.complexity > 0.7:
            base_budget += 4000
        elif intent.complexity > 0.4:
            base_budget += 2000

        # Increase if context is required
        if intent.requires_context:
            base_budget += 2000

        # Adjust based on estimated response size
        if intent.estimated_tokens > 2000:
            base_budget += 2000

        # Cap at reasonable limit
        return min(base_budget, 16000)

    def _build_reasoning(
        self,
        intent: IntentAnalysis,
        model: str,
        use_council: bool
    ) -> str:
        """Build human-readable reasoning for the routing decision"""
        parts = [
            f"Task: {intent.user_goal[:50]}{'...' if len(intent.user_goal) > 50 else ''}",
            f"Category: {intent.primary_category.value}",
            f"Complexity: {intent.complexity:.0%}",
            f"Model: {model.split('/')[-1]}",
        ]

        if use_council:
            parts.append("Using multi-agent council")

        if intent.requires_execution:
            parts.append("Requires execution")

        return " | ".join(parts)

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get statistics about routing decisions"""
        if not self._routing_history:
            return {"total_routes": 0}

        category_counts = {}
        model_counts = {}
        council_count = 0

        for decision in self._routing_history:
            if decision.intent:
                cat = decision.intent.primary_category.value
                category_counts[cat] = category_counts.get(cat, 0) + 1

            model = decision.primary_model.split("/")[-1]
            model_counts[model] = model_counts.get(model, 0) + 1

            if decision.should_use_council:
                council_count += 1

        return {
            "total_routes": len(self._routing_history),
            "category_distribution": category_counts,
            "model_distribution": model_counts,
            "council_percentage": council_count / len(self._routing_history) * 100,
            "avg_confidence": sum(d.confidence for d in self._routing_history) / len(self._routing_history)
        }


# Convenience function for quick routing
async def quick_route(prompt: str, llm_adapter: Optional["LLMAdapter"] = None) -> RoutingDecision:
    """Quick routing without setting up full router"""
    analyzer = IntentAnalyzer(llm_adapter)
    router = IntelligentRouter(analyzer)
    return await router.route(prompt)


# Export main classes
__all__ = [
    "TaskCategory",
    "IntentAnalysis",
    "RoutingDecision",
    "IntentAnalyzer",
    "IntelligentRouter",
    "quick_route",
]
