"""
NC1709 Built-in Agents
Specialized plugins for common development tasks
"""

from .git_agent import GitAgent
from .docker_agent import DockerAgent
from .fastapi_agent import FastAPIAgent
from .nextjs_agent import NextJSAgent
from .django_agent import DjangoAgent

__all__ = [
    "GitAgent",
    "DockerAgent",
    "FastAPIAgent",
    "NextJSAgent",
    "DjangoAgent"
]
