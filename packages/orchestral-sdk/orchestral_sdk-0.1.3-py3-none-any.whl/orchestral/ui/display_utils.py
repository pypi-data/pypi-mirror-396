"""Utility functions for displaying Messages and Contexts with Rich formatting.

Use these functions when you want to pretty-print orchestral objects in your scripts.
The core Message and Context classes remain dependency-free.
"""

from rich.console import Console, Group
from rich.panel import Panel

from orchestral.context.message import Message
from orchestral.context.context import Context
from orchestral.llm.base.response import Response
from orchestral.ui.rich_components.message import MessagePanel
from orchestral.ui.rich_components.agent import AgentPanel


def display_message(message: Message, width: int = 80):
    """Display a single Message with Rich formatting.

    Args:
        message: Message object to display
        width: Panel width (default 80)

    Returns:
        Rich Panel object ready to print

    Example:
        from rich.console import Console
        console = Console()
        console.print(display_message(message))
    """
    if message.role == 'assistant' and message.tool_calls:
        # Use AgentPanel for assistant messages with tools
        tool_uses = []
        for tc in message.tool_calls:
            tool_uses.append({
                'name': tc.tool_name,
                'arguments': tc.arguments,
                'output': None  # No output yet, just the call
            })

        return AgentPanel(
            response_text=message.text,
            tool_uses=tool_uses,
            width=width
        ).display()
    else:
        # Use MessagePanel for simple messages
        return MessagePanel(
            role=message.role,
            content=message.text or "(empty)",
            width=width
        ).display()


def display_context(context: Context, width: int = 80):
    """Display an entire Context with Rich formatting.

    Args:
        context: Context object to display
        width: Panel width (default 80)

    Returns:
        Rich Group object with all message panels

    Example:
        from rich.console import Console
        console = Console()
        console.print(display_context(context))
    """
    panels = []
    i = 0
    messages = context.messages

    while i < len(messages):
        msg = messages[i]

        # Handle Response objects
        if isinstance(msg, Response):
            msg = msg.message

        # Skip empty messages
        if not msg:
            i += 1
            continue

        # Check if this is an assistant message with tool calls
        if msg.role == 'assistant' and msg.tool_calls:
            # Collect the matching tool responses
            tool_call_ids = [tc.id for tc in msg.tool_calls]
            tool_uses = []

            # Build tool_uses with outputs from subsequent tool messages
            for tc in msg.tool_calls:
                tool_use = {
                    'name': tc.tool_name,
                    'arguments': tc.arguments,
                    'output': None  # Default to None (pending)
                }

                # Look ahead for matching tool response
                for j in range(i + 1, len(messages)):
                    next_msg = messages[j]
                    if isinstance(next_msg, Response):
                        next_msg = next_msg.message

                    if next_msg and next_msg.role == 'tool' and next_msg.tool_call_id == tc.id:
                        tool_use['output'] = next_msg.text
                        break

                tool_uses.append(tool_use)

            # Create AgentPanel with text and tools
            panels.append(AgentPanel(
                response_text=msg.text,
                tool_uses=tool_uses,
                width=width
            ).display())

            # Skip the tool response messages we've already processed
            i += 1
            while i < len(messages):
                next_msg = messages[i]
                if isinstance(next_msg, Response):
                    next_msg = next_msg.message
                if next_msg and next_msg.role == 'tool' and next_msg.tool_call_id in tool_call_ids:
                    i += 1
                else:
                    break

        elif msg.role == 'tool':
            # Standalone tool message (shouldn't normally happen, but handle it)
            panels.append(MessagePanel(
                role='tool',
                content=f"Tool Result (ID: {msg.tool_call_id[:8] if msg.tool_call_id else ''}...):\n{msg.text}",
                width=width
            ).display())
            i += 1

        else:
            # Regular message (user, system, assistant without tools)
            panels.append(display_message(msg, width=width))
            i += 1

    # Return group of all panels (no outer panel wrapper)
    return Group(*panels)


def print_message(message: Message, width: int = 80):
    """Convenience function to print a Message directly.

    Args:
        message: Message object to print
        width: Panel width (default 80)
    """
    console = Console()
    console.print(display_message(message, width=width))


def print_context(context: Context, width: int = 80, clear: bool = False):
    """Convenience function to print a Context directly.

    Args:
        context: Context object to print
        width: Panel width (default 80)
        clear: If True, clear the screen before printing (default False)
    """
    console = Console()
    if clear:
        console.clear()
    console.print(display_context(context, width=width))


if __name__ == "__main__":
    # Example usage
    from orchestral.llm.base.tool_call import ToolCall

    console = Console()

    # Example 1: Simple user message
    user_msg = Message(role="user", text="What's the weather like?")
    console.print(display_message(user_msg))
    print()

    # Example 2: Assistant message with tool calls (pending - no output yet)
    tool_call = ToolCall(
        id="call_123",
        tool_name="get_weather",
        arguments={"location": "San Francisco"}
    )
    assistant_msg = Message(
        role="assistant",
        text="Let me check the weather for you.",
        tool_calls=[tool_call]
    )
    console.print(display_message(assistant_msg))
    print()

    # Example 3: Full context with tool responses
    context = Context(system_prompt="You are a helpful weather assistant.")
    context.add_message(user_msg)
    context.add_message(assistant_msg)

    # Add tool response message
    tool_response = Message(
        role="tool",
        tool_call_id="call_123",
        text='{"temperature": 72, "condition": "sunny", "humidity": 45}'
    )
    context.add_message(tool_response)

    # Add final assistant response
    final_msg = Message(
        role="assistant",
        text="The weather in San Francisco is sunny with a temperature of 72°F and 45% humidity."
    )
    context.add_message(final_msg)

    console.print(display_context(context))
