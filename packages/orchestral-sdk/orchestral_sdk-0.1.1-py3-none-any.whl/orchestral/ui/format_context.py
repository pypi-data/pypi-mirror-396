from rich.console import Console, Group
from typing import List, Dict, Any

from orchestral.context.context import Context
from orchestral.context.message import Message
from orchestral.llm.base.response import Response
from orchestral.ui.rich_components.message import MessagePanel
from orchestral.ui.rich_components.agent import AgentPanel


def format_context(context: Context, width: int = 80) -> Group:
    """
    Format a context object for display using Rich panels.

    Args:
        context (Context): The context containing messages and responses
        width (int): Panel width for display

    Returns:
        Group: Rich Group containing all formatted panels
    """
    panels = []
    agent_content_buffer = []  # Buffer to collect agent responses between user messages

    def _flush_agent_buffer():
        """Create an AgentPanel from buffered agent content and add to panels."""
        if agent_content_buffer:
            content_items = []

            # Process each agent response in the buffer
            for response in agent_content_buffer:
                # Add response text if present
                if response.message.text and response.message.text.strip():
                    content_items.append({
                        'type': 'text',
                        'content': response.message.text
                    })

                # Add tool calls with their responses
                if response.message.tool_calls:
                    tool_uses = _pair_tool_calls_with_responses(
                        response.message.tool_calls,
                        context
                    )
                    for tool_use in tool_uses:
                        content_items.append({
                            'type': 'tool',
                            'name': tool_use['name'],
                            'arguments': tool_use['arguments'],
                            'output': tool_use['output']
                        })

            # Create agent panel with ordered content
            if content_items:
                agent_panel = AgentPanel(
                    content_items=content_items,
                    width=width
                )
                panels.append(agent_panel.display())

            agent_content_buffer.clear()

    # Process messages in order
    for item in context.messages:
        if isinstance(item, Message):
            # Handle regular messages (user, system, tool response)
            if item.role in ['user', 'system']:
                # Flush any buffered agent content before user/system message
                _flush_agent_buffer()

                # Simple message display
                panel = MessagePanel(
                    role=item.role,
                    content=item.text or "(no content)",
                    width=width
                )
                panels.append(panel.display())

            elif item.role == 'tool':
                # Tool response message - will be paired with tool calls later
                continue

        elif isinstance(item, Response):
            # Buffer agent responses to group them
            agent_content_buffer.append(item)

    # Flush any remaining agent content at the end
    _flush_agent_buffer()

    return Group(*panels)


def _pair_tool_calls_with_responses(tool_calls: List, context: Context) -> List[Dict[str, Any]]:
    """
    Pair tool calls with their corresponding tool response messages.

    If a tool call doesn't have a matching response yet (agent still working),
    shows "working..." as a placeholder.

    Args:
        tool_calls: List of tool call objects
        context: Full context for finding tool responses

    Returns:
        List of tool_use dictionaries with name, arguments, and output
    """
    tool_uses = []

    # Create a mapping of tool_call_id to tool response (Message object)
    tool_responses = {}
    for msg in context.messages:
        if isinstance(msg, Message) and msg.role == 'tool' and msg.tool_call_id:
            tool_responses[msg.tool_call_id] = msg

    # Pair each tool call with its response (or None if incomplete)
    for tool_call in tool_calls:
        # Check if this tool call has a response yet
        if tool_call.id in tool_responses:
            response_msg = tool_responses[tool_call.id]
            output = response_msg.text or "(no output)"
            is_failed = response_msg.failed
        else:
            # No response yet - agent is still working on this tool
            output = None  # None output will auto-infer pending state
            is_failed = False

        tool_use = {
            'id': tool_call.id,  # Include ID for streaming lookup
            'name': tool_call.tool_name,
            'arguments': tool_call.arguments,
            'output': output,
            'is_failed': is_failed,
        }
        tool_uses.append(tool_use)

    return tool_uses


def display_context(context: Context, width: int = 80, console: Console | None = None, clear_screen: bool = True) -> None:
    """
    Display a context object to the console.

    Args:
        context (Context): The context to display
        width (int): Panel width for display
        console (Console): Rich console instance (creates new one if None)
        clear_screen (bool): Whether to clear the screen before displaying
    """
    if console is None:
        console = Console()

    if clear_screen:
        print("\033c", end="")  # Clear screen

    formatted_group = format_context(context, width)
    console.print(formatted_group)


