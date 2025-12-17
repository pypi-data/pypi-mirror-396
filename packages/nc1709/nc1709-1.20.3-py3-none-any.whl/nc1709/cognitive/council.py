"""
Layer 3: Multi-Agent Council

Orchestrates multiple AI agents that specialize in different aspects:
- Implementer: Writes clean, efficient code
- Architect: Designs system structure and patterns
- Reviewer: Finds bugs, security issues, improvements
- Debugger: Diagnoses and fixes issues
- Optimizer: Improves performance
- Security: Analyzes security implications
- Documentation: Writes clear documentation

The council convenes for complex tasks (complexity > threshold) and
produces a consensus response that combines multiple perspectives.

This layer answers: "What do our AI experts think about this?"
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from datetime import datetime
import asyncio
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Specialized agent roles in the council"""
    IMPLEMENTER = "implementer"
    ARCHITECT = "architect"
    REVIEWER = "reviewer"
    DEBUGGER = "debugger"
    OPTIMIZER = "optimizer"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    TESTER = "tester"
    DEVOPS = "devops"


@dataclass
class AgentPersona:
    """Configuration for an AI agent's behavior and expertise"""
    role: AgentRole
    name: str
    description: str
    system_prompt: str
    focus_areas: List[str]
    weight: float = 1.0  # Weight in consensus voting
    preferred_model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


