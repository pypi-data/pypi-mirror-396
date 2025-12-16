"""
Tool abstraction for the delegate framework.

Tools are the building blocks that agents can use to accomplish tasks.
Each tool defines its input schema and output schema using Pydantic models.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

# Type variables for tool input and output
T = TypeVar("T", bound=BaseModel)
R = TypeVar("R", bound=BaseModel)


class Tool(ABC, BaseModel, Generic[T, R]):
    """
    Base class for tools that can be used by agents.
    
    Tools define:
    - name: A human-readable name for the tool
    - description: What the tool does (used in LLM prompts)
    - instruction_schema: Pydantic model defining the tool's input parameters
    - result_schema: Pydantic model defining the tool's output structure
    
    Subclasses must implement the `run` method to execute the tool.
    """

    name: str
    description: str
    instruction_schema: type[T]
    result_schema: type[R]

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    async def run(self, instruction: T) -> R:
        """
        Execute the tool with the given instruction.
        
        Args:
            instruction: Validated input matching instruction_schema
            
        Returns:
            Result matching result_schema
        """
        pass

