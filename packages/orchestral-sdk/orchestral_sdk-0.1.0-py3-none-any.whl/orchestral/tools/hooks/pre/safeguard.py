import os
from orchestral.llm import Groq
from orchestral.agent.agent import Agent
from orchestral.tools.hooks.base import ToolHook, ToolHookResult
from orchestral.tools.hooks.pre.security_policy import policy_text


class SafeguardHook(ToolHook):
    """
    Hook that blocks potentially dangerous shell commands using an LLM safeguard model.

    Uses OpenAI's GPT-OSS-Safeguard model via Groq to analyze commands before execution.
    Only applies to the 'runcommand' tool.

    NOTE: Using this hook requires a Groq API key with access to the GPT-OSS-Safeguard model.
    Although, you can optionally provide your own LLM that implements similar functionality.
    It requires an internet connection and may incur additional costs. 
    It is designed to minimize latency while providing robust safety checks.

    Example:
        agent = Agent(hooks=[SafeguardHook()])
    """

    def __init__(self, llm=None):
        """Initialize the safeguard hook with the security policy."""
        # Create safeguard agent with no hooks (avoid recursion)
        llm = Groq(model="openai/gpt-oss-safeguard-20b") if llm is None else llm
        self.agent = Agent(llm=llm, system_prompt=policy_text, tool_hooks=[])

        # Assert no hooks to prevent infinite recursion
        assert len(self.agent.tool_hooks) == 0, "SafeguardHook agent must not have hooks to prevent recursion"

    def before_call(self, tool_name: str, arguments: dict) -> ToolHookResult:
        """
        Analyze command for safety before execution.

        Args:
            tool_name: Name of the tool being called
            arguments: Tool arguments

        Returns:
            ToolHookResult with approved=True/False and error_message if blocked
        """
        # Determine what to check based on tool name
        if tool_name == 'runcommand':
            command = arguments.get('command', '')
        elif tool_name == 'dummyruncommand':
            command = arguments.get('command', '')
        elif tool_name == 'runpython':
            command = arguments.get('code', '')
        else:
            # Not a tool we safeguard - approve
            return ToolHookResult(approved=True)

        # Handle empty commands
        if not command or not command.strip():
            return ToolHookResult(
                approved=True,
            )

        # Prepare the agent by clearing everything but the system prompt
        self.agent.context.clear() # Preserves system prompt by default

        # Ask safeguard model to evaluate
        response = self.agent.run(command, temperature=0.1)

        assert response is not None, "SafeguardHook received no response from safeguard agent"
        assert isinstance(response.text, str), "SafeguardHook received invalid response type"
        response_text = response.text.strip() if hasattr(response, 'text') else str(response).strip()

        # Parse response
        if response_text.upper().startswith('SAFE'):
            return ToolHookResult(approved=True)
        elif response_text.upper().startswith('UNSAFE'):
            # Extract reason after the colon
            reason = response_text[7:].strip()  # Skip "UNSAFE:"
            return ToolHookResult(
                approved=False,
                error_message=f"Command blocked by SafeguardHook: {reason}"
            )
        else:
            # Unexpected response - treat as unsafe to be cautious
            return ToolHookResult(
                approved=False,
                error_message=f"Safeguard Hook Error (unexpected response): {response_text}"
            )


# Example usage:
if __name__ == "__main__":
    safeguard = SafeguardHook()
    result = safeguard.before_call(
        tool_name='runcommand',
        arguments={'command': 'sudo rm -rf /home/user/.ssh/*'}
    )
    if result.approved:
        print("Command approved.")
    else:
        print(f"Command blocked: {result.error_message}")