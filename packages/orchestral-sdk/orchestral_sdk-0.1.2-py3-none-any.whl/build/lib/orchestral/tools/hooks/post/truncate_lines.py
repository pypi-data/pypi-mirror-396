from orchestral.tools.hooks.base import ToolHook, ToolHookResult
from orchestral.context.message import Message


class TruncateLinesHook(ToolHook):
    """
    Hook that truncates tool output if it exceeds a maximum length.

    Example:
        agent = Agent(hooks=[TruncateLinesHook(max_lines=100)])
    """

    def __init__(self, max_lines: int = 100, max_chars: int = 5000):
        """
        Initialize the truncation hook.

        Args:
            max_lines: Maximum number of lines of tool output before truncation
        """
        self.max_lines = max_lines
        self.max_chars = max_chars

    def after_call(self, tool_name: str, result: Message) -> ToolHookResult:
        """Truncate the tool result if it's too long."""
        if not result.text or result.text.count('\n') <= self.max_lines:
            # Output is within limits - no modification needed
            return ToolHookResult(modified_result=result)

        print(f'[TruncateHook]: Truncating output of tool "{tool_name}" ')
        print(f'[TruncateHook]: Original length: {len(result.text)} characters')
        print(f'[TruncateHook]: Original lines: {result.text.count("\n")} lines')

        # Truncate
        lines = result.text.split('\n')
        truncated_text = '\n'.join(lines[:self.max_lines])

        print(f'[TruncateHook]: lines: {len(lines)} -> {self.max_lines}')

        # Also enforce character limit to avoid excessive length
        if len(truncated_text) > self.max_chars:
            print(f'[TruncateHook]: characters: {len(truncated_text)} -> {self.max_chars}')
            truncated_text = truncated_text[:self.max_chars]

        # Add indicator
        truncated_text += f"\n...\n\n [TruncateHook]: (truncated {len(lines) - self.max_lines} lines)"
        print(f'[TruncateHook]: {len(lines)} - {self.max_lines} = {len(lines) - self.max_lines} lines truncated.')

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
