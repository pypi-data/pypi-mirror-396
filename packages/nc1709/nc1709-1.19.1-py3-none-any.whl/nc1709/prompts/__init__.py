"""
NC1709 Prompt System

Provides task-specific prompts to improve LLM performance on different types of requests.
"""

from .agent_system import get_agent_prompt, AGENT_SYSTEM_PROMPT
from .task_prompts import (
    detect_task_type,
    get_task_prompt,
    get_full_prompt,
    TaskType,
)

__all__ = [
    'get_agent_prompt',
    'AGENT_SYSTEM_PROMPT',
    'detect_task_type',
    'get_task_prompt',
    'get_full_prompt',
    'TaskType',
]
