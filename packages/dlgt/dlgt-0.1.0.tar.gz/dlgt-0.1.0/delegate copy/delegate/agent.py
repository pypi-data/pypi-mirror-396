"""
Agent implementation for the delegate framework.

Agents use LLMs to select and execute tools to complete tasks.
They maintain execution loops with reflection to determine when tasks are complete.
"""

from typing import Literal

from pydantic import BaseModel

from delegate.llm import LLMProvider, Message, ToolCall
from delegate.task import Task, TaskResult
from delegate.tool import Tool


class ReflectionResult(BaseModel):
    """Result of reflecting on a tool execution."""

    assessment: str
    implications: str
    is_complete: bool


class Agent(BaseModel):
    """
    An agent that uses an LLM to select and execute tools.
    
    Agents:
    1. Receive a task with an instruction
    2. Use an LLM to select appropriate tools
    3. Execute selected tools
    4. Reflect on results to determine if the task is complete
    5. Repeat until complete or max iterations reached
    """

    name: str
    system_prompt: str
    available_tools: list[Tool]
    llm: LLMProvider
    max_iterations: int = 30
    reflection_prompt: str = (
        "After each tool execution, assess whether the task is complete. "
        "Consider the tool's output and whether it achieved the goal. "
        "If the task is complete, set is_complete to true. "
        "Otherwise, provide implications for next steps."
    )

    class Config:
        arbitrary_types_allowed = True

    def _build_tool_schema(self, tool: Tool) -> dict:
        """Convert a tool to OpenAI function calling format."""
        schema = tool.instruction_schema.model_json_schema()
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": schema,
            },
        }

    def _build_messages(
        self,
        task: Task,
        include_reflection: bool = False,
        last_tool_result: str | None = None,
    ) -> list[Message]:
        """Build the message history for the LLM."""
        messages: list[Message] = [
            Message(role="system", content=self.system_prompt),
        ]

        # Add task instruction
        messages.append(
            Message(role="user", content=f"Task: {task.instruction}")
        )

        # Add execution history
        for execution in task.execution_log:
            tool_info = (
                f"Tool: {execution.tool_name}\n"
                f"Input: {execution.instruction}\n"
                f"Output: {execution.result}\n"
            )
            if execution.assessment:
                tool_info += f"Assessment: {execution.assessment}\n"
            messages.append(Message(role="assistant", content=tool_info))

        # Add reflection prompt if needed
        if include_reflection and last_tool_result:
            reflection_content = (
                f"{self.reflection_prompt}\n\n"
                f"Latest tool result:\n{last_tool_result}\n\n"
                "Respond with a JSON object containing: assessment (string), "
                "implications (string), is_complete (boolean)."
            )
            messages.append(Message(role="system", content=reflection_content))

        return messages

    async def _select_tool(self, task: Task) -> tuple[Tool, dict]:
        """Use the LLM to select a tool and generate its input."""
        tools_schema = [self._build_tool_schema(tool) for tool in self.available_tools]

        messages = self._build_messages(task)
        # Add tool selection instruction
        messages.append(
            Message(
                role="system",
                content=(
                    "Select one tool from the available tools to proceed with the task. "
                    "Do not repeat the same tool call with identical inputs."
                ),
            )
        )

        text_response, tool_call = await self.llm.chat(messages, tools=tools_schema)

        if tool_call is None:
            raise ValueError("LLM did not select a tool")

        # Find the tool
        tool_registry = {tool.name: tool for tool in self.available_tools}
        tool = tool_registry.get(tool_call.name)
        if tool is None:
            raise ValueError(f"Tool {tool_call.name} not found")

        # Validate the instruction
        instruction = tool.instruction_schema.model_validate(tool_call.arguments)
        return tool, instruction.model_dump()

    async def _reflect(
        self, task: Task, tool_name: str, tool_result: dict
    ) -> ReflectionResult:
        """Reflect on a tool execution to determine if the task is complete."""
        result_str = f"Tool: {tool_name}\nResult: {tool_result}"

        messages = self._build_messages(
            task, include_reflection=True, last_tool_result=result_str
        )

        text_response, _ = await self.llm.chat(messages)

        if text_response is None:
            # Default to not complete if reflection fails
            return ReflectionResult(
                assessment="Reflection failed",
                implications="Continue with next tool",
                is_complete=False,
            )

        # Try to parse JSON from the response
        import json
        import re

        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r"\{.*\}", text_response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return ReflectionResult(
                    assessment=data.get("assessment", ""),
                    implications=data.get("implications", ""),
                    is_complete=data.get("is_complete", False),
                )
            except json.JSONDecodeError:
                pass

        # Fallback: simple heuristic
        is_complete = "complete" in text_response.lower() or "done" in text_response.lower()
        return ReflectionResult(
            assessment=text_response,
            implications="Continue with next tool",
            is_complete=is_complete,
        )

    async def run(self, task: Task) -> TaskResult:
        """
        Run the agent to complete the task.
        
        The agent will:
        1. Select tools using the LLM
        2. Execute selected tools
        3. Reflect on results
        4. Repeat until complete or max iterations
        """
        for iteration in range(self.max_iterations):
            try:
                # Select and execute a tool
                tool, instruction_dict = await self._select_tool(task)

                # Execute the tool
                instruction = tool.instruction_schema.model_validate(instruction_dict)
                result = await tool.run(instruction)
                result_dict = result.model_dump()

                # Add to execution log
                task.add_execution(
                    tool_name=tool.name,
                    instruction=instruction_dict,
                    result=result_dict,
                )

                # Reflect on the result
                reflection = await self._reflect(task, tool.name, result_dict)
                task.execution_log[-1].assessment = reflection.assessment

                # Check if task is complete
                if reflection.is_complete:
                    task_result = TaskResult(
                        content=str(result_dict),
                        reasoning=reflection.assessment,
                        status="success",
                    )
                    task.result = task_result
                    return task_result

            except Exception as e:
                # On error, return failure
                task_result = TaskResult(
                    content=f"Error: {str(e)}",
                    reasoning="An error occurred during execution",
                    status="failure",
                )
                task.result = task_result
                return task_result

        # Max iterations reached
        task_result = TaskResult(
            content="Maximum iterations reached without completing the task",
            reasoning="The agent exceeded the maximum number of iterations",
            status="failure",
        )
        task.result = task_result
        return task_result

