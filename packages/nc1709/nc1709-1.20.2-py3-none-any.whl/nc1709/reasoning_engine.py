"""
Multi-Step Reasoning Engine
Handles complex tasks by breaking them down into manageable steps
"""
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from .llm_adapter import LLMAdapter, TaskType
from .file_controller import FileController
from .executor import CommandExecutor
from .cli_ui import (
    ActionSpinner, TaskDisplay, Color, Icons,
    status, thinking, success, error, warning, info,
    action_spinner, StreamingOutput
)


class StepType(Enum):
    """Types of steps in a plan"""
    ANALYZE = "analyze"
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    EXECUTE_COMMAND = "execute_command"
    REASON = "reason"
    VERIFY = "verify"


class Step:
    """Represents a single step in a plan"""
    
    def __init__(
        self,
        step_type: StepType,
        description: str,
        details: Dict[str, Any],
        dependencies: Optional[List[int]] = None
    ):
        """Initialize a step
        
        Args:
            step_type: Type of step
            description: Human-readable description
            details: Step-specific details
            dependencies: List of step indices this depends on
        """
        self.step_type = step_type
        self.description = description
        self.details = details
        self.dependencies = dependencies or []
        self.status = "pending"  # pending, running, completed, failed
        self.result: Optional[Any] = None
        self.error: Optional[str] = None


