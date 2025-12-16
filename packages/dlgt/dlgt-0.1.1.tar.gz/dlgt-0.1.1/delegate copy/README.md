# Delegate

A clean, simple framework for building delegated agents. This framework provides a minimal abstraction for creating agentic AI systems where agents can select and execute tools to complete tasks.

## Core Concepts

### Tool
Tools are the building blocks that agents use. Each tool defines:
- **name**: A human-readable identifier
- **description**: What the tool does (used in LLM prompts)
- **instruction_schema**: Pydantic model for input parameters
- **result_schema**: Pydantic model for output structure

### Agent
Agents orchestrate tool execution:
1. Receive a task with an instruction
2. Use an LLM to select appropriate tools
3. Execute selected tools
4. Reflect on results to determine completion
5. Repeat until complete or max iterations reached

### Task
Tasks represent work to be done and track:
- The instruction/objective
- Execution history (tool calls)
- Final result
- Metadata

## Quick Start

```python
from delegate import Agent, Tool, Task
from delegate.llm import LLMProvider, Message, ToolCall
from pydantic import BaseModel

# Define a simple tool
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
            description="Performs basic arithmetic operations",
            instruction_schema=CalculatorInput,
            result_schema=CalculatorOutput,
        )

    async def run(self, instruction: CalculatorInput) -> CalculatorOutput:
        if instruction.operation == "add":
            result = instruction.a + instruction.b
        elif instruction.operation == "multiply":
            result = instruction.a * instruction.b
        else:
            raise ValueError(f"Unknown operation: {instruction.operation}")
        return CalculatorOutput(result=result)

# Implement an LLM provider (e.g., OpenAI)
class OpenAIProvider(LLMProvider):
    # ... implementation ...

# Create an agent
agent = Agent(
    name="math_agent",
    system_prompt="You are a helpful math assistant.",
    available_tools=[CalculatorTool()],
    llm=OpenAIProvider(),
)

# Run a task
from uuid import uuid4

task = Task(
    id=uuid4(),
    instruction="Calculate 5 + 3",
)
result = await agent.run(task)
print(result.status)  # "success"
```

## Architecture

The framework is designed to be:
- **Simple**: Minimal abstractions, easy to understand
- **Flexible**: Works with any LLM provider via the `LLMProvider` interface
- **Type-safe**: Uses Pydantic for validation throughout
- **Extensible**: Easy to add new tools and agents

## Installation

```bash
pip install -e .
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff format .

# Lint code
ruff check .
```

