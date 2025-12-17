#!/usr/bin/env python3
"""
Debug the tool execution step by step.
"""

import tempfile
import os
import shutil
from orchestral.tools.terminal.mac_linux import PersistentTerminal

def debug_tool_execution():
    """Debug tool execution step by step."""
    print("🔍 Debugging tool execution...")

    base_dir = tempfile.mkdtemp()
    print(f"Base directory: {base_dir}")

    try:
        # Create test file
        with open(os.path.join(base_dir, "test_folder.txt"), "w") as f:
            f.write("test")

        # Verify file was created
        print(f"Files in base_dir: {os.listdir(base_dir)}")

        # Direct terminal test
        terminal = PersistentTerminal()
        terminal.start_session(base_dir)

        print("\n--- Direct terminal test ---")
        result = terminal.execute_command("ls")
        print(f"Result object: {result}")
        print(f"Command: {result.command}")
        print(f"Output: {repr(result.output)}")
        print(f"Return code: {result.return_code}")

        terminal.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    debug_tool_execution()