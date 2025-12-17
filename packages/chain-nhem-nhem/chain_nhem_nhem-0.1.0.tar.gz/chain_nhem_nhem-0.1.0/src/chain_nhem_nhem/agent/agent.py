from chain_nhem_nhem.core.messages import Message
from chain_nhem_nhem.tools.base import Tool
from chain_nhem_nhem.tools.registry import ToolRegistry
from chain_nhem_nhem.llm.llm_driver import LLMDriver
from chain_nhem_nhem.agent.models import AgentResult


class Agent:
    def __init__(self, driver: LLMDriver, tool_registry: ToolRegistry, driver_name: str, max_steps: int = 5):
        self.driver = driver
        self.tool_registry = tool_registry
        self.driver_name = driver_name
        self.max_steps = max_steps

    def run(self, user_input: str) -> AgentResult:
        steps = []
        tools_used = []
        total_tokens = 0

        messages = [
            Message(role="user", content=user_input)
        ]

        steps.append(f"User input: {user_input}")

        for step in range(self.max_steps):
            response = self.driver.generate(
                messages=messages,
                tools=self.tool_registry.for_driver(self.driver_name)
            )

            if response.tokens_used:
                total_tokens += response.tokens_used

            # Final answer
            if response.type == "message":
                steps.append(f"Step: {step + 1} - Final answer generated")
                return AgentResult(
                    output=response.content,
                    steps=steps,
                    tools_used=tools_used,
                    tokens=total_tokens
                )

            # 🔧 Tool call
            if response.type == "tool_call":
                tool_name = response.tool_name
                tools_used.append(tool_name)
                steps.append(f"Model called tool: {tool_name}")

                tool = self.tool_registry.get(tool_name)
                if not tool or not isinstance(tool, Tool):
                    raise RuntimeError(f"Tool '{tool_name}' not found")

                args = tool.args_schema(**response.tool_args)
                result = tool(args)

                steps.append(f"Step: {step + 1} - Tool '{tool_name}' returned: {result}")

                # Gemini workaround
                messages.append(
                    Message(
                        role="user",
                        content=f"Tool result ({tool_name}): {result}"
                    )
                )
                continue
                
        raise RuntimeError(f"Agent exceeded max steps ({self.max_steps}) without final answer")