from orchestral.tools.hooks.base import ToolHook, ToolHookResult
from orchestral.context.message import Message


class TruncateOutputHook(ToolHook):
    """
    Hook that truncates tool output if it exceeds a maximum length.

    Example:
        agent = Agent(hooks=[TruncateOutputHook(max_length=1000)])
    """

    def __init__(self, max_length: int = 2000):
        """
        Initialize the truncation hook.

        Args:
            max_length: Maximum length of tool output before truncation
        """
        self.max_length = max_length

    def after_call(self, tool_name: str, result: Message) -> ToolHookResult:
        """Truncate the tool result if it's too long."""
        if not result.text or len(result.text) <= self.max_length:
            # Output is within limits - no modification needed
            return ToolHookResult(modified_result=result)

        # Truncate and add indicator
        truncated_text = result.text[:self.max_length] + f"\n\n... (truncated {len(result.text) - self.max_length} characters)"

        # Create modified message with truncated text
        modified_message = Message(
            role=result.role,
            text=truncated_text,
            tool_call_id=result.tool_call_id
        )

        # Copy metadata and mark as truncated
        modified_message.metadata = result.metadata.copy()
        modified_message.metadata['truncated'] = True
        modified_message.metadata['original_length'] = len(result.text)

        return ToolHookResult(modified_result=modified_message)
