#!/usr/bin/env python3
"""
Test the simple interactive terminal approach.
"""

import tempfile
import os
import shutil
from orchestral.tools.terminal import RunCommandTool


def test_simple_interactive():
    """Test that interactive prompts return partial output."""
    print("🧪 Testing simple interactive approach...")

    base_dir = tempfile.mkdtemp()

    try:
        tool = RunCommandTool(working_directory=base_dir)

        # Test a simple interactive command
        print("Running: read -p 'Enter your name: ' name")
        result = tool.execute(command="read -p 'Enter your name: ' name")

        print(f"Result: {result}")
        print(f"Return code: {result.split('Return Code: ')[1].split('\\n')[0] if 'Return Code:' in result else 'N/A'}")

        # Check if we got the prompt back instead of a timeout
        if "Enter your name:" in result and "timeout" not in result.lower():
            print("✅ Interactive prompt detected and returned!")

            # Now test responding with 'Alice'
            print("\\nResponding with: Alice")
            result2 = tool.execute(command="Alice")
            print(f"Result2: {result2}")

            return True
        else:
            print("❌ Interactive detection failed!")
            return False

    finally:
        shutil.rmtree(base_dir)


if __name__ == "__main__":
    test_simple_interactive()