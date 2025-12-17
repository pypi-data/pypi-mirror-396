import os
from openai import OpenAI
from openai.agents import Agent, Runner, RunHooks, RunContextWrapper
from typing import Any

# Ensure you have the library installed: pip install openai openai-agents-sdk

class MyRunHooks(RunHooks):
    """
    A custom RunHooks implementation to track token usage and log events.
    """
    def __init__(self):
        super().__init__()
        self.event_counter = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    async def on_agent_start(self, ctx: RunContextWrapper, agent: Agent) -> None:
        """Called before an agent is invoked."""
        self.event_counter += 1
        print(f"[HOOK] Agent Start: {agent.name}, Event #{self.event_counter}")

    async def on_tool_end(self, ctx: RunContextWrapper, agent: Agent, tool: Any, result: str) -> None:
        """Called after a local tool is invoked."""
        print(f"[HOOK] Tool End: {tool.name} completed successfully")
        # Example of how you might estimate or track tokens (actual tracking requires specific logic)
        # self.total_output_tokens += estimate_tokens(result)

# --- Example Usage ---
# 1. Define a simple agent and tool (from a public example)
def multiply_by_two(x: int) -> int:
    """Return x times two."""
    return x * 2

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

multiplier_agent = Agent(
    name="MultiplierAgent",
    tools=[multiply_by_two],
    prompt="You multiply the input number by two using the provided tool."
)

# 2. Instantiate your custom hooks
my_hooks = MyRunHooks()

# 3. Run the agent with the custom hooks
async def main():
    print("Starting agent run with custom hooks...")
    result = await Runner.run(
        agent=multiplier_agent,
        input="Multiply 5 by two.",
        hooks=my_hooks # Pass the hooks instance here
    )
    print(f"Run Result: {result.output}")
    print(f"Total Events Tracked: {my_hooks.event_counter}")

# Note: This code typically runs in an async environment (like a Jupyter notebook or async function).
# To run this in a standard Python script, you would use an async runner or run_sync method.