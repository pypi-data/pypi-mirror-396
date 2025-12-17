from dataclasses import dataclass
from typing import Optional
from orchestral.context.message import Message


@dataclass
class ToolHookResult:
    """
    Result of a tool hook execution.

    For before_call hooks:
        - approved: Whether the tool execution should proceed
        - error_message: Error message to return if not approved
        - should_interrupt: Whether to interrupt the agent's execution entirely (stops all remaining tool calls)
        - modified_result: Not used for before_call

    For after_call hooks:
        - approved: Not used for after_call
        - error_message: Not used for after_call
        - should_interrupt: Not typically used for after_call
        - modified_result: Modified Message to replace the original (or None to keep original)
    """
    approved: bool = True
    error_message: Optional[str] = None
    should_interrupt: bool = False
    modified_result: Optional[Message] = None

    def apply_to(self, message: Message) -> Message:
        """
        Return the modified result if present, else the input message.

        Used for chaining after_call hooks - each hook sees the result
        from the previous hook in the chain.
        """
        return self.modified_result or message


class ToolHook:
    """
    Base class for tool hooks.

    Hooks are executed before and after tool calls. By default, they act as
    identity operations (approve everything, modify nothing). Subclasses
    override before_call() and/or after_call() as needed.

    Hook execution order:
        - before_call hooks run in sequence; first rejection short-circuits
        - after_call hooks run in sequence; each sees the modified result from previous hooks

    Example:
        class DangerousCommandHook(ToolHook):
            def before_call(self, tool_name: str, arguments: dict) -> ToolHookResult:
                if 'rm -rf' in arguments.get('command', ''):
                    return ToolHookResult(
                        approved=False,
                        error_message="Dangerous command blocked"
                    )
                return ToolHookResult(approved=True)
    """

    def before_call(self, tool_name: str, arguments: dict) -> ToolHookResult:
        """
        Called before a tool executes.

        Args:
            tool_name: Name of the tool being called
            arguments: Dictionary of tool arguments

        Returns:
            ToolHookResult with approved=True/False and optional error_message
        """
        return ToolHookResult(approved=True)

    def after_call(self, tool_name: str, result: Message) -> ToolHookResult:
        """
        Called after a tool executes, possibly to modify the result.

        Args:
            tool_name: Name of the tool that was called
            result: The Message containing the tool result

        Returns:
            ToolHookResult with optional modified_result

        Note:
            Hooks are chained - each hook receives the (possibly modified)
            result from the previous hook in the sequence.
        """
        return ToolHookResult(modified_result=result)