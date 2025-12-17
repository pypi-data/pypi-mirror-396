#!/usr/bin/env python3
"""
Test interactive prompt handling for the terminal tool.
Tests the ability to automatically respond to interactive prompts.
"""

import tempfile
import shutil
from orchestral.tools.terminal_tool import RunCommandTool, PEXPECT_AVAILABLE

def test_interactive_prompt_basic():
    """Test basic interactive prompt handling."""
    print("🧪 Testing basic interactive prompt handling...")

    if not PEXPECT_AVAILABLE:
        print("⚠️ Skipping interactive test - pexpect not available")
        return

    base_dir = tempfile.mkdtemp()
    tool = RunCommandTool(base_directory=base_dir, persistent_mode=True)

    try:
        # Test a command that would normally prompt for confirmation
        # We'll use Python to simulate an interactive prompt
        interactive_responses = {
            "Do you want to continue?": "yes"
        }

        # Create a Python script that asks for confirmation
        python_script = '''
import sys
print("Starting operation...")
response = input("Do you want to continue? (yes/no): ")
if response.lower() == "yes":
    print("Operation completed successfully!")
else:
    print("Operation cancelled.")
sys.exit(0 if response.lower() == "yes" else 1)
'''

        # First create the script file
        tool.execute(command=f'cat > test_interactive.py << "EOF"\n{python_script}\nEOF')

        # Now run it with interactive responses
        result = tool.execute(
            command="python test_interactive.py",
            interactive_responses=interactive_responses
        )
        print("✅ Interactive prompt test:")
        print(result)
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error during interactive test: {e}")
    finally:
        tool.close_session()
        shutil.rmtree(base_dir)

def test_multiple_prompts():
    """Test handling multiple interactive prompts."""
    print("\n🧪 Testing multiple interactive prompts...")

    if not PEXPECT_AVAILABLE:
        print("⚠️ Skipping multiple prompts test - pexpect not available")
        return

    base_dir = tempfile.mkdtemp()
    tool = RunCommandTool(base_directory=base_dir, persistent_mode=True)

    try:
        # Create a script with multiple prompts
        multi_prompt_script = '''
import sys
print("Multi-step configuration...")
name = input("Enter your name: ")
age = input("Enter your age: ")
confirm = input(f"Name: {name}, Age: {age}. Is this correct? (y/n): ")
if confirm.lower() == "y":
    print(f"Configuration saved for {name}, age {age}")
else:
    print("Configuration cancelled")
'''

        interactive_responses = {
            "Enter your name:": "Alice",
            "Enter your age:": "30",
            "Is this correct?": "y"
        }

        # Create and run the script
        tool.execute(command=f'cat > multi_prompt.py << "EOF"\n{multi_prompt_script}\nEOF')

        result = tool.execute(
            command="python multi_prompt.py",
            interactive_responses=interactive_responses
        )
        print("✅ Multiple prompts test:")
        print(result)
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error during multiple prompts test: {e}")
    finally:
        tool.close_session()
        shutil.rmtree(base_dir)

def test_prompt_timeout():
    """Test timeout handling with interactive prompts."""
    print("\n🧪 Testing prompt timeout handling...")

    if not PEXPECT_AVAILABLE:
        print("⚠️ Skipping timeout test - pexpect not available")
        return

    base_dir = tempfile.mkdtemp()
    tool = RunCommandTool(base_directory=base_dir, persistent_mode=True)

    try:
        # Create a script that prompts but we don't provide a response
        timeout_script = '''
import sys
print("This will wait for input...")
response = input("Enter something (we won't respond): ")
print(f"You entered: {response}")
'''

        # Run without providing the expected response (should timeout)
        tool.execute(command=f'cat > timeout_test.py << "EOF"\n{timeout_script}\nEOF')

        result = tool.execute(
            command="python timeout_test.py",
            timeout=3  # Short timeout
        )
        print("✅ Timeout test:")
        print(result)
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error during timeout test: {e}")
    finally:
        tool.close_session()
        shutil.rmtree(base_dir)

def test_regex_prompt_matching():
    """Test regex pattern matching for prompts."""
    print("\n🧪 Testing regex prompt matching...")

    if not PEXPECT_AVAILABLE:
        print("⚠️ Skipping regex test - pexpect not available")
        return

    base_dir = tempfile.mkdtemp()
    tool = RunCommandTool(base_directory=base_dir, persistent_mode=True)

    try:
        # Create a script with variable prompts
        regex_script = '''
import sys
import random
num = random.randint(1, 100)
response = input(f"Enter a number greater than {num}: ")
print(f"You entered: {response}")
'''

        # Use regex pattern to match variable prompts
        interactive_responses = {
            r"Enter a number greater than \d+:": "999"  # regex pattern
        }

        tool.execute(command=f'cat > regex_test.py << "EOF"\n{regex_script}\nEOF')

        result = tool.execute(
            command="python regex_test.py",
            interactive_responses=interactive_responses
        )
        print("✅ Regex matching test:")
        print(result)
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error during regex test: {e}")
    finally:
        tool.close_session()
        shutil.rmtree(base_dir)

def main():
    """Run all interactive prompt tests."""
    print("🚀 Starting interactive prompt tests...")
    print(f"pexpect available: {PEXPECT_AVAILABLE}")
    print("=" * 60)

    try:
        test_interactive_prompt_basic()
        test_multiple_prompts()
        test_prompt_timeout()
        test_regex_prompt_matching()

        print("\n🎉 All interactive prompt tests completed!")

    except Exception as e:
        print(f"\n❌ Interactive prompt tests failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()