"""
Streaming Display Manager for Main UI

Combines streaming support with caching for optimal performance.
Uses improved components from orchestral.ui with all enhancements:
- Markdown rendering with syntax highlighting
- BaseToolPanel with consistent styling
- Auto-inferred pending states
- Centralized color management

Key Features:
- Cached display for completed messages (instant)
- Rich Live for streaming text (real-time updates)
- Seamless integration with CachedContextDisplay
"""

from rich.console import Console
from rich.live import Live
from typing import Optional

from orchestral.context.context import Context
from orchestral.context.message import Message
from orchestral.ui.format_context import CachedContextDisplay
from orchestral.ui.rich_components.message import MessagePanel
from orchestral.ui.rich_components.agent import AgentPanel


class StreamingDisplay:
    """
    Manages streaming display with caching for completed messages.

    Architecture:
    - Uses CachedContextDisplay for all completed messages (fast!)
    - Uses Rich Live only for actively streaming agent response
    - Updates cache after streaming completes
    """

    def __init__(self, context: Context, width: int = 80, refresh_per_second: int = 10):
        """
        Initialize streaming display.

        Args:
            context (Context): The conversation context
            width (int): Display width
            refresh_per_second (int): Live refresh rate
        """
        self.context = context
        self.width = width
        self.refresh_per_second = refresh_per_second
        self.console = Console()

        # Create cached display for completed messages
        self.cached_display = CachedContextDisplay(context, width)

        # Streaming state
        self.live = None
        self.accumulated_text = ""
        self.base_content_items = []  # Content items before resuming streaming (for after-tool streaming)

    def start_streaming(self, new_user_message: str):
        """
        Start streaming mode - display cached content + new user message.

        Args:
            new_user_message (str): The new user message (not yet in context)
        """
        # Clear screen
        print("\033c", end="")

        # Display all cached content (everything up to last user message) - instant!
        self.cached_display.display(self.console, clear_screen=False)

        # Display the new user message (will be added to context by stream_text_message)
        user_panel = MessagePanel(
            role="user",
            content=new_user_message,
            width=self.width
        )
        self.console.print(user_panel.display())

        # Start Live display for streaming agent response
        # Initialize with empty agent panel
        empty_panel = AgentPanel(response_text="", width=self.width).display()

        self.live = Live(
            empty_panel,
            console=self.console,
            refresh_per_second=self.refresh_per_second,
            auto_refresh=False,  # Manual refresh only - prevents artifacts
            vertical_overflow="visible",  # Allow scrolling
            screen=False,  # Don't take over entire terminal
            transient=False  # False prevents corruption during streaming
        )
        self.live.start()
        self.accumulated_text = ""
        self.base_content_items = []  # Reset for initial streaming

    def update_streaming_text(self, text_chunk: str):
        """
        Update the streaming display with a new text chunk.

        Args:
            text_chunk (str): New chunk of text from the stream
        """
        if not self.live:
            raise RuntimeError("Must call start_streaming() before update_streaming_text()")

        self.accumulated_text += text_chunk

        # Build agent panel - include base content if streaming after tools
        if self.base_content_items:
            # Streaming after tools - show previous content + new streaming text
            content_items = self.base_content_items + [
                {'type': 'text', 'content': self.accumulated_text}
            ]
            streaming_panel = AgentPanel(
                content_items=content_items,
                width=self.width
            ).display()
        else:
            # Initial streaming - just the text
            streaming_panel = AgentPanel(
                response_text=self.accumulated_text,
                width=self.width
            ).display()

        self.live.update(streaming_panel)
        self.live.refresh()  # Manual refresh required when auto_refresh=False

    def finalize_stream(self):
        """
        Finalize the stream - the complete response is now in context.

        If there are tool calls, update Live to show pending tools and KEEP IT RUNNING.
        If no tool calls, stop Live and immediately redraw static (to avoid flicker).
        """
        from orchestral.llm.base.response import Response
        from orchestral.ui.format_context import _pair_tool_calls_with_responses

        if not self.live:
            raise RuntimeError("Must call start_streaming() before finalize_stream()")

        # Check if the LAST AGENT RESPONSE (Response object) has tool calls
        # Note: Context might have tool response messages after the Response, so we
        # need to find the last Response object, not just the last message
        last_response = None
        for msg in reversed(self.context.messages):
            if isinstance(msg, Response):
                last_response = msg
                break

        has_tool_calls = (last_response is not None and
                         last_response.message.tool_calls)

        # ALWAYS stop Live and redraw as static to avoid scrolling artifacts
        # Build content items from scratch by scanning all responses after last user message
        content_items = []

        last_user_idx = -1
        for i in range(len(self.context.messages) - 1, -1, -1):
            msg = self.context.messages[i]
            if isinstance(msg, Message) and msg.role == 'user':
                last_user_idx = i
                break

        # Collect all Response objects after last user message
        for i in range(last_user_idx + 1, len(self.context.messages)):
            item = self.context.messages[i]
            if isinstance(item, Response):
                # Add text if present
                if item.message.text and item.message.text.strip():
                    content_items.append({
                        'type': 'text',
                        'content': item.message.text
                    })

                # Add tools if present
                if item.message.tool_calls:
                    tool_uses = _pair_tool_calls_with_responses(
                        item.message.tool_calls,
                        self.context
                    )
                    for tool_use in tool_uses:
                        content_items.append({
                            'type': 'tool',
                            'name': tool_use['name'],
                            'arguments': tool_use['arguments'],
                            'output': tool_use['output']
                        })

        # If there are tools, update Live to show them (pending state) and KEEP RUNNING
        # If no tools, stop Live
        if has_tool_calls:
            panel_with_pending_tools = AgentPanel(
                content_items=content_items,
                width=self.width
            ).display()
            self.live.update(panel_with_pending_tools)
            self.live.refresh()  # Manual refresh required when auto_refresh=False
            # DON'T stop Live - keep it running so resume_streaming_after_tools can update in place
        else:
            # No tools - final completion, stop Live (content persists)
            self.live.stop()
            self.live = None

        # Store content items for resume_streaming_after_tools
        self.base_content_items = content_items
        self.accumulated_text = ""

        # The content is now visible (static if done, will be Live if resuming)
        # Cache will be updated on next display

    def resume_streaming_after_tools(self):
        """
        Resume streaming after tools execute.

        Updates the existing Live display (still running) with completed tools.
        No screen clearing - smooth transition from pending to completed tools.
        """
        from orchestral.ui.format_context import _pair_tool_calls_with_responses
        from orchestral.llm.base.response import Response

        if not self.live:
            raise RuntimeError("Live should still be running from finalize_stream()")

        # Rebuild base content items with COMPLETED tools
        self.base_content_items = []

        # Find all agent responses after last user message
        last_user_idx = -1
        for i in range(len(self.context.messages) - 1, -1, -1):
            msg = self.context.messages[i]
            if isinstance(msg, Message) and msg.role == 'user':
                last_user_idx = i
                break

        # Collect all Response objects after last user message
        for i in range(last_user_idx + 1, len(self.context.messages)):
            item = self.context.messages[i]
            if isinstance(item, Response):
                # Add text if present
                if item.message.text and item.message.text.strip():
                    self.base_content_items.append({
                        'type': 'text',
                        'content': item.message.text
                    })

                # Add tools if present (now with completed outputs)
                if item.message.tool_calls:
                    tool_uses = _pair_tool_calls_with_responses(
                        item.message.tool_calls,
                        self.context
                    )
                    for tool_use in tool_uses:
                        self.base_content_items.append({
                            'type': 'tool',
                            'name': tool_use['name'],
                            'arguments': tool_use['arguments'],
                            'output': tool_use['output']
                        })

        # Update the EXISTING Live with completed tools
        # No screen clearing - smooth transition from dim to gold tools
        panel_with_completed_tools = AgentPanel(
            content_items=self.base_content_items + [{'type': 'text', 'content': ''}],
            width=self.width
        ).display()
        self.live.update(panel_with_completed_tools)
        self.live.refresh()  # Manual refresh required when auto_refresh=False

        # Reset accumulated text for next streaming phase
        self.accumulated_text = ""

    def update_after_tools(self):
        """
        Update display after tool execution completes.

        NOTE: This method is now a no-op. Pending tools are shown by finalize_stream(),
        and completed tools are shown by resume_streaming_after_tools().
        Kept for backward compatibility.
        """
        # No-op: finalize_stream() already showed pending tools
        pass

    def finalize_and_redraw(self):
        """
        Finalize the agent turn and redraw everything cleanly from cache.

        This eliminates any artifacts from Live updates by:
        1. Stopping Live (content persists)
        2. Forcing cache rebuild to include completed agent response
        3. Clearing screen and redrawing everything statically

        Call this after the complete agent turn (including all tools) finishes.
        """
        # Stop Live if still running
        if self.live:
            self.live.stop()
            self.live = None

        # Force cache invalidation so it rebuilds with the completed agent response
        self.cached_display._invalidate_cache()

        # Clear screen and redraw everything from cache (all static, no artifacts)
        print("\033c", end="")
        self.cached_display.display(self.console, clear_screen=False, include_live=True)

    def stop(self):
        """Stop live display if active."""
        if self.live:
            self.live.stop()
            self.live = None


if __name__ == "__main__":
    print("StreamingDisplay - combines streaming with caching for optimal performance")
    print("Usage:")
    print("  1. streaming_display.start_streaming(user_message)")
    print("  2. for chunk in stream: streaming_display.update_streaming_text(chunk)")
    print("  3. streaming_display.finalize_stream()")
    print("  4. streaming_display.update_after_tools()  # After tool execution")
