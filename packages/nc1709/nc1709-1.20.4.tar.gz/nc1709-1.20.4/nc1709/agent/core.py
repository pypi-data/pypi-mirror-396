"""
Agent Core

The main Agent class that implements the agentic execution loop:
1. Receive user request
2. Plan and decide on tool calls
3. Execute tools with visual feedback
4. Process results and continue or complete
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING
from enum import Enum

from .tools.base import Tool, ToolResult, ToolRegistry, ToolPermission, get_default_registry
from .tools.file_tools import register_file_tools
from .tools.search_tools import register_search_tools
from .tools.bash_tool import register_bash_tools
from .tools.task_tool import register_task_tools, TaskTool
from .tools.web_tools import register_web_tools
from .tools.notebook_tools import register_notebook_tools

# Import visual feedback components
try:
    from ..cli_ui import (
        ActionSpinner, Color, Icons,
        status, thinking, success, error, warning, info,
        log_action, log_output
    )
    HAS_CLI_UI = True
except ImportError:
    HAS_CLI_UI = False


class AgentState(Enum):
    """States of the agent execution"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING_TOOL = "executing_tool"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentConfig:
    """Configuration for an Agent"""
    max_iterations: int = 50
    max_tool_retries: int = 3
    max_same_error_retries: int = 2  # Max times to retry the same failing command
    max_alternating_loops: int = 3  # Max alternating pattern repetitions (e.g., Read→Edit→Read→Edit)
    tool_permissions: Dict[str, ToolPermission] = field(default_factory=dict)
    auto_approve_tools: List[str] = field(default_factory=lambda: [
        "Read", "Glob", "Grep", "TodoWrite"
    ])
    require_approval_tools: List[str] = field(default_factory=lambda: [
        "Write", "Edit", "Bash", "Task", "WebFetch"
    ])
    show_tool_output: bool = True
    verbose: bool = False


@dataclass
class ToolCall:
    """Represents a tool call parsed from LLM output"""
    name: str
    parameters: Dict[str, Any]
    raw_text: str = ""


