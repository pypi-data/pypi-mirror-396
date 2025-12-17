#!/usr/bin/env python3
"""
Test the complete interactive flow.
"""

import tempfile
import os
import shutil
from orchestral.tools.terminal import RunCommandTool


def test_complete_interactive_flow():
    """Test the complete interactive flow."""
    print("🧪 Testing complete interactive flow...")

    base_dir = tempfile.mkdtemp()

    try:
        tool = RunCommandTool(working_directory=base_dir)

        # Step 1: Start interactive command
        print("Step 1: Starting read command...")
        result1 = tool.execute(command="read -p 'Enter your name: ' name && echo Hello $name")
        print(f"Result1: {result1}")

        # Check if we got the interactive prompt
        if "Enter your name:" in result1 and "Return Code: -1" in result1:
            print("✅ Step 1: Interactive prompt detected!")

            # Step 2: Respond to the prompt
            print("\\nStep 2: Responding with 'Alice'...")
            result2 = tool.execute(command="Alice")
            print(f"Result2: {result2}")

            # Check if we got the expected output
            if "Hello Alice" in result2:
                print("✅ Step 2: Interactive response processed correctly!")
                return True
            else:
                print("❌ Step 2: Interactive response failed!")
                return False
        else:
            print("❌ Step 1: Interactive prompt not detected!")
            return False

    finally:
        shutil.rmtree(base_dir)


if __name__ == "__main__":
    test_complete_interactive_flow()