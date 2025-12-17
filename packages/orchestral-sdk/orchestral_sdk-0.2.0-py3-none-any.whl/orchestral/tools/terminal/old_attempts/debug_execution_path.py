#!/usr/bin/env python3
"""Debug the actual execution path and any exceptions."""

import tempfile
import shutil
import os
from orchestral.tools.terminal_tool import RunCommandTool

def debug_execution_path():
    """Debug the execution path with detailed logging."""
    print("🔍 Debugging execution path...")

    base_dir = tempfile.mkdtemp()

    try:
        # Create test folder
        os.mkdir(os.path.join(base_dir, "test_folder"))

        tool = RunCommandTool(base_directory=base_dir, persistent_mode=True)

        # Patch methods to see exactly what's happening
        original_run = tool._run
        original_persistent = tool._execute_persistent
        original_oneshot = tool._execute_oneshot

        def debug_run():
            print("📞 _run() called")
            print(f"  Command: {tool.command}")
            print(f"  Should use persistent: {tool._should_use_persistent()}")
            print(f"  Persistent mode: {tool.persistent_mode}")
            print(f"  Auto fallback: {tool.auto_fallback}")
            return original_run()

        def debug_persistent():
            print("✅ _execute_persistent() called")
            try:
                result = original_persistent()
                print(f"✅ Persistent execution succeeded: {result[:100]}...")
                return result
            except Exception as e:
                print(f"❌ Persistent execution failed: {e}")
                raise

        def debug_oneshot():
            print("🔥 _execute_oneshot() called")
            try:
                result = original_oneshot()
                print(f"🔥 One-shot execution result: {result[:100]}...")
                return result
            except Exception as e:
                print(f"❌ One-shot execution failed: {e}")
                raise

        tool._run = debug_run
        tool._execute_persistent = debug_persistent
        tool._execute_oneshot = debug_oneshot

        # Test cd command
        print("\n--- Testing cd command ---")
        result = tool.execute(command="cd test_folder")
        print(f"Final result: {result}")

        # Test pwd after cd
        print("\n--- Testing pwd after cd ---")
        result2 = tool.execute(command="pwd")
        print(f"Final result: {result2}")

    finally:
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    debug_execution_path()