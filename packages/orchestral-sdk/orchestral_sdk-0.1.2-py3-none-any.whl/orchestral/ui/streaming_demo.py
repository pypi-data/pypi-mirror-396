"""
Streaming UI Demo with Caching

Demonstrates real-time streaming combined with caching for optimal performance.

Key Features:
- Text streams character-by-character with Live display
- Caching for completed messages (instant display)
- Multi-turn tool execution loops (agents can chain tool calls)
- All UI improvements: markdown rendering, syntax highlighting, auto-pending states
- Multiple simultaneous tool calls supported

Performance:
- Cached messages display instantly (no re-rendering)
- Only streaming portion uses Live (minimal overhead)
- Scales well with long conversations

Important: The multi-turn loop is critical for chained tool calls.
Without it, subsequent tool calls won't execute.
"""

from time import time

from orchestral.ui.streaming_display import StreamingDisplay
from orchestral.ui.logo.logo1 import logo1
from orchestral.ui.commands import handle_command
from rich.console import Console

# Define an example agent with tools
from orchestral import Agent
from orchestral.tools import RunCommandTool, RunPythonTool, WriteFileTool, WebSearchTool

console = Console()

base_directory = '/Users/adroman/orchestral3/orchestral_core/demos/demo_files'
tools = [
    RunCommandTool(base_directory=base_directory),
    WriteFileTool(base_directory=base_directory),
    RunPythonTool(base_directory=base_directory),
    WebSearchTool(),
]

# Create agent WITHOUT display_hook (we manage display manually for streaming)
agent = Agent(tools=tools)

# Create streaming display manager (includes caching)
streaming_display = None


if __name__ == "__main__":
    print("\033c", end="")
    console.print(logo1)
    console.print('\n  Send a message... (Streaming Mode with Caching)')
    console.print('  [Performance optimized - cached + streaming]\n')

    while True:
        # Get user input
        user_input = input('\n> ')

        # Handle special commands
        if user_input and user_input[0] == '/':
            # For commands, stop streaming and use regular display
            if streaming_display:
                streaming_display.stop()
            handle_command(user_input[1:], agent, console)
            continue

        # Normal input - use streaming with caching
        try:
            start_time = time()

            # Initialize or update streaming display
            if streaming_display is None or streaming_display.context is not agent.context:
                streaming_display = StreamingDisplay(
                    context=agent.context,
                    width=80,
                    refresh_per_second=10
                )

            # Start streaming display (shows cached content + new user message)
            streaming_display.start_streaming(user_input)

            # Stream the agent response
            streaming_generator = agent.stream_text_message(user_input)

            # Process streaming chunks
            for text_chunk in streaming_generator:
                streaming_display.update_streaming_text(text_chunk)

            # Finalize the stream
            streaming_display.finalize_stream()

            streaming_time = time() - start_time

            # Handle multi-turn tool calling loop
            # The agent may make multiple rounds of tool calls
            from orchestral.llm.base.response import Response

            max_iterations = 10  # Prevent infinite loops
            iteration = 0

            while iteration < max_iterations:
                last_response = agent.context.messages[-1]

                # Check if the last message has tool calls
                if isinstance(last_response, Response) and last_response.message.tool_calls:
                    # Execute tool calls
                    agent._handle_tool_calls()
                    streaming_display.update_after_tools()

                    # Get next LLM response after tools (non-streaming for now)
                    llm_response = agent.llm.get_response(agent.context)
                    agent.context.add_message(llm_response)
                    streaming_display.update_after_tools()

                    iteration += 1
                else:
                    # No more tool calls, conversation turn complete
                    break

            if iteration >= max_iterations:
                streaming_display.stop()
                print(f"\n\nWarning: Reached maximum tool call iterations ({max_iterations})")

            total_time = time() - start_time
            print(f"\n[Streaming time: {streaming_time:.4f}s | Total time: {total_time:.4f}s]")

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
