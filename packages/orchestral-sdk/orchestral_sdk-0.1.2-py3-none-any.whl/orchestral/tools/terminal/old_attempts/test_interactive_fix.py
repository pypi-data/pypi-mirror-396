#!/usr/bin/env python3
"""
Test the fixed interactive terminal flow.
"""

import tempfile
import shutil
from orchestral.tools.terminal import RunCommandTool


def test_interactive_fix():
    """Test that interactive flow works correctly."""
    print("🧪 Testing fixed interactive flow...")

    base_dir = tempfile.mkdtemp()

    try:
        tool = RunCommandTool(working_directory=base_dir)

        # Step 1: Start interactive command
        print("Step 1: Starting read command...")
        result1 = tool.execute(command="read -p 'Enter your name: ' name")
        print(f"Result1: {result1}")

        # Check if we got the interactive prompt
        if "Enter your name:" in result1 and "Return Code: -1" in result1:
            print("✅ Step 1: Interactive prompt detected!")

            # Step 2: Respond to the prompt
            print("\nStep 2: Responding with 'Alice'...")
            result2 = tool.execute(command="Alice")
            print(f"Result2: {result2}")

            # Check if we got successful completion
            if "Return Code: 0" in result2:
                print("✅ Step 2: Interactive response processed correctly!")

                # Step 3: Test that we can use the variable
                print("\nStep 3: Testing that variable was set...")
                result3 = tool.execute(command="echo Hello $name")
                print(f"Result3: {result3}")

                if "Hello Alice" in result3:
                    print("✅ Step 3: Variable was set correctly!")
                    return True
                else:
                    print("❌ Step 3: Variable was not set!")
                    return False
            else:
                print("❌ Step 2: Interactive response failed!")
                return False
        else:
            print("❌ Step 1: Interactive prompt not detected!")
            return False

    finally:
        shutil.rmtree(base_dir)


if __name__ == "__main__":
    success = test_interactive_fix()
    if success:
        print("\n🎉 Interactive terminal fix works!")
    else:
        print("\n💥 Interactive terminal fix failed!")