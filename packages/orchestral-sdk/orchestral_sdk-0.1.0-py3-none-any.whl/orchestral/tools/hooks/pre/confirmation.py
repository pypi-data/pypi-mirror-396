"""
ConfirmationHook - Simple approval prompt for specific tools.

This is a lightweight alternative to UserApprovalHook that doesn't require an LLM.
It simply prompts the user before executing specified tools.

Useful for:
- Users without a Groq API key
- Simple workflows where you want manual confirmation for specific tools
- Development/testing environments
"""

from orchestral.tools.hooks.base import ToolHook, ToolHookResult


class ConfirmationHook(ToolHook):
    """
    Hook that prompts for user confirmation before executing specific tools.

    This is a "dumb" version of UserApprovalHook - it doesn't use an LLM to evaluate
    whether approval is needed. Instead, it always prompts for the specified tools.

    NOTE: This hook works with the web app approval modal OR falls back to terminal input.
    Can be used in place of UserApprovalHook if you don't have a Groq API key.

    Example:
        # Require approval for all file/command operations
        agent = Agent(hooks=[
            ConfirmationHook(tools=['runcommand', 'writefile', 'runpython'])
        ])

        # Require approval for everything
        agent = Agent(hooks=[ConfirmationHook()])
    """

    def __init__(self, tools=None):
        """
        Initialize the confirmation hook.

        Args:
            tools: List of tool names to require confirmation for.
                   If None, requires confirmation for all tools.
        """
        self.tools = tools  # None means all tools

    def before_call(self, tool_name: str, arguments: dict) -> ToolHookResult:
        """
        Prompt for confirmation before executing tool.

        Args:
            tool_name: Name of the tool being called
            arguments: Tool arguments

        Returns:
            ToolHookResult with approved=True/False and should_interrupt if denied
        """
        # Check if this tool requires confirmation
        if self.tools is not None and tool_name not in self.tools:
            return ToolHookResult(approved=True)

        # Build description from arguments
        description = self._build_description(tool_name, arguments)

        # Try to get approval callback from app state
        try:
            from app.server import state
            if hasattr(state, 'approval_callback') and state.approval_callback:
                # Use web app callback (blocks until user responds)
                approved = state.approval_callback(tool_name, arguments, description)
            else:
                # Fallback to terminal input
                print(f"\n[ConfirmationHook] Confirmation required: {description}")
                user_input = input("Approve? (y/n): ")
                approved = user_input.lower() in ['y', 'yes']
        except (ImportError, AttributeError):
            # No app state available (running outside app context)
            print(f"\n[ConfirmationHook] Confirmation required: {description}")
            user_input = input("Approve? (y/n): ")
            approved = user_input.lower() in ['y', 'yes']

        if not approved:
            return ToolHookResult(
                approved=False,
                error_message=f"User denied: {description}",
                should_interrupt=True  # Stop the agent from trying alternatives
            )

        return ToolHookResult(approved=True)

    def _build_description(self, tool_name: str, arguments: dict) -> str:
        """
        Build a human-readable description of the tool call.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            Description string
        """
        # Format based on common tool types
        if tool_name in ['runcommand', 'dummyruncommand']:
            command = arguments.get('command', '')
            return f"Run command: {command}"
        elif tool_name == 'runpython':
            code = arguments.get('code', '')
            preview = code[:100] + '...' if len(code) > 100 else code
            return f"Execute Python code: {preview}"
        elif tool_name == 'writefile':
            path = arguments.get('file_path', '')
            return f"Write to file: {path}"
        elif tool_name == 'readfile':
            path = arguments.get('file_path', '')
            return f"Read file: {path}"
        elif tool_name == 'websearch':
            query = arguments.get('query', '')
            return f"Search the web: {query}"
        else:
            # Generic format for other tools
            args_preview = ', '.join(f"{k}={repr(v)[:30]}" for k, v in list(arguments.items())[:3])
            return f"Call {tool_name}({args_preview})"


# Example usage:
if __name__ == "__main__":
    # Test the hook with terminal fallback
    hook = ConfirmationHook(tools=['runcommand', 'writefile'])

    # Test tool that requires confirmation
    result = hook.before_call(
        tool_name='runcommand',
        arguments={'command': 'ls -la'}
    )
    print(f"runcommand: approved={result.approved}")

    # Test tool that doesn't require confirmation
    result = hook.before_call(
        tool_name='readfile',
        arguments={'file_path': 'test.txt'}
    )
    print(f"readfile: approved={result.approved} (should auto-approve)")
