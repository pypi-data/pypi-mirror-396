#!/usr/bin/env python3
"""Debug the marker approach in detail."""

import tempfile
import shutil
from orchestral.tools.terminal_tool import RunCommandTool

def debug_marker_step_by_step():
    """Debug the marker approach step by step."""
    print("🔍 Debugging marker approach...")

    base_dir = tempfile.mkdtemp()
    tool = RunCommandTool(base_directory=base_dir, persistent_mode=True)

    try:
        # Initialize session
        tool._setup()
        tool._start_session()
        print("✅ Session started")

        # Test simple ls command manually
        command = "ls"
        print(f"Testing command: {command}")

        # Step 1: Send marker
        import time
        marker = f"__CMD_START_{int(time.time())}__{id(tool)}__"
        print(f"Marker: {marker}")

        tool._shell_session.sendline(f'echo "{marker}"')
        tool._shell_session.expect('READY> ', timeout=5)
        print("✅ Marker sent and prompt returned")

        # Step 2: Send actual command
        tool._shell_session.sendline(command)
        tool._shell_session.expect('READY> ', timeout=5)
        print("✅ Command sent and prompt returned")

        # Step 3: Get raw output
        raw_output = tool._shell_session.before
        print(f"📥 Raw output: {raw_output}")

        if isinstance(raw_output, bytes):
            decoded = raw_output.decode('utf-8', errors='replace')
        else:
            decoded = str(raw_output)

        print(f"📥 Decoded: {repr(decoded)}")

        # Step 4: Process with marker logic
        import re
        cleaned = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', decoded)
        cleaned = re.sub(r'\r\n', '\n', cleaned)
        cleaned = re.sub(r'\r', '\n', cleaned)

        lines = cleaned.split('\n')
        print(f"📥 Lines: {lines}")

        # Find marker and capture
        capturing = False
        filtered_lines = []

        for line in lines:
            print(f"Processing line: {repr(line)}")
            if marker in line:
                print("  → Found marker, start capturing")
                capturing = True
                continue

            if capturing:
                if line.strip() == command.strip():
                    print("  → Skipping command echo")
                    continue

                if line.strip() in ['PS1="READY> "', 'READY>', f'cd "{base_dir}"']:
                    print("  → Skipping artifact")
                    continue

                print(f"  → Capturing: {repr(line)}")
                filtered_lines.append(line)

        final_output = '\n'.join(filtered_lines).rstrip()
        print(f"📥 Final output: {repr(final_output)}")

        # Compare with tool result
        print("\n" + "="*50)
        result = tool.execute(command="ls")
        print("Tool result:")
        print(result)

    finally:
        tool.close_session()
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    debug_marker_step_by_step()