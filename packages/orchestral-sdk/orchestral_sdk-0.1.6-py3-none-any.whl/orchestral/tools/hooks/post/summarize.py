from orchestral.tools.hooks.base import ToolHook, ToolHookResult
from orchestral.context.message import Message
from orchestral.context.summarization.summarizer import Summarizer


class SummarizeHook(ToolHook):
    """
    Hook that summarizes tool output if it exceeds a maximum length.
    Uses the Summarizer to create a concise version of long outputs.

    Example:
        agent = Agent(hooks=[SummarizeHook(max_length=1000)])
    """

    def __init__(self, max_length: int = 2000, llm=None):
        """
        Initialize the summarization hook.

        Args:
            max_length: Maximum length of tool output before summarization
            llm: Optional LLM to use for summarization (defaults to GPT in Summarizer)
        """
        self.max_length = max_length
        self.summarizer = Summarizer(llm=llm)

    def after_call(self, tool_name: str, result: Message) -> ToolHookResult:
        """Summarize the tool result if it's too long."""
        if not result.text or len(result.text) <= self.max_length:
            # Output is within limits - no modification needed
            return ToolHookResult(modified_result=result)

        # Summarize the output
        summary = self.summarizer.summarize(result.text)

        # Add indicator showing original length
        summarized_text = f"{summary}\n\n[Summarized from {len(result.text)} characters]"

        # Create modified message with summarized text
        modified_message = Message(
            role=result.role,
            text=summarized_text,
            tool_call_id=result.tool_call_id
        )

        # Copy metadata and mark as summarized
        modified_message.metadata = result.metadata.copy()
        modified_message.metadata['summarized'] = True
        modified_message.metadata['original_length'] = len(result.text)

        return ToolHookResult(modified_result=modified_message)
