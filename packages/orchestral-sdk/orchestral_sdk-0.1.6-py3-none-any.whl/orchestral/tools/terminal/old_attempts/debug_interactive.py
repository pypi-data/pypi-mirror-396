#!/usr/bin/env python3
"""
Debug the interactive terminal issue.
"""

import tempfile
import shutil
from orchestral.tools.terminal import RunCommandTool


def debug_interactive():
    """Debug the interactive flow."""
    print("🔍 Debugging interactive flow...")

    base_dir = tempfile.mkdtemp()

    try:
        tool = RunCommandTool(working_directory=base_dir)

        # Step 1: Start interactive command
        print("Step 1: Starting read command...")
        print(f"Tool waiting_for_input state before: {tool.waiting_for_input}")
        result1 = tool.execute(command="read -p 'Enter your name: ' name")
        print(f"Tool waiting_for_input state after: {tool.waiting_for_input}")
        print(f"Result1: {result1}")
        print()

        # Step 2: Respond to the prompt
        print("Step 2: Responding with 'Alice'...")
        print(f"Tool waiting_for_input state before: {tool.waiting_for_input}")
        result2 = tool.execute(command="Alice")
        print(f"Tool waiting_for_input state after: {tool.waiting_for_input}")
        print(f"Result2: {result2}")

    finally:
        shutil.rmtree(base_dir)


if __name__ == "__main__":
    debug_interactive()