"""
Task Tool - Sub-agent Spawning

Allows spawning sub-agents for complex, multi-step tasks.
Each sub-agent can use tools and work autonomously.
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
import threading
import queue

from .base import Tool, ToolResult, ToolParameter, ToolPermission

if TYPE_CHECKING:
    from ..core import Agent


class TaskTool(Tool):
    """Spawn a sub-agent for complex tasks"""

    name = "Task"
    description = (
        "Launch a sub-agent to handle a complex, multi-step task autonomously. "
        "The sub-agent has access to all tools and can work independently. "
        "Use for tasks that require multiple steps or exploration."
    )
    category = "agent"
    permission = ToolPermission.ASK  # Ask before spawning

    parameters = [
        ToolParameter(
            name="prompt",
            description="Detailed task description for the sub-agent",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="description",
            description="Short description of the task (3-5 words)",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="agent_type",
            description="Type of agent to spawn",
            type="string",
            required=False,
            default="general",
            enum=["general", "explore", "code", "research"],
        ),
    ]

    def __init__(self, parent_agent: "Agent" = None):
        super().__init__()
        self.parent_agent = parent_agent
        self._running_tasks: Dict[str, Dict] = {}
        self._task_counter = 0

    def set_parent_agent(self, agent: "Agent") -> None:
        """Set the parent agent for spawning sub-agents"""
        self.parent_agent = agent

    def execute(
        self,
        prompt: str,
        description: str,
        agent_type: str = "general",
    ) -> ToolResult:
        """Spawn a sub-agent to handle a task"""

        if not self.parent_agent:
            return ToolResult(
                success=False,
                output="",
                error="No parent agent configured for task spawning",
                target=description,
            )

        try:
            # Create sub-agent with same configuration
            from ..core import Agent, AgentConfig

            # Configure sub-agent based on type
            config = AgentConfig(
                max_iterations=20,  # Limit sub-agent iterations
                tool_permissions=self.parent_agent.config.tool_permissions.copy(),
            )

            # Create sub-agent
            sub_agent = Agent(
                llm=self.parent_agent.llm,
                config=config,
                parent_agent=self.parent_agent,
            )

            # Add context about this being a sub-agent
            context = f"""You are a sub-agent spawned to handle a specific task.
Your task: {description}

Detailed instructions:
{prompt}

Work autonomously to complete this task. Use available tools as needed.
When complete, provide a clear summary of what you accomplished.
"""

            # Run sub-agent synchronously for now
            # (could be made async for parallel tasks)
            result = sub_agent.run(context)

            return ToolResult(
                success=True,
                output=f"Sub-agent completed task: {description}\n\nResult:\n{result}",
                target=description,
                data={
                    "agent_type": agent_type,
                    "iterations": sub_agent.iteration_count,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error running sub-agent: {e}",
                target=description,
            )


class TodoWriteTool(Tool):
    """Manage a task list for tracking progress"""

    name = "TodoWrite"
    description = (
        "Create or update a todo list to track task progress. "
        "Use this to plan complex tasks and show progress to the user."
    )
    category = "agent"
    permission = ToolPermission.AUTO  # Safe to auto-execute

    parameters = [
        ToolParameter(
            name="todos",
            description="List of todo items with status",
            type="array",
            required=True,
        ),
    ]

    # Class-level todo storage
    _todos: list = []

    def execute(self, todos: list) -> ToolResult:
        """Update the todo list"""

        try:
            # Validate todo format
            validated_todos = []
            for item in todos:
                if isinstance(item, dict):
                    validated_todos.append({
                        "content": item.get("content", ""),
                        "status": item.get("status", "pending"),
                        "activeForm": item.get("activeForm", item.get("content", "")),
                    })
                elif isinstance(item, str):
                    validated_todos.append({
                        "content": item,
                        "status": "pending",
                        "activeForm": item,
                    })

            TodoWriteTool._todos = validated_todos

            # Format output
            output_lines = ["Todo list updated:"]
            for i, todo in enumerate(validated_todos, 1):
                status_icon = {
                    "pending": "○",
                    "in_progress": "●",
                    "completed": "✓",
                }.get(todo["status"], "○")
                output_lines.append(f"  {status_icon} {i}. {todo['content']}")

            return ToolResult(
                success=True,
                output="\n".join(output_lines),
                target=f"{len(validated_todos)} items",
                data={"todos": validated_todos},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error updating todos: {e}",
                target="todos",
            )

    @classmethod
    def get_todos(cls) -> list:
        """Get current todo list"""
        return cls._todos.copy()

    @classmethod
    def clear_todos(cls) -> None:
        """Clear the todo list"""
        cls._todos = []


class AskUserTool(Tool):
    """Ask the user a question"""

    name = "AskUser"
    description = (
        "Ask the user a question to clarify requirements or get a decision. "
        "Use when you need user input to proceed."
    )
    category = "agent"
    permission = ToolPermission.AUTO  # Safe - just asks question

    parameters = [
        ToolParameter(
            name="question",
            description="The question to ask the user",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="options",
            description="Optional list of choices for the user",
            type="array",
            required=False,
        ),
    ]

    def __init__(self, input_callback=None):
        super().__init__()
        self.input_callback = input_callback or input

    def execute(self, question: str, options: list = None) -> ToolResult:
        """Ask user a question"""

        try:
            # Display question
            print(f"\n❓ {question}")

            if options:
                for i, opt in enumerate(options, 1):
                    print(f"  {i}. {opt}")
                print()

            # Get user input
            response = self.input_callback("> ").strip()

            # If options provided and user entered a number, map to option
            if options and response.isdigit():
                idx = int(response) - 1
                if 0 <= idx < len(options):
                    response = options[idx]

            return ToolResult(
                success=True,
                output=f"User response: {response}",
                target=question[:30],
                data={"response": response},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error getting user input: {e}",
                target=question[:30],
            )


def register_task_tools(registry, parent_agent=None):
    """Register task management tools with a registry"""
    task_tool = TaskTool(parent_agent)
    registry.register(task_tool)
    registry.register_class(TodoWriteTool)
    registry.register_class(AskUserTool)
    return task_tool  # Return so parent_agent can be set later
