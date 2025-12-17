#!/usr/bin/env python3
"""Debug mode selection logic."""

import tempfile
import shutil
import os
from orchestral.tools.terminal_tool import RunCommandTool, PEXPECT_AVAILABLE

def debug_mode_selection():
    """Debug why persistent mode isn't being used."""
    print("🔍 Debugging mode selection...")
    print(f"PEXPECT_AVAILABLE: {PEXPECT_AVAILABLE}")

    base_dir = tempfile.mkdtemp()
    tool = RunCommandTool(base_directory=base_dir, persistent_mode=True)

    print(f"Tool persistent_mode: {tool.persistent_mode}")

    # Test various commands
    test_commands = ["ls", "cd test_folder", "pwd", "echo hello"]

    for cmd in test_commands:
        tool.command = cmd
        should_use = tool._should_use_persistent()
        print(f"Command: '{cmd}' -> should_use_persistent: {should_use}")

    # Test the actual execution path
    print("\n--- Testing execution path ---")

    # Patch the execution methods to see which is called
    original_oneshot = tool._execute_oneshot
    original_persistent = tool._execute_persistent

    def debug_oneshot():
        print("🔥 USING ONE-SHOT MODE")
        return original_oneshot()

    def debug_persistent():
        print("✅ USING PERSISTENT MODE")
        return original_persistent()

    tool._execute_oneshot = debug_oneshot
    tool._execute_persistent = debug_persistent

    # Test cd command
    result = tool.execute(command="cd test_folder")
    print(f"Result: {result}")

    shutil.rmtree(base_dir)

if __name__ == "__main__":
    debug_mode_selection()