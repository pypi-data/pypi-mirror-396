"""
Task abstraction for tracking agent execution state.

Tasks represent work that needs to be done and track the execution history
including tool calls and their results.
"""

from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel


class TaskResult(BaseModel):
    """Result of a task execution."""

    content: str
    reasoning: str
    status: Literal["success", "failure"]


class ToolExecution(BaseModel):
    """Represents a single tool execution within a task."""

    tool_name: str
    instruction: dict
    result: dict
    assessment: str | None = None


class Task(BaseModel):
    """
    Represents a task that an agent needs to complete.
    
    Tasks track:
    - The instruction/objective
    - Execution history (tool calls)
    - Final result
    - Metadata (id, parent relationships)
    """

    id: UUID
    instruction: str
    result: TaskResult | None = None
    execution_log: list[ToolExecution] = []
    parent_id: UUID | None = None
    metadata: dict = {}

    def add_execution(
        self,
        tool_name: str,
        instruction: dict,
        result: dict,
        assessment: str | None = None,
    ) -> None:
        """Add a tool execution to the log."""
        self.execution_log.append(
            ToolExecution(
                tool_name=tool_name,
                instruction=instruction,
                result=result,
                assessment=assessment,
            )
        )

    def create_subtask(self, instruction: str, metadata: dict | None = None) -> "Task":
        """Create a child task."""
        return Task(
            id=uuid4(),
            instruction=instruction,
            parent_id=self.id,
            metadata=metadata or {},
        )

