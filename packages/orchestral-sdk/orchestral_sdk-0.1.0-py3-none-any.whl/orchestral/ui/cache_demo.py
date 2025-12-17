from time import time

from format_context import CachedContextDisplay
from orchestral.ui.logo.logo1 import logo1
from orchestral.ui.commands import handle_command
from rich.console import Console
console = Console()

# Define an example agent with some tools
from orchestral import Agent
from orchestral.llm import Claude
from orchestral.tools import RunCommandTool, RunPythonTool, WriteFileTool, WebSearchTool

base_directory = '/Users/adroman/orchestral3/orchestral_core/demos/demo_files'
tools = [
    RunCommandTool(base_directory=base_directory),
    WriteFileTool(base_directory=base_directory),
    RunPythonTool(base_directory=base_directory),
    WebSearchTool(),
]

# Create cached display instance (reused for performance)
cached_display = None

# Wrapper to use CachedContextDisplay with timing
def cached_display_context(context, width=80, console=None, clear_screen=True):
    global cached_display

    # Create or update cached display instance
    if cached_display is None or cached_display.context is not context:
        cached_display = CachedContextDisplay(context, width)

    # Update width if changed
    if cached_display.width != width:
        cached_display.width = width

    start_time = time()
    cached_display.display(console, clear_screen)
    elapsed = time() - start_time
    # print(f"\n[Display time (CACHED): {elapsed:.4f}s]")

llm = Claude()
agent = Agent(llm=llm, tools=tools, display_hook=cached_display_context)

if __name__ == "__main__":
    print("\033c", end="")
    console.print(logo1)
    console.print('\n  Send a message... ')
    # console.print('  [CACHED MODE - Performance optimized]\n')
    while True:
        # Get user input
        user_input = input('\n> ')

        # Handle special commands
        if user_input[0] == '/':
            handle_command(user_input[1:], agent, console)

        # Normal input
        else:
            agent.run(user_input)