# Default agent personas
DEFAULT_AGENTS: Dict[AgentRole, AgentPersona] = {
    AgentRole.IMPLEMENTER: AgentPersona(
        role=AgentRole.IMPLEMENTER,
        name="Implementer",
        description="Expert at writing clean, efficient, maintainable code",
        system_prompt="""You are an expert software implementer. Your focus is on:
- Writing clean, readable, and maintainable code
- Following language idioms and best practices
- Implementing features correctly and completely
- Using appropriate data structures and algorithms
- Writing code that is easy to test and debug

When analyzing or writing code, prioritize correctness, clarity, and simplicity.
Suggest concrete implementations with actual code when relevant.""",
        focus_areas=["code_quality", "implementation", "best_practices", "readability"],
        weight=1.0,
    ),

    AgentRole.ARCHITECT: AgentPersona(
        role=AgentRole.ARCHITECT,
        name="Architect",
        description="Designs system structure, patterns, and high-level solutions",
        system_prompt="""You are a software architect. Your focus is on:
- System design and architecture patterns
- Code organization and module structure
- Scalability and maintainability concerns
- Design patterns and their appropriate use
- API design and interfaces
- Managing complexity through abstraction

When analyzing code, think about the bigger picture: how components interact,
where boundaries should be, and what patterns would improve the design.""",
        focus_areas=["architecture", "design_patterns", "scalability", "modularity"],
        weight=1.2,  # Slightly higher weight for complex decisions
    ),

    AgentRole.REVIEWER: AgentPersona(
        role=AgentRole.REVIEWER,
        name="Reviewer",
        description="Reviews code for bugs, issues, and improvements",
        system_prompt="""You are an expert code reviewer. Your focus is on:
- Finding bugs, logic errors, and edge cases
- Identifying code smells and anti-patterns
- Suggesting improvements and refactoring opportunities
- Checking for consistency with project style
- Ensuring error handling is comprehensive
- Validating that tests cover important cases

Be thorough but constructive. Point out issues with specific suggestions for fixes.""",
        focus_areas=["bugs", "code_quality", "improvements", "consistency"],
        weight=1.0,
    ),

    AgentRole.DEBUGGER: AgentPersona(
        role=AgentRole.DEBUGGER,
        name="Debugger",
        description="Expert at diagnosing and fixing bugs",
        system_prompt="""You are an expert debugger. Your focus is on:
- Analyzing error messages and stack traces
- Identifying root causes of bugs
- Understanding unexpected behavior
- Tracing execution flow and state
- Suggesting targeted fixes with minimal side effects
- Adding logging/debugging aids when helpful

When debugging, be systematic: hypothesize, verify, fix. Explain your reasoning.""",
        focus_areas=["debugging", "error_analysis", "root_cause", "fixes"],
        weight=1.1,  # Higher weight for debugging tasks
    ),

    AgentRole.OPTIMIZER: AgentPersona(
        role=AgentRole.OPTIMIZER,
        name="Optimizer",
        description="Focuses on performance and efficiency improvements",
        system_prompt="""You are a performance optimization expert. Your focus is on:
- Identifying performance bottlenecks
- Algorithm and data structure optimization
- Memory usage and allocation patterns
- I/O and database query optimization
- Caching strategies and memoization
- Profiling and benchmarking suggestions

When optimizing, consider trade-offs between readability and performance.
Only suggest optimizations that provide meaningful improvements.""",
        focus_areas=["performance", "optimization", "efficiency", "memory"],
        weight=0.9,
    ),

    AgentRole.SECURITY: AgentPersona(
        role=AgentRole.SECURITY,
        name="Security Analyst",
        description="Analyzes security implications and vulnerabilities",
        system_prompt="""You are a security expert. Your focus is on:
- Identifying security vulnerabilities (OWASP Top 10, etc.)
- Input validation and sanitization
- Authentication and authorization issues
- Injection attacks (SQL, XSS, command injection)
- Secrets management and exposure
- Secure coding practices

When reviewing code, think like an attacker. Point out vulnerabilities with
severity levels and specific remediation steps.""",
        focus_areas=["security", "vulnerabilities", "authentication", "validation"],
        weight=1.3,  # High weight for security concerns
    ),

    AgentRole.DOCUMENTATION: AgentPersona(
        role=AgentRole.DOCUMENTATION,
        name="Documentarian",
        description="Creates clear documentation and explanations",
        system_prompt="""You are a technical writer and documentation expert. Your focus is on:
- Writing clear, comprehensive documentation
- Creating helpful docstrings and comments
- Explaining complex code in simple terms
- Writing README files and guides
- API documentation with examples
- Architecture decision records

When documenting, think about the reader: what do they need to know?
Provide examples and context, not just descriptions.""",
        focus_areas=["documentation", "clarity", "examples", "explanations"],
        weight=0.8,
    ),

    AgentRole.TESTER: AgentPersona(
        role=AgentRole.TESTER,
        name="Tester",
        description="Expert at testing strategies and test implementation",
        system_prompt="""You are a testing expert. Your focus is on:
- Designing comprehensive test strategies
- Writing unit, integration, and e2e tests
- Identifying edge cases and boundary conditions
- Test coverage and quality metrics
- Mocking and test isolation
- Test-driven development practices

When analyzing code, think about how to test it effectively.
Suggest specific test cases that would catch bugs.""",
        focus_areas=["testing", "test_cases", "coverage", "quality"],
        weight=0.9,
    ),

    AgentRole.DEVOPS: AgentPersona(
        role=AgentRole.DEVOPS,
        name="DevOps Engineer",
        description="Expert in deployment, infrastructure, and operations",
        system_prompt="""You are a DevOps expert. Your focus is on:
- CI/CD pipelines and deployment automation
- Infrastructure as code
- Container orchestration (Docker, Kubernetes)
- Monitoring, logging, and observability
- Environment configuration and secrets
- Scalability and reliability concerns

When analyzing code, consider operational aspects: how will this run in production?
What monitoring and deployment considerations apply?""",
        focus_areas=["devops", "deployment", "infrastructure", "monitoring"],
        weight=0.8,
    ),
}


