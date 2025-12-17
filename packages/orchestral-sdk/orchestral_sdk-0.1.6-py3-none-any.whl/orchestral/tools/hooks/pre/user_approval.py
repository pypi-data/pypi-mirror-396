"""
UserApprovalHook - Requires user approval for impactful development actions.

This hook uses an LLM to evaluate commands and determine if they require user approval.
It's designed for a supervisor-developer relationship where the agent checks in before
taking impactful actions like deleting files, modifying code, or running non-routine commands.

This hook ONLY works when integrated with the web app that provides the approval_callback.
In other contexts (demos, scripts), it falls back to terminal input().
"""

from orchestral.llm import Groq
from orchestral.agent.agent import Agent
from orchestral.tools.hooks.base import ToolHook, ToolHookResult
from orchestral.tools.hooks.pre.security_policy import policy_text_strict


class UserApprovalHook(ToolHook):
    """
    Hook that requires user approval for impactful development actions.

    Uses OpenAI's GPT-OSS-Safeguard model via Groq to analyze commands and determine
    if they require approval. Responds with:
    - SAFE: Auto-approve (read-only, tests, informational)
    - APPROVE: Requires user approval (file deletion, package install, git commits)
    - UNSAFE: Block entirely (dangerous commands)

    NOTE: This hook is designed for use with the web app that provides an approval_callback.
    When running outside the app context, it falls back to terminal input() for approval.

    Example:
        # In web app context (with callback)
        agent = Agent(hooks=[UserApprovalHook()])

        # In terminal/demo context (with fallback)
        agent = Agent(hooks=[UserApprovalHook()])  # Will use input() for approval
    """

    def __init__(self, llm=None):
        """Initialize the user approval hook with the strict security policy."""
        # Create evaluation agent with no hooks (avoid recursion)
        llm = Groq(model="openai/gpt-oss-safeguard-20b") if llm is None else llm
        self.agent = Agent(llm=llm, system_prompt=policy_text_strict, tool_hooks=[])

        # Assert no hooks to prevent infinite recursion
        assert len(self.agent.tool_hooks) == 0, "UserApprovalHook agent must not have hooks to prevent recursion"

    def before_call(self, tool_name: str, arguments: dict) -> ToolHookResult:
        """
        Analyze command for approval requirements before execution.

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
            # Not a tool we evaluate - approve
            return ToolHookResult(approved=True)

        # Handle empty commands
        if not command or not command.strip():
            return ToolHookResult(approved=True)

        # Prepare the agent by clearing everything but the system prompt
        self.agent.context.clear()  # Preserves system prompt by default

        # Ask evaluation model to analyze
        response = self.agent.run(command)

        assert response is not None, "UserApprovalHook received no response from evaluation agent"
        assert isinstance(response.text, str), "UserApprovalHook received invalid response type"
        response_text = response.text.strip()
        print(f"[UserApprovalHook] Evaluation response: {response_text}")

        # Parse response
        if response_text.upper().startswith('SAFE'):
            # Auto-approve safe commands
            return ToolHookResult(approved=True)

        elif response_text.upper().startswith('APPROVE:'):
            # Requires user approval
            description = response_text[8:].strip(' .')  # Skip "APPROVE:"

            # Try to get approval callback from app state
            try:
                from app.server import state
                from app.approval_bridge import ApprovalDisconnectException

                if hasattr(state, 'approval_callback') and state.approval_callback:
                    # Use web app callback (blocks until user responds)
                    try:
                        approved = state.approval_callback(tool_name, arguments, description)
                    except ApprovalDisconnectException:
                        # WebSocket disconnected during approval
                        return ToolHookResult(
                            approved=False,
                            error_message=f"Connection lost during approval request. Please try again.",
                            should_interrupt=True
                        )
                else:
                    # Fallback to terminal input
                    print(f"\n[UserApprovalHook] Approval required: {description}")
                    user_input = input("Approve? (y/n): ")
                    approved = user_input.lower() in ['y', 'yes']
            except (ImportError, AttributeError):
                # No app state available (running outside app context)
                print(f"\n[UserApprovalHook] Approval required: {description}")
                user_input = input("Approve? (y/n): ")
                approved = user_input.lower() in ['y', 'yes']

            if not approved:
                return ToolHookResult(
                    approved=False,
                    error_message=f"User denied: {description}",
                    should_interrupt=True  # Stop the agent from trying alternatives
                )

            return ToolHookResult(approved=True)

        elif response_text.upper().startswith('UNSAFE:'):
            # Block dangerous commands
            reason = response_text[7:].strip()  # Skip "UNSAFE:"
            return ToolHookResult(
                approved=False,
                error_message=f"Command blocked by UserApprovalHook: {reason}"
            )

        else:
            # Unexpected response format - fail safe by blocking
            raise ValueError(
                f"UserApprovalHook received unexpected response format: '{response_text[:100]}'. "
                f"Expected response to start with 'SAFE', 'APPROVE:', or 'UNSAFE:'"
            )


# Example usage:
if __name__ == "__main__":
    # Test the hook with terminal fallback
    hook = UserApprovalHook()

    # Test auto-approve (SAFE)
    result = hook.before_call(
        tool_name='runcommand',
        arguments={'command': 'ls -la'}
    )
    print(f"ls -la: approved={result.approved}")

    # Test approval required (APPROVE)
    result = hook.before_call(
        tool_name='runcommand',
        arguments={'command': 'rm test.txt'}
    )
    print(f"rm test.txt: approved={result.approved}, message={result.error_message}")

    # Test block (UNSAFE)
    result = hook.before_call(
        tool_name='runcommand',
        arguments={'command': 'rm -rf /'}
    )
    print(f"rm -rf /: approved={result.approved}, message={result.error_message}")
