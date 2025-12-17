"""
Dummy RunCommand tool for testing safeguard hooks safely.

This tool simulates command execution using an LLM instead of actually running commands.
Useful for testing hooks that might block dangerous commands without risking the actual system.
"""

from orchestral.tools.base.tool import BaseTool
from orchestral.tools.base.field_utils import RuntimeField


class DummyRunCommandTool(BaseTool):
    """
    A dummy version of RunCommandTool that simulates command execution using an LLM.

    This tool is useful for safely testing safeguard hooks without actually executing
    potentially dangerous commands on the system.

    Example:
        # Use dummy tool for safe testing
        agent = Agent(
            tools=[DummyRunCommandTool()],
            hooks=[SafeguardHook()]
        )
    """

    command: str = RuntimeField(description="The shell command to simulate")
    timeout: int = RuntimeField(default=30, description="Ignored in dummy mode")

    def __init__(self, **data):
        """Initialize the dummy tool with a simulated terminal agent."""
        super().__init__(**data)

        # Lazy import to avoid circular dependencies
        from orchestral.llm import GPT
        from orchestral.agent import Agent

        # Create an agent that simulates a terminal
        system_prompt = """You are simulating a Unix/Linux terminal session.
When given a command, respond with what a real terminal would output for that command.

Guidelines:
- For safe commands (ls, pwd, echo, etc): Provide realistic example output
- For dangerous commands (rm -rf /, mkfs, etc): Show what WOULD happen if executed (e.g., "Permission denied" or describe the damage)
- For file operations: Simulate file system state realistically
- For package managers: Simulate installation/removal output
- Keep outputs concise and realistic
- If a command would fail (permissions, doesn't exist), show the error

Current directory: /Users/testuser/project
User: testuser (non-root)

Format your response as plain terminal output without explanation."""

        llm = GPT(model='gpt-4o-mini')
        self.terminal_agent = Agent(llm=llm, system_prompt=system_prompt, tool_hooks=[])

    def _run(self) -> str:
        """Simulate running the command using the LLM."""
        # Clear context to keep simulation stateless
        self.terminal_agent.context.clear()

        # Get simulated output
        response = self.terminal_agent.run(f"$ {self.command}")

        # Extract text from response
        if hasattr(response, 'text') and isinstance(response.text, str):
            output = response.text.strip()
        else:
            raise ValueError("Unexpected response format from terminal agent")

        # Format like real terminal output
        result = f"[SIMULATED] Command: {self.command}\n{output}"

        return result


if __name__ == "__main__":
    # Test the dummy tool
    print("Testing DummyRunCommandTool...\n")

    # Test safe command
    tool = DummyRunCommandTool(command="ls -la")
    print(tool.execute())
    print("\n" + "="*80 + "\n")

    # Test dangerous command (should still execute in simulation)
    tool = DummyRunCommandTool(command="rm -rf /")
    print(tool.execute())
    print("\n" + "="*80 + "\n")

    # Test info command
    tool = DummyRunCommandTool(command="pwd")
    print(tool.execute())