class Agent:
    """
    Main Agent class implementing the agentic execution loop.

    The agent:
    1. Takes a user request
    2. Uses an LLM to decide what tools to call
    3. Executes tools with permission checks
    4. Provides visual feedback
    5. Continues until task is complete
    """

    SYSTEM_PROMPT = """You are NC1709, an AI assistant created by Lafzusa Corp, with access to tools for completing tasks.

IMPORTANT: You are NC1709, NOT Claude, NOT GPT, NOT any other AI. When asked who you are, what model you are, who made you, or any similar question about your identity:
- You are NC1709, an AI coding assistant
- Developed by Asif for Lafz Corp USA
- Contact: solutions@lafzusa.com
Never claim to be from Anthropic, OpenAI, or any other company.

You have access to these tools:
{tools_description}

## How to use tools

To use a tool, include a tool call in your response using this exact format:
```tool
{{"tool": "ToolName", "parameters": {{"param1": "value1", "param2": "value2"}}}}
```

## CRITICAL: When to STOP

You MUST stop and provide a final summary (without tool calls) when:
- A command/script runs successfully (exit code 0)
- The requested file has been created/edited
- The task is complete
- You've already run the same command successfully - DO NOT run it again

NEVER repeat the same successful tool call. If `python example.py` succeeds once, the task is DONE.

## Guidelines

1. **Read before writing**: Always read files before modifying them
2. **Be precise**: Use exact file paths and specific parameters
3. **Explain your actions**: Briefly explain what you're doing and why
4. **Handle errors**: If a tool fails, try a DIFFERENT approach instead of repeating the same command
5. **Know when to stop**: Once a task succeeds, STOP and summarize - don't repeat it
6. **Ask if unclear**: Use AskUser if you need clarification

## Building New Projects - IMPORTANT

When creating a new project or application:

1. **Always create a project directory first**:
   - Create a dedicated directory for the project (e.g., `my_project/`)
   - ALL project files go inside this directory
   - Example: For a "quantum simulator", create `quantum_simulator/` first

2. **Set up Python environment properly**:
   - Create a virtual environment: `python3 -m venv <project_dir>/venv`
   - Install packages using: `<project_dir>/venv/bin/pip install <package>`
   - Run scripts using: `<project_dir>/venv/bin/python <script.py>`
   - NEVER use bare `pip install` - always use the venv pip

3. **Project structure example**:
   ```
   project_name/
   ├── venv/              # Virtual environment
   ├── requirements.txt   # Dependencies
   ├── main.py           # Entry point
   ├── app.py            # Web app (if applicable)
   ├── static/           # Static files
   └── templates/        # HTML templates
   ```

4. **After writing files, verify they exist and have content**

## Error Recovery

- If a command fails 2 times with the same error, TRY A DIFFERENT APPROACH
- Don't keep repeating `pip install` if it fails - check the Python environment
- Use absolute paths when relative paths fail
- If a module is not found, verify the correct Python interpreter is being used

## Current context

Working directory: {cwd}
"""

    def __init__(
        self,
        llm=None,
        config: AgentConfig = None,
        registry: ToolRegistry = None,
        parent_agent: "Agent" = None,
    ):
        """Initialize the agent

        Args:
            llm: LLM adapter for generating responses
            config: Agent configuration
            registry: Tool registry (creates default if None)
            parent_agent: Parent agent if this is a sub-agent
        """
        self.llm = llm
        self.config = config or AgentConfig()
        self.registry = registry or self._create_default_registry()
        self.parent_agent = parent_agent

        self.state = AgentState.IDLE
        self.iteration_count = 0
        self.conversation_history: List[Dict[str, str]] = []
        self.tool_results: List[ToolResult] = []

        # Visual feedback
        self._spinner: Optional[ActionSpinner] = None

        # Loop detection - track failed commands to avoid repeating
        self._failed_commands: Dict[str, int] = {}  # command_signature -> failure_count
        self._last_error: Optional[str] = None

        # Advanced loop detection
        self._tool_sequence: List[str] = []  # Track tool names for pattern detection
        self._successful_commands: set = set()  # Track commands that already succeeded

        # Apply permission settings
        self._apply_permission_config()

    def _create_default_registry(self) -> ToolRegistry:
        """Create and populate default tool registry"""
        registry = ToolRegistry()

        # Register all built-in tools
        register_file_tools(registry)
        register_search_tools(registry)
        register_bash_tools(registry)
        task_tool = register_task_tools(registry, parent_agent=self)
        register_web_tools(registry)
        register_notebook_tools(registry)

        return registry

    def _apply_permission_config(self) -> None:
        """Apply permission configuration to registry"""
        # Set auto-approve tools
        for tool_name in self.config.auto_approve_tools:
            self.registry.set_permission(tool_name, ToolPermission.AUTO)

        # Set require-approval tools
        for tool_name in self.config.require_approval_tools:
            self.registry.set_permission(tool_name, ToolPermission.ASK)

        # Apply custom overrides
        for tool_name, permission in self.config.tool_permissions.items():
            self.registry.set_permission(tool_name, permission)

    def run(self, user_request: str) -> str:
        """
        Run the agent on a user request.

        Args:
            user_request: The user's request or task

        Returns:
            Final response or result
        """
        self.state = AgentState.THINKING
        self.iteration_count = 0
        self.conversation_history = []
        self.tool_results = []
        self._recent_tool_calls = []  # Track recent calls for loop detection

        # Build system prompt with tools
        import os
        system_prompt = self.SYSTEM_PROMPT.format(
            tools_description=self.registry.get_tools_prompt(),
            cwd=os.getcwd(),
        )

        # Add user request
        self.conversation_history.append({
            "role": "system",
            "content": system_prompt,
        })
        self.conversation_history.append({
            "role": "user",
            "content": user_request,
        })

        # Main execution loop
        while self.iteration_count < self.config.max_iterations:
            self.iteration_count += 1

            if HAS_CLI_UI:
                thinking(f"Iteration {self.iteration_count}...")

            try:
                # Get LLM response
                response = self._get_llm_response()

                # Parse for tool calls
                tool_calls = self._parse_tool_calls(response)

                if not tool_calls:
                    # No tool calls - agent is done or providing final response
                    self.state = AgentState.COMPLETED
                    return self._clean_response(response)

                # Detect loops - same tool call made 3+ times
                current_call_sig = [(tc.name, str(tc.arguments)) for tc in tool_calls]
                self._recent_tool_calls.append(current_call_sig)
                if len(self._recent_tool_calls) >= 3:
                    last_three = self._recent_tool_calls[-3:]
                    if last_three[0] == last_three[1] == last_three[2]:
                        if HAS_CLI_UI:
                            warning("Detected loop - same tool called 3 times. Stopping.")
                        self.state = AgentState.COMPLETED
                        return "Task completed (detected repetitive tool calls)."

                # Execute tool calls
                all_results = []
                for tool_call in tool_calls:
                    result = self._execute_tool_call(tool_call)
                    all_results.append(result)
                    self.tool_results.append(result)

                # Add results to conversation
                results_text = self._format_tool_results(all_results)
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                })

                # Check if all tools succeeded - if so, strongly hint task may be done
                all_succeeded = all(r.success for r in all_results)
                has_bash = any(tc.name == "Bash" for tc in tool_calls)
                has_write = any(tc.name in ["Write", "Edit"] for tc in tool_calls)

                # Check for silent success (command succeeded but no output)
                silent_success = all_succeeded and all(
                    not r.output.strip() for r in all_results
                )

                if all_succeeded and has_bash:
                    # Bash command succeeded - task is likely complete
                    if silent_success:
                        follow_up = (
                            f"Tool results:\n{results_text}\n\n"
                            "The command completed successfully with no output (exit code 0). "
                            "This typically means the operation succeeded. "
                            "Provide a final summary of what was accomplished WITHOUT any more tool calls."
                        )
                    else:
                        follow_up = (
                            f"Tool results:\n{results_text}\n\n"
                            "The command executed successfully. "
                            "If this completes the user's request, provide a final summary WITHOUT any tool calls. "
                            "Only use more tools if there are additional steps needed."
                        )
                elif all_succeeded and has_write:
                    # File was written/edited successfully
                    follow_up = (
                        f"Tool results:\n{results_text}\n\n"
                        "The file was successfully created/modified. "
                        "If this completes the task, provide a summary. "
                        "Do NOT read the file back unless the user asked to verify it."
                    )
                elif all_succeeded:
                    follow_up = (
                        f"Tool results:\n{results_text}\n\n"
                        "All tools succeeded. Provide a summary if the task is complete, or continue with the next step."
                    )
                else:
                    # Some failed - analyze failure type
                    failed_results = [r for r in all_results if not r.success]
                    loop_detected = any("LOOP" in (r.error or "") or "REDUNDANT" in (r.error or "") for r in failed_results)

                    if loop_detected:
                        follow_up = (
                            f"Tool results:\n{results_text}\n\n"
                            "A loop or redundant operation was detected. "
                            "STOP and either: 1) Provide a final summary if the task is done, or "
                            "2) Explain what's blocking progress and ask the user for guidance."
                        )
                    else:
                        follow_up = (
                            f"Tool results:\n{results_text}\n\n"
                            "Some tools failed. Try a DIFFERENT approach - don't repeat the same command. "
                            "If you've tried multiple approaches without success, ask the user for help."
                        )

                self.conversation_history.append({
                    "role": "user",
                    "content": follow_up,
                })

            except Exception as e:
                self.state = AgentState.ERROR
                if HAS_CLI_UI:
                    error(f"Agent error: {e}")
                return f"Error during execution: {e}"

        # Max iterations reached
        self.state = AgentState.COMPLETED
        if HAS_CLI_UI:
            warning(f"Reached maximum iterations ({self.config.max_iterations})")
        return "Task incomplete - reached maximum iterations."

    def _get_llm_response(self) -> str:
        """Get response from LLM"""
        if self.llm is None:
            raise ValueError("No LLM configured for agent")

        # Build messages for LLM
        messages = self.conversation_history.copy()

        # Get completion
        response = self.llm.chat(messages)
        return response

    def _parse_tool_calls(self, response: str) -> List[ToolCall]:
        """Parse tool calls from LLM response"""
        tool_calls = []

        # Pattern 1: ```tool ... ``` blocks
        pattern = r"```tool\s*\n?(.*?)\n?```"
        matches = re.findall(pattern, response, re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match.strip())
                if "tool" in data:
                    tool_calls.append(ToolCall(
                        name=data["tool"],
                        parameters=data.get("parameters", {}),
                        raw_text=match,
                    ))
            except json.JSONDecodeError:
                continue

        # Pattern 2: JSON objects with "tool" key
        json_pattern = r'\{[^{}]*"tool"\s*:\s*"[^"]+"\s*[^{}]*\}'
        json_matches = re.findall(json_pattern, response)

        for match in json_matches:
            if match not in [tc.raw_text for tc in tool_calls]:
                try:
                    data = json.loads(match)
                    if "tool" in data:
                        tool_calls.append(ToolCall(
                            name=data["tool"],
                            parameters=data.get("parameters", {}),
                            raw_text=match,
                        ))
                except json.JSONDecodeError:
                    continue

        return tool_calls

    def _get_command_signature(self, tool_call: ToolCall) -> str:
        """Get a signature for a tool call to detect repeated failures"""
        import hashlib
        sig_data = f"{tool_call.name}:{json.dumps(tool_call.parameters, sort_keys=True)}"
        return hashlib.md5(sig_data.encode()).hexdigest()[:12]

    def _check_loop_detection(self, tool_call: ToolCall) -> Optional[str]:
        """Check if this command has failed too many times

        Returns:
            Warning message if loop detected, None otherwise
        """
        sig = self._get_command_signature(tool_call)

        # Check 1: Same command failed too many times
        fail_count = self._failed_commands.get(sig, 0)
        if fail_count >= self.config.max_same_error_retries:
            return (
                f"LOOP DETECTED: This command has failed {fail_count} times with the same error. "
                f"You MUST try a DIFFERENT approach instead of repeating this command. "
                f"Last error: {self._last_error}"
            )

        # Check 2: Trying to repeat a command that already succeeded
        if sig in self._successful_commands:
            return (
                f"REDUNDANT COMMAND: This exact command already succeeded. "
                f"Do NOT repeat it. If the task is complete, provide a summary. "
                f"If you need different output, modify the command parameters."
            )

        return None

    def _check_alternating_pattern(self) -> Optional[str]:
        """Detect alternating tool patterns like Read→Edit→Read→Edit

        Returns:
            Warning message if pattern detected, None otherwise
        """
        seq = self._tool_sequence
        if len(seq) < 4:
            return None

        # Check for 2-tool alternating pattern (e.g., Read→Edit→Read→Edit)
        if len(seq) >= 6:
            last_six = seq[-6:]
            if (last_six[0] == last_six[2] == last_six[4] and
                last_six[1] == last_six[3] == last_six[5] and
                last_six[0] != last_six[1]):
                return (
                    f"ALTERNATING LOOP DETECTED: Pattern {last_six[0]}→{last_six[1]} repeated 3 times. "
                    f"You appear to be stuck in a loop. Stop and summarize what you've accomplished, "
                    f"or try a completely different approach."
                )

        # Check for single-tool repetition (already covered elsewhere but double-check)
        if len(seq) >= 4 and seq[-1] == seq[-2] == seq[-3] == seq[-4]:
            return (
                f"REPETITION DETECTED: {seq[-1]} called 4 times in a row. "
                f"Stop repeating and either complete the task or try a different approach."
            )

        return None

    def _record_success(self, tool_call: ToolCall) -> None:
        """Record a successful command to prevent redundant repeats"""
        sig = self._get_command_signature(tool_call)
        self._successful_commands.add(sig)

    def _record_failure(self, tool_call: ToolCall, error: str) -> None:
        """Record a command failure for loop detection"""
        sig = self._get_command_signature(tool_call)
        self._failed_commands[sig] = self._failed_commands.get(sig, 0) + 1
        self._last_error = error

    def _execute_tool_call(self, tool_call: ToolCall) -> ToolResult:
        """Execute a single tool call"""
        tool = self.registry.get(tool_call.name)

        if not tool:
            return ToolResult(
                success=False,
                output="",
                error=f"Unknown tool: {tool_call.name}",
                tool_name=tool_call.name,
                target=str(tool_call.parameters)[:30],
            )

        # Track tool sequence for alternating pattern detection
        self._tool_sequence.append(tool_call.name)

        # Loop detection - check if this command has failed too many times or already succeeded
        loop_warning = self._check_loop_detection(tool_call)
        if loop_warning:
            if HAS_CLI_UI:
                warning(f"Loop detected for {tool_call.name}")
            return ToolResult(
                success=False,
                output="",
                error=loop_warning,
                tool_name=tool_call.name,
                target=tool._get_target(**tool_call.parameters),
            )

        # Check for alternating tool patterns
        alt_warning = self._check_alternating_pattern()
        if alt_warning:
            if HAS_CLI_UI:
                warning("Alternating pattern detected")
            return ToolResult(
                success=False,
                output="",
                error=alt_warning,
                tool_name=tool_call.name,
                target=tool._get_target(**tool_call.parameters),
            )

        # Check permission - special handling for Bash with safe commands
        needs_approval = self.registry.needs_approval(tool_call.name)

        # For Bash tool, check if command is safe (read-only)
        if tool_call.name == "Bash" and "command" in tool_call.parameters:
            from .tools.bash_tool import BashTool
            if BashTool.is_safe_command(tool_call.parameters["command"]):
                needs_approval = False

        if needs_approval:
            self.state = AgentState.WAITING_APPROVAL
            approved = self._request_approval(tool_call)
            if not approved:
                return ToolResult(
                    success=False,
                    output="",
                    error="Tool execution denied by user",
                    tool_name=tool_call.name,
                    target=tool._get_target(**tool_call.parameters),
                )

        # Execute tool
        self.state = AgentState.EXECUTING_TOOL

        if HAS_CLI_UI:
            target = tool._get_target(**tool_call.parameters)
            log_action(tool_call.name, target, "running")

        result = tool.run(**tool_call.parameters)

        # Track results for loop detection
        if result.success:
            self._record_success(tool_call)
        else:
            self._record_failure(tool_call, result.error or "Unknown error")

        if HAS_CLI_UI:
            # Show output using Claude Code style (corner indentation)
            if self.config.show_tool_output:
                if result.success and result.output:
                    log_output(result.output, is_error=False, max_lines=15)
                elif not result.success and result.error:
                    log_output(result.error, is_error=True, max_lines=10)

        return result

    def _request_approval(self, tool_call: ToolCall) -> bool:
        """Request user approval for a tool call"""
        tool = self.registry.get(tool_call.name)
        target = tool._get_target(**tool_call.parameters) if tool else ""

        # Claude Code style approval prompt
        print(f"\n{Color.YELLOW}{Icons.BULLET}{Color.RESET} {Color.BOLD}{tool_call.name}{Color.RESET}({Color.CYAN}{target}{Color.RESET})")

        if tool_call.parameters:
            # Show parameters with corner indentation
            params_str = json.dumps(tool_call.parameters, indent=2)
            for i, line in enumerate(params_str.split('\n')[:5]):
                if i == 0:
                    print(f"  {Color.DIM}{Icons.CORNER}{Color.RESET}  {Color.DIM}{line}{Color.RESET}")
                else:
                    print(f"      {Color.DIM}{line}{Color.RESET}")

        response = input(f"\n{Color.BOLD}Allow?{Color.RESET} [y/N/always]: ").strip().lower()

        if response == "always":
            self.registry.approve_for_session(tool_call.name)
            return True
        elif response in ["y", "yes"]:
            return True
        else:
            return False

    def _format_tool_results(self, results: List[ToolResult]) -> str:
        """Format tool results for conversation"""
        parts = []
        for result in results:
            if result.success:
                parts.append(f"✓ {result.tool_name}({result.target}):\n{result.output}")
            else:
                parts.append(f"✗ {result.tool_name}({result.target}) failed: {result.error}")
        return "\n\n".join(parts)

    def _clean_response(self, response: str) -> str:
        """Clean tool call markers from final response"""
        # Remove tool blocks
        response = re.sub(r"```tool\s*\n?.*?\n?```", "", response, flags=re.DOTALL)
        # Remove JSON tool calls
        response = re.sub(r'\{[^{}]*"tool"\s*:\s*"[^"]+"\s*[^{}]*\}', "", response)
        return response.strip()

    def get_tool_history(self) -> List[Dict[str, Any]]:
        """Get history of tool calls and results"""
        return [
            {
                "tool": r.tool_name,
                "target": r.target,
                "success": r.success,
                "duration_ms": r.duration_ms,
            }
            for r in self.tool_results
        ]


def create_agent(llm=None, **config_kwargs) -> Agent:
    """Create an agent with default configuration

    Args:
        llm: LLM adapter
        **config_kwargs: Configuration overrides

    Returns:
        Configured Agent instance
    """
    config = AgentConfig(**config_kwargs)
    return Agent(llm=llm, config=config)
