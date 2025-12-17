from time import time

from format_context import display_context
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

# Wrapper to add timing to display_context
def timed_display_context(context, width=80, console=None, clear_screen=True):
    start_time = time()
    display_context(context, width, console, clear_screen)
    elapsed = time() - start_time
    print(f"\n[Display time: {elapsed:.4f}s]")


llm = Claude()
agent = Agent(llm=llm, tools=tools, display_hook=timed_display_context)

if __name__ == "__main__":
    print("\033c", end="")
    console.print(logo1)
    console.print('\n  Send a message... ')
    while True:
        # Get user input
        user_input = input('\n> ')

        # Handle special commands
        if user_input[0] == '/':
            handle_command(user_input[1:], agent, console)

        # Normal input
        else:
            agent.run(user_input)