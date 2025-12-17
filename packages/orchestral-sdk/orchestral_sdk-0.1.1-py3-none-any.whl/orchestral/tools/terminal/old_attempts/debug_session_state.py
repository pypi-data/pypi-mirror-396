#!/usr/bin/env python3
"""
Debug the session state in detail.
"""

import tempfile
import shutil
from orchestral.tools.terminal.mac_linux import PersistentTerminal


def debug_session_state():
    """Debug session state at low level."""
    print("🔍 Debugging session state...")

    base_dir = tempfile.mkdtemp()

    try:
        terminal = PersistentTerminal()
        terminal.start_session(base_dir)

        print("=== Step 1: Regular command ===")
        result1 = terminal.execute_command("echo Hello World")
        print(f"Result1: return_code={result1.return_code}, output='{result1.output}'")

        print("\n=== Step 2: Interactive command ===")
        result2 = terminal.execute_command("read -p 'Enter name: ' name")
        print(f"Result2: return_code={result2.return_code}, output='{result2.output}'")

        if result2.return_code == -1:
            print("✅ Interactive prompt detected")

            print("\n=== Step 3: Provide input ===")
            result3 = terminal.execute_command("Alice", waiting_for_input=True)
            print(f"Result3: return_code={result3.return_code}, output='{result3.output}'")

            print("\n=== Step 4: Test variable ===")
            result4 = terminal.execute_command("echo $name")
            print(f"Result4: return_code={result4.return_code}, output='{result4.output}'")

            if "Alice" in result4.output:
                print("✅ Session state preserved!")
                return True
            else:
                print("❌ Session state lost!")

        terminal.close()

    finally:
        shutil.rmtree(base_dir)

    return False


if __name__ == "__main__":
    success = debug_session_state()
    if success:
        print("\n🎉 Session state works!")
    else:
        print("\n💥 Session state failed!")