@dataclass
class AgentResponse:
    """Response from a single agent"""
    agent_role: AgentRole
    content: str
    confidence: float  # 0.0 to 1.0
    key_points: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    code_snippets: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CouncilSession:
    """A council session with multiple agent responses"""
    session_id: str
    task_description: str
    agents_consulted: List[AgentRole]
    responses: Dict[AgentRole, AgentResponse] = field(default_factory=dict)
    consensus: Optional[str] = None
    consensus_confidence: float = 0.0
    disagreements: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentSelector:
    """Selects which agents should participate based on task type"""

    # Task type to agent role mapping
    TASK_AGENT_MAP: Dict[str, List[AgentRole]] = {
        "code_generation": [AgentRole.IMPLEMENTER, AgentRole.ARCHITECT],
        "code_modification": [AgentRole.IMPLEMENTER, AgentRole.REVIEWER],
        "debugging": [AgentRole.DEBUGGER, AgentRole.IMPLEMENTER],
        "code_review": [AgentRole.REVIEWER, AgentRole.SECURITY],
        "security": [AgentRole.SECURITY, AgentRole.REVIEWER],
        "performance": [AgentRole.OPTIMIZER, AgentRole.ARCHITECT],
        "refactoring": [AgentRole.ARCHITECT, AgentRole.REVIEWER, AgentRole.IMPLEMENTER],
        "testing": [AgentRole.TESTER, AgentRole.REVIEWER],
        "documentation": [AgentRole.DOCUMENTATION, AgentRole.IMPLEMENTER],
        "devops": [AgentRole.DEVOPS, AgentRole.SECURITY],
        "explanation": [AgentRole.DOCUMENTATION, AgentRole.ARCHITECT],
        "reasoning": [AgentRole.ARCHITECT, AgentRole.REVIEWER],
        "project_setup": [AgentRole.ARCHITECT, AgentRole.DEVOPS],
    }

    # Minimum and maximum agents per session
    MIN_AGENTS = 2
    MAX_AGENTS = 4

    @classmethod
    def select_agents(
        cls,
        task_category: str,
        complexity: float,
        explicit_roles: Optional[List[str]] = None
    ) -> List[AgentRole]:
        """
        Select agents for a task based on category and complexity

        Args:
            task_category: Type of task (from TaskCategory)
            complexity: Task complexity score (0.0 to 1.0)
            explicit_roles: Optional list of specific roles to include

        Returns:
            List of AgentRole to consult
        """
        selected: Set[AgentRole] = set()

        # Add explicitly requested roles
        if explicit_roles:
            for role_name in explicit_roles:
                try:
                    role = AgentRole(role_name.lower())
                    selected.add(role)
                except ValueError:
                    logger.warning(f"Unknown agent role: {role_name}")

        # Add roles based on task type
        task_key = task_category.lower().replace("_", "_")
        if task_key in cls.TASK_AGENT_MAP:
            for role in cls.TASK_AGENT_MAP[task_key]:
                selected.add(role)

        # For high complexity, add more perspectives
        if complexity > 0.8 and len(selected) < cls.MAX_AGENTS:
            # Add architect for complex design decisions
            selected.add(AgentRole.ARCHITECT)
            # Add reviewer for quality assurance
            selected.add(AgentRole.REVIEWER)

        # For security-sensitive tasks, always include security
        security_keywords = ["auth", "login", "password", "token", "secret", "credential", "encrypt"]
        if any(kw in task_category.lower() for kw in security_keywords):
            selected.add(AgentRole.SECURITY)

        # Ensure minimum agents
        if len(selected) < cls.MIN_AGENTS:
            # Default to implementer and reviewer
            selected.add(AgentRole.IMPLEMENTER)
            selected.add(AgentRole.REVIEWER)

        # Limit to max agents
        result = list(selected)[:cls.MAX_AGENTS]

        return result


