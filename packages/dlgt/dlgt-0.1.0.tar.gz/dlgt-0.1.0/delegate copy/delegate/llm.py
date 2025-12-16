"""
LLM abstraction interface for the delegate framework.

This module defines the interface that LLM providers must implement.
This allows the framework to work with different LLM backends.
"""

from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel


class Message(BaseModel):
    """A message in a conversation."""

    role: Literal["system", "user", "assistant"]
    content: str


class ToolCall(BaseModel):
    """Represents a tool call selected by the LLM."""

    name: str
    arguments: dict[str, Any]


class LLMProvider(ABC):
    """
    Abstract interface for LLM providers.
    
    Implementations should handle:
    - Sending messages to the LLM
    - Function calling/tool selection
    - Streaming responses (optional)
    """

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> tuple[str | None, ToolCall | None]:
        """
        Send messages to the LLM and get a response.
        
        Args:
            messages: Conversation history
            tools: Optional list of available tools (OpenAI function format)
            
        Returns:
            Tuple of (text_response, tool_call)
            - If text_response is not None, the LLM responded with text
            - If tool_call is not None, the LLM selected a tool to call
            - Both can be None if the LLM didn't respond
        """
        pass