class ReasoningEngine:
    """Engine for multi-step reasoning and task execution"""

    # System prompt that defines NC1709's identity and capabilities
    SYSTEM_PROMPT = """You are NC1709, a local-first AI developer assistant created by Lafzusa Corp, running entirely on the user's machine.

IMPORTANT: You are NC1709, NOT Claude, NOT GPT, NOT any other AI. When asked who you are, what model you are, who made you, or any similar question about your identity:
- You are NC1709, an AI coding assistant
- Developed by Asif for Lafz Corp USA
- Contact: solutions@lafzusa.com
Never claim to be from Anthropic, OpenAI, or any other company.

Your capabilities include:
- Reading and writing files in the project
- Executing shell commands safely
- Searching code semantically
- Git operations (status, diff, commit, branch, etc.)
- Docker operations (containers, images, compose)
- Scaffolding projects (FastAPI, Next.js, Django)
- MCP (Model Context Protocol) tool integration

Key principles:
- You run 100% locally - no data leaves the user's machine
- Be helpful and concise in your responses
- When asked to do something, explain what you'll do briefly, then do it
- For code tasks, provide working code with explanations
- Ask clarifying questions if the request is ambiguous

Current context:
- You are responding through the NC1709 dashboard or CLI
- The user's project is in their current working directory
- You have access to their codebase and can help with development tasks

Respond helpfully and directly to the user's request."""

    def __init__(self):
        """Initialize the reasoning engine"""
        self.llm = LLMAdapter()
        self.file_controller = FileController()
        self.executor = CommandExecutor()
        self.current_plan: Optional[List[Step]] = None
        self.execution_context: Dict[str, Any] = {}
    
    def process_request(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a user request with multi-step reasoning
        
        Args:
            user_request: User's request
            context: Additional context (e.g., current directory, files)
        
        Returns:
            Final result or response
        """
        # Determine if this needs multi-step reasoning
        if self._needs_multi_step(user_request):
            return self._execute_multi_step(user_request, context)
        else:
            # Simple single-step request
            return self._execute_single_step(user_request)
    
    def _needs_multi_step(self, request: str) -> bool:
        """Determine if a request needs multi-step reasoning
        
        Args:
            request: User's request
        
        Returns:
            True if multi-step reasoning is needed
        """
        # Keywords that indicate complex, multi-step tasks
        multi_step_keywords = [
            "create a project", "build a", "set up", "implement",
            "refactor", "migrate", "convert", "analyze and",
            "first.*then", "step by step", "plan"
        ]
        
        request_lower = request.lower()
        return any(re.search(keyword, request_lower) for keyword in multi_step_keywords)
    
    def _execute_single_step(self, request: str) -> str:
        """Execute a simple, single-step request

        Args:
            request: User's request

        Returns:
            Response
        """
        # Use spinner for visual feedback during LLM call
        spinner = ActionSpinner("Processing your request")
        spinner.start()

        try:
            spinner.update("Generating response")
            response = self.llm.complete(request, system_prompt=self.SYSTEM_PROMPT)
            spinner.success("Response generated")
            return response
        except Exception as e:
            spinner.failure(f"Error: {e}")
            raise
    
    def _execute_multi_step(self, request: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute a complex, multi-step request

        Args:
            request: User's request
            context: Additional context

        Returns:
            Final result
        """
        # Use spinner for plan creation
        spinner = ActionSpinner("Analyzing request")
        spinner.start()

        try:
            spinner.update("Creating execution plan")
            plan = self._create_plan(request, context)

            if not plan:
                spinner.failure("Could not create plan")
                return "I couldn't create a plan for this request. Please try rephrasing."

            self.current_plan = plan
            spinner.success(f"Created plan with {len(plan)} steps")

        except Exception as e:
            spinner.failure(f"Planning error: {e}")
            return f"Error creating plan: {e}"

        # Show plan to user
        self._display_plan(plan)

        # Ask for confirmation
        response = input(f"\n{Color.BOLD}Proceed with this plan?{Color.RESET} [y/N]: ").strip().lower()
        if response != 'y':
            warning("Plan cancelled by user")
            return "Plan cancelled by user."

        # Execute plan with TaskDisplay
        task = TaskDisplay(f"Executing {len(plan)}-step plan")
        task.start()
        result = self._execute_plan_with_display(plan, task)
        task.finish()

        return result
    
    def _create_plan(self, request: str, context: Optional[Dict[str, Any]] = None) -> List[Step]:
        """Create an execution plan for a request

        Args:
            request: User's request
            context: Additional context

        Returns:
            List of steps
        """
        # Use reasoning model to create a plan
        planning_prompt = f"""You are a task planning assistant. Break down the following request into clear, actionable steps.

User Request: {request}

Context: {json.dumps(context or {}, indent=2)}

Create a step-by-step plan. For each step, specify:
1. What type of action it is (analyze, read_file, write_file, execute_command, reason, verify)
2. A clear description
3. Specific details needed to execute the step

Format your response as a JSON array of steps:
[
  {{
    "type": "analyze",
    "description": "Understand the requirements",
    "details": {{"focus": "key requirements"}}
  }},
  {{
    "type": "write_file",
    "description": "Create main.py",
    "details": {{"file_path": "main.py", "content_description": "Python script with..."}}
  }}
]

Provide ONLY the JSON array, no additional text."""

        try:
            response = self.llm.complete(planning_prompt, task_type=TaskType.REASONING)

            # Try to extract and parse JSON from the response
            plan_data = self._extract_json_from_response(response)

            if not plan_data:
                print("⚠️  Could not extract valid JSON plan from LLM response")
                return []

            # Convert to Step objects
            steps = []
            for step_data in plan_data:
                try:
                    step_type_str = step_data.get("type", "reason")
                    # Handle case where type might not be a valid StepType
                    try:
                        step_type = StepType(step_type_str)
                    except ValueError:
                        step_type = StepType.REASON  # Default to REASON for unknown types

                    description = step_data.get("description", "Unknown step")
                    details = step_data.get("details", {})

                    # Ensure details is a dict
                    if not isinstance(details, dict):
                        details = {"value": details}

                    steps.append(Step(step_type, description, details))
                except Exception as step_error:
                    print(f"⚠️  Skipping malformed step: {step_error}")
                    continue

            return steps

        except Exception as e:
            print(f"⚠️  Error creating plan: {e}")
            return []

    def _extract_json_from_response(self, response: str) -> Optional[List[Dict]]:
        """Extract JSON array from LLM response with multiple fallback strategies

        Args:
            response: Raw LLM response text

        Returns:
            Parsed JSON list or None if extraction fails
        """
        # Strategy 1: Try to parse the entire response as JSON
        try:
            data = json.loads(response.strip())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

        # Strategy 2: Find JSON array using regex (handles markdown code blocks)
        patterns = [
            r'```json\s*(\[.*?\])\s*```',  # JSON in code block
            r'```\s*(\[.*?\])\s*```',       # Array in generic code block
            r'(\[\s*\{.*?\}\s*\])',          # Bare JSON array
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue

        # Strategy 3: Find the first '[' and last ']' and try to parse
        start = response.find('[')
        end = response.rfind(']')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(response[start:end + 1])
            except json.JSONDecodeError:
                pass

        # Strategy 4: Try to fix common JSON issues
        try:
            # Remove trailing commas before ] or }
            cleaned = re.sub(r',(\s*[\]\}])', r'\1', response)
            start = cleaned.find('[')
            end = cleaned.rfind(']')
            if start != -1 and end != -1:
                return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError:
            pass

        return None
    
    def _display_plan(self, plan: List[Step]) -> None:
        """Display the execution plan to the user

        Args:
            plan: List of steps
        """
        print(f"\n{Color.DIM}{'─'*60}{Color.RESET}")
        print(f"{Color.BOLD}EXECUTION PLAN{Color.RESET}")
        print(f"{Color.DIM}{'─'*60}{Color.RESET}")

        for i, step in enumerate(plan, 1):
            icon = self._get_step_icon(step.step_type)
            print(f"{Color.CYAN}{i}.{Color.RESET} {icon} {step.description}")
            if step.details:
                for key, value in step.details.items():
                    if len(str(value)) < 100:
                        print(f"   {Color.DIM}{Icons.TREE_BRANCH} {key}: {value}{Color.RESET}")

        print(f"{Color.DIM}{'─'*60}{Color.RESET}")
    
    def _get_step_icon(self, step_type: StepType) -> str:
        """Get an icon for a step type
        
        Args:
            step_type: Type of step
        
        Returns:
            Icon string
        """
        icons = {
            StepType.ANALYZE: "🔍",
            StepType.READ_FILE: "📖",
            StepType.WRITE_FILE: "✏️",
            StepType.EXECUTE_COMMAND: "💻",
            StepType.REASON: "🧠",
            StepType.VERIFY: "✅"
        }
        return icons.get(step_type, "•")
    
    def _execute_plan_with_display(self, plan: List[Step], task: TaskDisplay) -> str:
        """Execute a plan with visual feedback using TaskDisplay

        Args:
            plan: List of steps to execute
            task: TaskDisplay instance for visual feedback

        Returns:
            Final result
        """
        results = []

        for i, step in enumerate(plan, 1):
            step.status = "running"
            task.step(f"Step {i}/{len(plan)}: {step.description}")

            try:
                # Add action based on step type
                action_name = step.step_type.value.replace("_", " ").title()
                target = None

                if step.step_type == StepType.READ_FILE:
                    target = step.details.get("file_path", "file")
                    action_name = "Read"
                elif step.step_type == StepType.WRITE_FILE:
                    target = step.details.get("file_path", "file")
                    action_name = "Write"
                elif step.step_type == StepType.EXECUTE_COMMAND:
                    target = step.details.get("command", "command")[:30]
                    action_name = "Execute"
                elif step.step_type in (StepType.ANALYZE, StepType.REASON):
                    action_name = "Analyze"
                    target = step.description[:30]

                action_idx = task.action(action_name, target) if target else -1

                result = self._execute_step(step)
                step.result = result
                step.status = "completed"
                results.append(result)

                if action_idx >= 0:
                    task.complete_action(action_idx)
                task.complete_step(f"Step {i} complete")

            except Exception as e:
                step.error = str(e)
                step.status = "failed"

                if action_idx >= 0:
                    task.fail_action(action_idx, str(e))
                task.fail_step(f"Step {i} failed: {e}")

                # Ask user if they want to continue
                response = input(f"\n{Color.YELLOW}Continue with remaining steps?{Color.RESET} [y/N]: ").strip().lower()
                if response != 'y':
                    break

        # Generate final summary
        return self._generate_summary(plan, results)

    def _execute_plan(self, plan: List[Step]) -> str:
        """Execute a plan (legacy method for compatibility)

        Args:
            plan: List of steps to execute

        Returns:
            Final result
        """
        # Use TaskDisplay for visual feedback
        task = TaskDisplay(f"Executing {len(plan)}-step plan")
        task.start()
        result = self._execute_plan_with_display(plan, task)
        task.finish()
        return result
    
    def _execute_step(self, step: Step) -> Any:
        """Execute a single step
        
        Args:
            step: Step to execute
        
        Returns:
            Step result
        """
        if step.step_type == StepType.ANALYZE:
            # Use LLM to analyze
            prompt = f"Analyze: {step.description}\nDetails: {json.dumps(step.details)}"
            return self.llm.complete(prompt, task_type=TaskType.REASONING)
        
        elif step.step_type == StepType.READ_FILE:
            file_path = step.details.get("file_path")
            if not file_path:
                raise ValueError("No file_path specified for read_file step")
            content = self.file_controller.read_file(file_path)
            print(f"📖 Read {len(content)} characters from {file_path}")
            return content
        
        elif step.step_type == StepType.WRITE_FILE:
            file_path = step.details.get("file_path")
            content = step.details.get("content")
            
            if not file_path:
                raise ValueError("No file_path specified for write_file step")
            
            # If content not provided, generate it with LLM
            if not content:
                content_description = step.details.get("content_description", "")
                prompt = f"Generate content for {file_path}: {content_description}"
                content = self.llm.complete(prompt, task_type=TaskType.CODING)
            
            success = self.file_controller.write_file(file_path, content)
            if not success:
                raise RuntimeError(f"Failed to write file: {file_path}")
            
            return f"File written: {file_path}"
        
        elif step.step_type == StepType.EXECUTE_COMMAND:
            command = step.details.get("command")
            if not command:
                raise ValueError("No command specified for execute_command step")
            
            return_code, stdout, stderr = self.executor.execute(command, confirm=False)
            
            if return_code != 0:
                raise RuntimeError(f"Command failed: {stderr}")
            
            return stdout
        
        elif step.step_type == StepType.REASON:
            prompt = f"{step.description}\nContext: {json.dumps(self.execution_context)}"
            return self.llm.complete(prompt, task_type=TaskType.REASONING)
        
        elif step.step_type == StepType.VERIFY:
            # Verification step
            verification_prompt = f"Verify: {step.description}\nDetails: {json.dumps(step.details)}"
            return self.llm.complete(verification_prompt, task_type=TaskType.REASONING)
        
        else:
            raise ValueError(f"Unknown step type: {step.step_type}")
    
    def _generate_summary(self, plan: List[Step], results: List[Any]) -> str:
        """Generate a summary of plan execution

        Args:
            plan: Executed plan
            results: Results from each step

        Returns:
            Summary text
        """
        completed = sum(1 for step in plan if step.status == "completed")
        failed = sum(1 for step in plan if step.status == "failed")

        summary = f"\n{Color.DIM}{'─'*60}{Color.RESET}\n"
        summary += f"{Color.BOLD}EXECUTION SUMMARY{Color.RESET}\n"
        summary += f"{Color.DIM}{'─'*60}{Color.RESET}\n"
        summary += f"Total steps: {len(plan)}\n"
        summary += f"{Color.GREEN}Completed: {completed}{Color.RESET}\n"
        if failed > 0:
            summary += f"{Color.RED}Failed: {failed}{Color.RESET}\n"
        summary += f"{Color.DIM}{'─'*60}{Color.RESET}\n"

        if failed == 0:
            summary += f"{Color.GREEN}{Icons.SUCCESS} All steps completed successfully!{Color.RESET}\n"
        else:
            summary += f"{Color.YELLOW}{Icons.WARNING} {failed} step(s) failed{Color.RESET}\n"
            for i, step in enumerate(plan, 1):
                if step.status == "failed":
                    summary += f"   {Color.RED}{Icons.FAILURE}{Color.RESET} Step {i}: {step.description}\n"
                    summary += f"     {Color.DIM}{Icons.TREE_BRANCH} {step.error}{Color.RESET}\n"

        return summary