class ConsensusBuilder:
    """Builds consensus from multiple agent responses"""

    @staticmethod
    def build_consensus(
        responses: Dict[AgentRole, AgentResponse],
        agent_personas: Dict[AgentRole, AgentPersona]
    ) -> tuple[str, float, List[str]]:
        """
        Build consensus from multiple agent responses

        Args:
            responses: Dict of agent role to response
            agent_personas: Dict of agent role to persona (for weights)

        Returns:
            Tuple of (consensus_text, confidence, disagreements)
        """
        if not responses:
            return "", 0.0, []

        # Collect all key points and suggestions with weights
        weighted_points: Dict[str, float] = {}
        weighted_suggestions: Dict[str, float] = {}
        all_concerns: List[str] = []
        all_code_snippets: List[str] = []

        total_weight = 0.0
        total_confidence = 0.0

        for role, response in responses.items():
            persona = agent_personas.get(role)
            weight = persona.weight if persona else 1.0
            total_weight += weight
            total_confidence += response.confidence * weight

            # Weight key points
            for point in response.key_points:
                point_lower = point.lower().strip()
                if point_lower not in weighted_points:
                    weighted_points[point_lower] = 0.0
                weighted_points[point_lower] += weight * response.confidence

            # Weight suggestions
            for suggestion in response.suggestions:
                sug_lower = suggestion.lower().strip()
                if sug_lower not in weighted_suggestions:
                    weighted_suggestions[sug_lower] = 0.0
                weighted_suggestions[sug_lower] += weight * response.confidence

            # Collect concerns
            all_concerns.extend(response.concerns)

            # Collect code snippets (prefer from implementer)
            if role == AgentRole.IMPLEMENTER:
                all_code_snippets = response.code_snippets + all_code_snippets
            else:
                all_code_snippets.extend(response.code_snippets)

        # Calculate overall confidence
        consensus_confidence = total_confidence / total_weight if total_weight > 0 else 0.0

        # Find disagreements (points mentioned by some but not others)
        disagreements = []
        for point, weight in weighted_points.items():
            # If a point has low weight relative to total, it's a potential disagreement
            agreement_ratio = weight / total_weight
            if 0.2 < agreement_ratio < 0.6:  # Partial agreement
                disagreements.append(f"Partial agreement on: {point}")

        # Build consensus text
        consensus_parts = []

        # Add top key points
        sorted_points = sorted(weighted_points.items(), key=lambda x: x[1], reverse=True)
        if sorted_points:
            consensus_parts.append("**Key Points:**")
            for point, _ in sorted_points[:5]:
                consensus_parts.append(f"- {point}")

        # Add top suggestions
        sorted_suggestions = sorted(weighted_suggestions.items(), key=lambda x: x[1], reverse=True)
        if sorted_suggestions:
            consensus_parts.append("\n**Recommendations:**")
            for suggestion, _ in sorted_suggestions[:5]:
                consensus_parts.append(f"- {suggestion}")

        # Add concerns if any
        unique_concerns = list(set(all_concerns))
        if unique_concerns:
            consensus_parts.append("\n**Concerns Raised:**")
            for concern in unique_concerns[:3]:
                consensus_parts.append(f"- {concern}")

        # Add code snippets if any
        if all_code_snippets:
            consensus_parts.append("\n**Code:**")
            for snippet in all_code_snippets[:2]:  # Limit code snippets
                consensus_parts.append(f"```\n{snippet}\n```")

        consensus_text = "\n".join(consensus_parts)

        return consensus_text, consensus_confidence, disagreements


class MultiAgentCouncil:
    """
    Layer 3: Multi-Agent Council

    Orchestrates multiple AI agents to collaborate on complex tasks.
    Each agent brings a specialized perspective, and the council
    produces a consensus response.
    """

    def __init__(
        self,
        llm_adapter: Optional[Any] = None,
        agent_personas: Optional[Dict[AgentRole, AgentPersona]] = None,
        max_parallel_agents: int = 3,
        council_threshold: float = 0.75
    ):
        """
        Initialize the council

        Args:
            llm_adapter: LLM adapter for agent completions
            agent_personas: Custom agent personas (defaults used if not provided)
            max_parallel_agents: Maximum agents to run in parallel
            council_threshold: Complexity threshold to convene full council
        """
        self._llm_adapter = llm_adapter
        self.agent_personas = agent_personas or DEFAULT_AGENTS
        self.max_parallel_agents = max_parallel_agents
        self.council_threshold = council_threshold
        self._executor = ThreadPoolExecutor(max_workers=max_parallel_agents)
        self._session_history: List[CouncilSession] = []
        self._lock = threading.Lock()

    @property
    def llm_adapter(self):
        """Lazy load LLM adapter"""
        if self._llm_adapter is None:
            try:
                from ..llm_adapter import get_llm_adapter
                self._llm_adapter = get_llm_adapter()
            except Exception as e:
                logger.warning(f"Could not load LLM adapter: {e}")
        return self._llm_adapter

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return f"council_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    def _create_agent_prompt(
        self,
        persona: AgentPersona,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create the full prompt for an agent"""
        parts = []

        # Add context if available
        if context:
            if context.get("code"):
                parts.append(f"**Code to analyze:**\n```\n{context['code']}\n```\n")
            if context.get("error"):
                parts.append(f"**Error:**\n{context['error']}\n")
            if context.get("files"):
                parts.append(f"**Relevant files:** {', '.join(context['files'])}\n")

        parts.append(f"**Task:**\n{task_description}")

        parts.append("""
