#!/usr/bin/env python3
"""Debug persistent state management."""

import tempfile
import shutil
import os
from orchestral.tools.terminal_tool import RunCommandTool

def debug_persistent_state():
    """Debug why cd commands don't persist."""
    print("🔍 Debugging persistent state...")

    base_dir = tempfile.mkdtemp()
    print(f"Base directory: {base_dir}")

    try:
        # Create test structure
        os.mkdir(os.path.join(base_dir, "test_folder"))
        with open(os.path.join(base_dir, "test_folder", "file_in_folder.txt"), "w") as f:
            f.write("I'm inside the folder!")

        # Test with explicit persistent mode
        tool = RunCommandTool(base_directory=base_dir, persistent_mode=True)

        # Step 1: Initial ls
        result1 = tool.execute(command="ls")
        print("Step 1 - Initial ls:")
        print(result1)
        print("-" * 50)

        # Step 2: Check current directory
        result2 = tool.execute(command="pwd")
        print("Step 2 - Current directory:")
        print(result2)
        print("-" * 50)

        # Step 3: Change directory
        result3 = tool.execute(command="cd test_folder")
        print("Step 3 - Change directory:")
        print(result3)
        print("-" * 50)

        # Step 4: Check current directory again
        result4 = tool.execute(command="pwd")
        print("Step 4 - Current directory after cd:")
        print(result4)
        print("-" * 50)

        # Step 5: List files in new directory
        result5 = tool.execute(command="ls")
        print("Step 5 - List files in new directory:")
        print(result5)
        print("-" * 50)

        # Step 6: Check session health
        print(f"Session healthy: {tool._session_healthy()}")
        print(f"Session alive: {tool._shell_session.isalive() if tool._shell_session else 'No session'}")

        tool.close_session()

    finally:
        shutil.rmtree(base_dir)

def debug_session_internals():
    """Debug what's happening inside the session."""
    print("\n🔍 Debugging session internals...")

    base_dir = tempfile.mkdtemp()
    tool = RunCommandTool(base_directory=base_dir, persistent_mode=True)

    try:
        # Create test folder
        os.mkdir(os.path.join(base_dir, "debug_folder"))

        # Initialize session manually
        tool._setup()
        tool._start_session()
        print("✅ Session initialized")

        # Send commands manually and observe
        print("\n--- Manual command sequence ---")

        # 1. Check initial directory
        tool._shell_session.sendline("pwd")
        tool._shell_session.expect('READY> ', timeout=5)
        output1 = tool._shell_session.before.decode('utf-8', errors='replace')
        print(f"Initial pwd output: {repr(output1)}")

        # 2. Change directory
        tool._shell_session.sendline("cd debug_folder")
        tool._shell_session.expect('READY> ', timeout=5)
        output2 = tool._shell_session.before.decode('utf-8', errors='replace')
        print(f"cd output: {repr(output2)}")

        # 3. Check directory again
        tool._shell_session.sendline("pwd")
        tool._shell_session.expect('READY> ', timeout=5)
        output3 = tool._shell_session.before.decode('utf-8', errors='replace')
        print(f"Final pwd output: {repr(output3)}")

        tool.close_session()

    finally:
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    debug_persistent_state()
    debug_session_internals()