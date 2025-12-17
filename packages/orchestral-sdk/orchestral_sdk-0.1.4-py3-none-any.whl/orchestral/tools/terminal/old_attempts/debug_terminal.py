#!/usr/bin/env python3
"""Debug the terminal tool output capture."""

import tempfile
import shutil
from orchestral.tools.terminal_tool import RunCommandTool

def debug_simple_command():
    """Debug a simple command step by step."""
    print("🔍 Debugging simple command...")

    base_dir = tempfile.mkdtemp()
    print(f"Base directory: {base_dir}")

    try:
        # Test with one-shot mode first
        tool = RunCommandTool(base_directory=base_dir, persistent_mode=False)
        result = tool.execute(command="echo 'Hello World'")
        print("One-shot mode result:")
        print(repr(result))
        print("-" * 50)

        # Test with persistent mode
        tool_persistent = RunCommandTool(base_directory=base_dir, persistent_mode=True)
        result = tool_persistent.execute(command="echo 'Hello from persistent'")
        print("Persistent mode result:")
        print(repr(result))
        print("-" * 50)

        # Test ls command
        result = tool_persistent.execute(command="ls")
        print("ls command result:")
        print(repr(result))
        print("-" * 50)

        tool_persistent.close_session()

    finally:
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    debug_simple_command()