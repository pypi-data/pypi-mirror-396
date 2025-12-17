#!/usr/bin/env python3
"""Debug output capture issues in detail."""

import tempfile
import shutil
from orchestral.tools.terminal_tool import RunCommandTool

def debug_output_capture():
    """Debug step by step what's happening with output capture."""
    print("🔍 Debugging output capture...")

    base_dir = tempfile.mkdtemp()
    tool = RunCommandTool(base_directory=base_dir, persistent_mode=True)

    try:
        # Manually step through the process to see what's happening
        print(f"Base directory: {base_dir}")

        # Test simple echo command
        command = "echo 'Hello World'"
        print(f"Testing command: {command}")

        # Get the raw session output
        tool._setup()
        if tool._session_healthy():
            print("❌ Session should not be healthy before starting")

        # Start session manually
        tool._start_session()
        print("✅ Session started")

        # Send command and capture raw output
        tool._shell_session.sendline(command)
        print(f"📤 Sent command: {command}")

        # Wait for prompt
        tool._shell_session.expect('READY> ', timeout=10)
        print("✅ Got prompt back")

        # Get raw output
        raw_output = tool._shell_session.before
        print(f"📥 Raw output type: {type(raw_output)}")
        print(f"📥 Raw output bytes: {raw_output}")

        if isinstance(raw_output, bytes):
            decoded = raw_output.decode('utf-8', errors='replace')
        else:
            decoded = str(raw_output)

        print(f"📥 Decoded output: {repr(decoded)}")
        print(f"📥 Decoded lines: {decoded.split('\\n')}")

        # Test the filtering
        import re
        cleaned = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', decoded)
        cleaned = re.sub(r'\r\n', '\n', cleaned)
        cleaned = re.sub(r'\r', '\n', cleaned)

        print(f"📥 Cleaned output: {repr(cleaned)}")
        lines = cleaned.split('\n')
        print(f"📥 Cleaned lines: {lines}")

        # Now test through the tool
        result = tool.execute(command="echo 'Test through tool'")
        print(f"📥 Tool result: {result}")

    finally:
        tool.close_session()
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    debug_output_capture()