"""
Simple example of using the delegate framework.

This example shows how to:
1. Define a tool
2. Create an agent
3. Run a task
"""

import asyncio
from uuid import uuid4

from pydantic import BaseModel

from delegate import Agent, Task
from delegate.llm import LLMProvider, Message, ToolCall
from delegate.tool import Tool


# Example: A simple calculator tool
class CalculatorInput(BaseModel):
    operation: str
    a: float
    b: float


class CalculatorOutput(BaseModel):
    result: float


class CalculatorTool(Tool[CalculatorInput, CalculatorOutput]):
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Performs basic arithmetic operations (add, subtract, multiply, divide)",
            instruction_schema=CalculatorInput,
            result_schema=CalculatorOutput,
        )

    async def run(self, instruction: CalculatorInput) -> CalculatorOutput:
        if instruction.operation == "add":
            result = instruction.a + instruction.b
        elif instruction.operation == "subtract":
            result = instruction.a - instruction.b
        elif instruction.operation == "multiply":
            result = instruction.a * instruction.b
        elif instruction.operation == "divide":
            if instruction.b == 0:
                raise ValueError("Cannot divide by zero")
            result = instruction.a / instruction.b
        else:
            raise ValueError(f"Unknown operation: {instruction.operation}")
        return CalculatorOutput(result=result)


# Example: A mock LLM provider (for demonstration)
class MockLLMProvider(LLMProvider):
    """A simple mock LLM that selects tools based on keywords."""

    async def chat(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> tuple[str | None, ToolCall | None]:
        # Get the last user message
        last_message = next((m for m in reversed(messages) if m.role == "user"), None)
        if not last_message:
            return None, None

        content = last_message.content.lower()

        # Simple keyword-based tool selection
        if "calculate" in content or "math" in content or "+" in content:
            # Extract numbers (very simple)
            import re

            numbers = re.findall(r"\d+", content)
            if len(numbers) >= 2:
                a, b = float(numbers[0]), float(numbers[1])
                operation = "add" if "+" in content else "multiply"
                return None, ToolCall(
                    name="calculator",
                    arguments={"operation": operation, "a": a, "b": b},
                )

        return "I can help with calculations. Try asking me to calculate something.", None


async def main():
    # Create the agent
    agent = Agent(
        name="math_agent",
        system_prompt="You are a helpful math assistant. Use the calculator tool to perform calculations.",
        available_tools=[CalculatorTool()],
        llm=MockLLMProvider(),
        max_iterations=5,
    )

    # Create and run a task
    task = Task(
        id=uuid4(),
        instruction="Calculate 15 + 27",
    )

    print(f"Running task: {task.instruction}")
    result = await agent.run(task)

    print(f"\nResult: {result.status}")
    print(f"Content: {result.content}")
    print(f"Reasoning: {result.reasoning}")

    print(f"\nExecution log ({len(task.execution_log)} steps):")
    for i, execution in enumerate(task.execution_log, 1):
        print(f"  {i}. {execution.tool_name}: {execution.instruction}")


if __name__ == "__main__":
    asyncio.run(main())