class CachedContextDisplay:
    """
    Cached context display for improved performance.

    Caches the rendered output of messages up to the last user message,
    and only re-renders the "live" portion (pending agent responses).

    Usage:
        cached_display = CachedContextDisplay(context, width=80)
        cached_display.display(console)  # Fast on subsequent calls!
    """

    def __init__(self, context: Context, width: int = 80):
        """
        Initialize cached display for a context.

        Args:
            context (Context): The context to display
            width (int): Panel width for display
        """
        self.context = context
        self.width = width
        self._cached_output = ""  # Rendered ANSI string (fast to print!)
        self._last_cached_index = -1  # Index of last cached message
        self._cached_width = width

    def display(self, console: Console | None = None, clear_screen: bool = True, include_live: bool = True) -> None:
        """
        Display the context with caching for improved performance.

        Args:
            console (Console): Rich console instance (creates new one if None)
            clear_screen (bool): Whether to clear the screen before displaying
            include_live (bool): Whether to render live content (everything after last user message)
        """
        if console is None:
            console = Console()

        if clear_screen:
            print("\033c", end="")  # Clear screen

        # Find index of most recent user message
        last_user_idx = self._find_last_user_message_index()

        # If width changed, invalidate cache
        if self._cached_width != self.width:
            self._invalidate_cache()
            self._cached_width = self.width

        # Rebuild cache if needed (up to last user message)
        if self._last_cached_index < last_user_idx:
            self._rebuild_cache(last_user_idx, console)

        # Print cached output (instant!) - write ANSI directly without re-processing
        if self._cached_output:
            console.file.write(self._cached_output)
            console.file.flush()

        # Render live content (everything after last user message) if requested
        if include_live:
            self._render_live_content(last_user_idx + 1, console)

    def _find_last_user_message_index(self) -> int:
        """
        Find index of most recent user message.

        Returns:
            int: Index of last user message, or -1 if none found
        """
        for i in range(len(self.context.messages) - 1, -1, -1):
            msg = self.context.messages[i]
            if isinstance(msg, Message) and msg.role == 'user':
                return i
        return -1  # No user message yet

    def _rebuild_cache(self, up_to_index: int, console: Console) -> None:
        """
        Rebuild cache from scratch up to specified index.

        Args:
            up_to_index (int): Index to cache up to (inclusive)
            console (Console): Console for rendering
        """
        if up_to_index < 0:
            self._cached_output = ""
            self._last_cached_index = -1
            return

        # Render messages directly to avoid creating temporary Context objects
        panels = []
        agent_content_buffer = []

        def _flush_agent_buffer():
            if agent_content_buffer:
                content_items = []
                for response in agent_content_buffer:
                    if response.message.text and response.message.text.strip():
                        content_items.append({
                            'type': 'text',
                            'content': response.message.text
                        })
                    if response.message.tool_calls:
                        tool_uses = _pair_tool_calls_with_responses(
                            response.message.tool_calls,
                            self.context
                        )
                        for tool_use in tool_uses:
                            content_items.append({
                                'type': 'tool',
                                'name': tool_use['name'],
                                'arguments': tool_use['arguments'],
                                'output': tool_use['output']
                            })
                if content_items:
                    agent_panel = AgentPanel(content_items=content_items, width=self.width)
                    panels.append(agent_panel.display())
                agent_content_buffer.clear()

        # Process only the messages we want to cache
        for i in range(up_to_index + 1):
            item = self.context.messages[i]
            if isinstance(item, Message):
                if item.role in ['user', 'system']:
                    _flush_agent_buffer()
                    panel = MessagePanel(role=item.role, content=item.text or "(no content)", width=self.width)
                    panels.append(panel.display())
                elif item.role == 'tool':
                    continue
            elif isinstance(item, Response):
                agent_content_buffer.append(item)

        _flush_agent_buffer()

        # Render and capture output
        with console.capture() as capture:
            for panel in panels:
                console.print(panel)

        self._cached_output = capture.get()
        self._last_cached_index = up_to_index

    def _render_live_content(self, start_index: int, console: Console) -> None:
        """
        Render live content (everything after the cache).

        Args:
            start_index (int): Index to start rendering from
            console (Console): Console for rendering
        """
        if start_index >= len(self.context.messages):
            return  # Nothing to render

        # Render messages directly without temporary Context
        panels = []
        agent_content_buffer = []

        def _flush_agent_buffer():
            if agent_content_buffer:
                content_items = []
                for response in agent_content_buffer:
                    if response.message.text and response.message.text.strip():
                        content_items.append({
                            'type': 'text',
                            'content': response.message.text
                        })
                    if response.message.tool_calls:
                        tool_uses = _pair_tool_calls_with_responses(
                            response.message.tool_calls,
                            self.context
                        )
                        for tool_use in tool_uses:
                            content_items.append({
                                'type': 'tool',
                                'name': tool_use['name'],
                                'arguments': tool_use['arguments'],
                                'output': tool_use['output']
                            })
                if content_items:
                    agent_panel = AgentPanel(content_items=content_items, width=self.width)
                    panels.append(agent_panel.display())
                agent_content_buffer.clear()

        # Process live messages
        for i in range(start_index, len(self.context.messages)):
            item = self.context.messages[i]
            if isinstance(item, Message):
                if item.role in ['user', 'system']:
                    _flush_agent_buffer()
                    panel = MessagePanel(role=item.role, content=item.text or "(no content)", width=self.width)
                    panels.append(panel.display())
                elif item.role == 'tool':
                    continue
            elif isinstance(item, Response):
                agent_content_buffer.append(item)

        _flush_agent_buffer()

        # Print live panels
        for panel in panels:
            console.print(panel)

    def _invalidate_cache(self) -> None:
        """Clear cache when width changes or context is reset."""
        self._cached_output = ""
        self._last_cached_index = -1


if __name__ == "__main__":
    # Test with example_context.json
    console = Console()

    try:
        # Create a Context object from the JSON data
        context = Context(filepath="/Users/adroman/orchestral3/orchestral_core/example_context.json")

        print("Testing standard display_context:")
        print("=" * 80)
        display_context(context, console=console)

        print("\n\n")
        print("Testing CachedContextDisplay:")
        print("=" * 80)

        # Create cached display
        cached = CachedContextDisplay(context, width=80)
        cached.display(console=console, clear_screen=False)

        print("\n\nSecond call (should use cache):")
        cached.display(console=console, clear_screen=False)

    except Exception as e:
        print(f"Error testing format_context: {e}")
        print("Make sure the example_context.json file exists and Context.load_json() works properly.")