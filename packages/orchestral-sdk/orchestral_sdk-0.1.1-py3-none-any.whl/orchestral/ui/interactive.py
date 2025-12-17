"""
Interactive Session Manager

High-level interface for running interactive chat sessions with agents.
Handles display, streaming, caching, commands, and tool execution loops.

Usage:
    from orchestral import Agent
    from orchestral.ui import run_interactive_session

    agent = Agent(tools=[...])
    run_interactive_session(agent, streaming=True)
"""

from time import time
from rich.console import Console

from orchestral.context.context import Context
from orchestral.llm.base.response import Response
from orchestral.ui.streaming_display import StreamingDisplay
from orchestral.ui.format_context import CachedContextDisplay, display_context
from orchestral.ui.logo.logo1 import logo1
from orchestral.ui.commands import handle_command


def run_interactive_session(
    agent,
    streaming: bool = True,
    use_cache: bool = True,
    width: int = 80,
    show_timing: bool = False,
    refresh_per_second: int = 10
):
    """
    Run an interactive chat session with an agent.

    Args:
        agent: The agent to interact with
        streaming (bool): Enable streaming mode (character-by-character display)
        use_cache (bool): Enable caching for faster display
        width (int): Display width in characters
        show_timing (bool): Show timing information
        refresh_per_second (int): Refresh rate for streaming (Hz)

    Features:
        - Streaming text display (if streaming=True)
        - Cached rendering for completed messages (if use_cache=True)
        - Multi-turn tool execution loops
        - Command handling (/help, /clear, etc.)
        - Error handling and graceful shutdown
    """
    console = Console()

    # Show logo and welcome message
    print("\033c", end="")
    console.print(logo1)

    mode_desc = []
    if streaming:
        mode_desc.append("Streaming")
    if use_cache:
        mode_desc.append("Cached")

    mode_str = " + ".join(mode_desc) if mode_desc else "Standard"
    console.print(f'\n  Send a message... ({mode_str} Mode)')

    # Initialize display managers
    streaming_display = None
    cached_display = None

    if streaming:
        streaming_display = StreamingDisplay(
            context=agent.context,
            width=width,
            refresh_per_second=refresh_per_second
        )
    elif use_cache:
        cached_display = CachedContextDisplay(agent.context, width=width)

    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input('\n> ')

            # Skip empty input
            if not user_input or not user_input.strip():
                continue

            # Handle special commands
            if user_input[0] == '/':
                if streaming_display:
                    streaming_display.stop()
                handle_command(user_input[1:], agent, console, streaming_display)
                continue

            # Process user message
            start_time = time()

            if streaming:
                _run_streaming_turn(
                    agent,
                    user_input,
                    streaming_display,
                    show_timing,
                    start_time
                )
            else:
                _run_standard_turn(
                    agent,
                    user_input,
                    cached_display,
                    width,
                    show_timing,
                    start_time
                )

        except KeyboardInterrupt:
            if streaming_display:
                streaming_display.stop()
            print("\n\nInterrupted by user")
            break

        except Exception as e:
            if streaming_display:
                streaming_display.stop()
            print(f"\n\nError: {e}")
            import traceback
            traceback.print_exc()
            break


def _run_streaming_turn(agent, user_input, streaming_display, show_timing, start_time):
    """Run a single turn in streaming mode."""
    # Update display context if needed
    if streaming_display.context is not agent.context:
        streaming_display.context = agent.context
        streaming_display.cached_display.context = agent.context

    # Start streaming display
    streaming_display.start_streaming(user_input)

    # Stream the agent response
    streaming_generator = agent.stream_text_message(user_input)

    for text_chunk in streaming_generator:
        streaming_display.update_streaming_text(text_chunk)

    streaming_display.finalize_stream()

    streaming_time = time() - start_time

    # Handle multi-turn tool execution loop
    _handle_tool_execution_loop(agent, streaming_display)

    # Finalize and clean redraw to eliminate any artifacts from Live updates
    streaming_display.finalize_and_redraw()

    total_time = time() - start_time

    if show_timing:
        print(f"\n[Streaming: {streaming_time:.4f}s | Total: {total_time:.4f}s]")


def _run_standard_turn(agent, user_input, cached_display, width, show_timing, start_time):
    """Run a single turn in standard (non-streaming) mode."""
    # Run the agent
    agent.run(user_input)

    # Display the result
    if cached_display:
        # Update context reference if needed
        if cached_display.context is not agent.context:
            cached_display.context = agent.context

        print("\033c", end="")
        cached_display.display(clear_screen=False)
    else:
        display_context(agent.context, width=width)

    if show_timing:
        elapsed = time() - start_time
        print(f"\n[Display time: {elapsed:.4f}s]")


def _handle_tool_execution_loop(agent, streaming_display, max_iterations=10):
    """
    Handle multi-turn tool execution loop.

    Agents may chain tool calls - execute tools, get response, execute more tools, etc.
    This loop handles that flow until the agent stops making tool calls.
    """
    iteration = 0

    while iteration < max_iterations:
        last_response = agent.context.messages[-1]

        # Check if the last message has tool calls
        if isinstance(last_response, Response) and last_response.message.tool_calls:
            # Show tools in pending state (output=None) BEFORE executing
            streaming_display.update_after_tools()

            # Execute tool calls
            agent._handle_tool_calls()

            # Show updated tools with completed results and prepare for streaming
            streaming_display.resume_streaming_after_tools()

            # Stream the next LLM response after tools
            response_generator = agent._stream_response()
            for text_chunk in response_generator:
                streaming_display.update_streaming_text(text_chunk)

            # Finalize stream
            streaming_display.finalize_stream()

            iteration += 1
        else:
            # No more tool calls, we're done
            break

    if iteration >= max_iterations:
        # Fix any unmatched tool calls from partial tool execution
        agent.context.fix_orphaned_results()
        agent.context.fix_missing_ids()
        if streaming_display:
            streaming_display.stop()
        print(f"\n\nWarning: Reached maximum tool call iterations ({max_iterations})")


if __name__ == "__main__":
    print("Interactive Session Manager")
    print("\nUsage:")
    print("  from orchestral import Agent")
    print("  from orchestral.ui import run_interactive_session")
    print("")
    print("  agent = Agent(tools=[...])")
    print("  run_interactive_session(agent)")
