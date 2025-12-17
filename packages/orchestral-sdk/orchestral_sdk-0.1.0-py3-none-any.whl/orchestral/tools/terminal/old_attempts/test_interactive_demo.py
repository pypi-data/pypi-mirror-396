#!/usr/bin/env python3
"""
Demo the interactive terminal feature.
"""

import tempfile
import os
import shutil
from orchestral.tools.terminal import RunCommandTool


def test_interactive_terminal():
    """Test interactive responses."""
    print("🧪 Testing interactive terminal feature...")

    base_dir = tempfile.mkdtemp()

    try:
        tool = RunCommandTool(working_directory=base_dir)

        # First, create an interactive Python script
        script_content = '''#!/usr/bin/env python3
name = input("What's your name? ")
age = input("What's your age? ")
print(f"Hello {name}! You are {age} years old.")
'''

        with open(os.path.join(base_dir, "interactive_script.py"), "w") as f:
            f.write(script_content)

        print("Created interactive script...")

        # Run it with interactive responses
        result = tool.execute(
            command="python3 interactive_script.py",
            interactive_responses={
                "What's your name? ": "Alice",
                "What's your age? ": "25"
            }
        )

        print(f"Result: {result}")

        if "Hello Alice! You are 25 years old." in result:
            print("✅ Interactive terminal feature works!")
            return True
        else:
            print("❌ Interactive terminal feature failed!")
            return False

    finally:
        shutil.rmtree(base_dir)


if __name__ == "__main__":
    test_interactive_terminal()