Please provide your analysis as a structured response:
1. KEY POINTS: Main observations or findings (bullet points)
2. SUGGESTIONS: Recommended actions or improvements
3. CONCERNS: Any issues or risks identified
4. CODE: Any code snippets (if applicable)

Be concise but thorough. Focus on your area of expertise.""")

        return "\n\n".join(parts)

    def _parse_agent_response(self, raw_response: str, role: AgentRole) -> AgentResponse:
        """Parse raw LLM response into structured AgentResponse"""
        key_points = []
        suggestions = []
        concerns = []
        code_snippets = []

        # Simple parsing of structured response
        current_section = None
        current_content = []

        for line in raw_response.split('\n'):
            line_lower = line.lower().strip()

            if 'key point' in line_lower or line_lower.startswith('1.'):
                if current_section and current_content:
                    self._add_to_section(current_section, current_content, key_points, suggestions, concerns)
                current_section = 'key_points'
                current_content = []
            elif 'suggestion' in line_lower or 'recommend' in line_lower or line_lower.startswith('2.'):
                if current_section and current_content:
                    self._add_to_section(current_section, current_content, key_points, suggestions, concerns)
                current_section = 'suggestions'
                current_content = []
            elif 'concern' in line_lower or 'issue' in line_lower or 'risk' in line_lower or line_lower.startswith('3.'):
                if current_section and current_content:
                    self._add_to_section(current_section, current_content, key_points, suggestions, concerns)
                current_section = 'concerns'
                current_content = []
            elif line.startswith('```'):
                # Handle code block
                if current_section == 'code':
                    code_snippets.append('\n'.join(current_content))
                    current_section = None
                    current_content = []
                else:
                    current_section = 'code'
                    current_content = []
            elif line.strip().startswith('-') or line.strip().startswith('•'):
                # Bullet point
                content = line.strip().lstrip('-•').strip()
                if content:
                    current_content.append(content)
            elif line.strip():
                current_content.append(line.strip())

        # Handle last section
        if current_section and current_content:
            if current_section == 'code':
                code_snippets.append('\n'.join(current_content))
            else:
                self._add_to_section(current_section, current_content, key_points, suggestions, concerns)

        # If no structure found, use raw response as key points
        if not key_points and not suggestions and not concerns:
            key_points = [raw_response[:500]]  # Truncate if too long

        # Calculate confidence based on response quality
        confidence = 0.7  # Base confidence
        if key_points:
            confidence += 0.1
        if suggestions:
            confidence += 0.1
        if code_snippets:
            confidence += 0.1

        return AgentResponse(
            agent_role=role,
            content=raw_response,
            confidence=min(1.0, confidence),
            key_points=key_points[:5],
            suggestions=suggestions[:5],
            concerns=concerns[:3],
            code_snippets=code_snippets[:2],
        )

    def _add_to_section(
        self,
        section: str,
        content: List[str],
        key_points: List[str],
        suggestions: List[str],
        concerns: List[str]
    ):
        """Add content to appropriate section"""
        joined = ' '.join(content)
        if section == 'key_points':
            key_points.extend(content)
        elif section == 'suggestions':
            suggestions.extend(content)
        elif section == 'concerns':
            concerns.extend(content)

    def _consult_agent(
        self,
        persona: AgentPersona,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Consult a single agent

        Args:
            persona: Agent's persona configuration
            task_description: Task to analyze
            context: Additional context

        Returns:
            AgentResponse with the agent's analysis
        """
        prompt = self._create_agent_prompt(persona, task_description, context)

        try:
            if self.llm_adapter:
                response = self.llm_adapter.complete(
                    prompt=prompt,
                    system_prompt=persona.system_prompt,
                    model=persona.preferred_model,
                    temperature=persona.temperature,
                    max_tokens=persona.max_tokens,
                )
            else:
                # Fallback: return a placeholder response
                response = f"[{persona.name}] Analysis placeholder for: {task_description[:100]}..."

            return self._parse_agent_response(response, persona.role)

        except Exception as e:
            logger.error(f"Error consulting {persona.name}: {e}")
            return AgentResponse(
                agent_role=persona.role,
                content=f"Error: {e}",
                confidence=0.0,
                concerns=[f"Agent error: {e}"],
            )

    def convene(
        self,
        task_description: str,
        task_category: str = "general",
        complexity: float = 0.5,
        context: Optional[Dict[str, Any]] = None,
        agents: Optional[List[str]] = None,
        parallel: bool = True
    ) -> CouncilSession:
        """
        Convene the council for a task

        Args:
            task_description: Description of the task
            task_category: Category of the task
            complexity: Task complexity (0.0 to 1.0)
            context: Additional context (code, files, errors)
            agents: Specific agents to consult
            parallel: Run agents in parallel

        Returns:
            CouncilSession with all responses and consensus
        """
        # Select agents
        agent_roles = AgentSelector.select_agents(
            task_category=task_category,
            complexity=complexity,
            explicit_roles=agents
        )

        session = CouncilSession(
            session_id=self._generate_session_id(),
            task_description=task_description,
            agents_consulted=agent_roles,
            metadata={
                "category": task_category,
                "complexity": complexity,
            }
        )

        logger.info(f"Council convened: {session.session_id} with {[r.value for r in agent_roles]}")

        # Consult agents
        if parallel and len(agent_roles) > 1:
            # Parallel consultation
            futures = {}
            for role in agent_roles:
                persona = self.agent_personas.get(role)
                if persona:
                    future = self._executor.submit(
                        self._consult_agent, persona, task_description, context
                    )
                    futures[future] = role

            for future in as_completed(futures):
                role = futures[future]
                try:
                    response = future.result()
                    session.responses[role] = response
                except Exception as e:
                    logger.error(f"Error from {role.value}: {e}")

        else:
            # Sequential consultation
            for role in agent_roles:
                persona = self.agent_personas.get(role)
                if persona:
                    response = self._consult_agent(persona, task_description, context)
                    session.responses[role] = response

        # Build consensus
        if session.responses:
            consensus, confidence, disagreements = ConsensusBuilder.build_consensus(
                session.responses,
                self.agent_personas
            )
            session.consensus = consensus
            session.consensus_confidence = confidence
            session.disagreements = disagreements

        session.completed_at = datetime.now()

        # Store session
        with self._lock:
            self._session_history.append(session)
            # Keep last 100 sessions
            if len(self._session_history) > 100:
                self._session_history = self._session_history[-100:]

        return session

    async def convene_async(
        self,
        task_description: str,
        task_category: str = "general",
        complexity: float = 0.5,
        context: Optional[Dict[str, Any]] = None,
        agents: Optional[List[str]] = None
    ) -> CouncilSession:
        """Async version of convene"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.convene(
                task_description=task_description,
                task_category=task_category,
                complexity=complexity,
                context=context,
                agents=agents,
                parallel=True
            )
        )

    def quick_consult(
        self,
        task_description: str,
        role: AgentRole
    ) -> AgentResponse:
        """
        Quick consultation with a single agent

        Args:
            task_description: Task to analyze
            role: Specific agent role

        Returns:
            AgentResponse from the agent
        """
        persona = self.agent_personas.get(role)
        if not persona:
            raise ValueError(f"Unknown agent role: {role}")

        return self._consult_agent(persona, task_description)

    def get_session_history(self, limit: int = 10) -> List[CouncilSession]:
        """Get recent council sessions"""
        with self._lock:
            return self._session_history[-limit:]

    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents with descriptions"""
        return [
            {
                "role": role.value,
                "name": persona.name,
                "description": persona.description,
                "focus_areas": persona.focus_areas,
            }
            for role, persona in self.agent_personas.items()
        ]


# Convenience functions
def get_council(llm_adapter: Optional[Any] = None) -> MultiAgentCouncil:
    """Get or create council instance"""
    return MultiAgentCouncil(llm_adapter=llm_adapter)


def quick_council(
    task: str,
    category: str = "general",
    complexity: float = 0.5
) -> CouncilSession:
    """Quickly convene council for a task"""
    council = get_council()
    return council.convene(
        task_description=task,
        task_category=category,
        complexity=complexity
    )
