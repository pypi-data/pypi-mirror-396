"""
Delegate - A clean, simple framework for delegated agents.

This framework provides a minimal abstraction for building agentic AI systems
where agents can select and execute tools to complete tasks.
"""

from delegate.agent import Agent
from delegate.task import Task, TaskResult
from delegate.tool import Tool

__all__ = ["Agent", "Tool", "Task", "TaskResult"]

