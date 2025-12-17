#!/usr/bin/env python3
"""
Manual test to understand pexpect behavior with read command.
"""

import pexpect
import tempfile
import os

def test_manual_pexpect():
    """Test what happens with pexpect and read command."""

    # Create temp directory
    temp_dir = tempfile.mkdtemp()

    try:
        # Start bash session
        session = pexpect.spawn(
            'bash --norc --noprofile',
            cwd=temp_dir,
            timeout=30,
            encoding='utf-8',
            codec_errors='replace'
        )

        # Set custom prompt
        prompt_marker = "ORCHTERM_READY>"
        session.sendline(f'PS1="{prompt_marker} "')
        session.expect(prompt_marker, timeout=10)

        # Clear buffer
        try:
            session.read_nonblocking(size=1000, timeout=0.1)
        except:
            pass

        print("=== Test 1: Send read command ===")
        session.sendline("read -p 'Enter name: ' name")

        # Wait for the prompt
        patterns = [prompt_marker, r'.*:\s*$']
        index = session.expect(patterns, timeout=10)

        if index == 1:
            print("Got interactive prompt!")
            print(f"Before: '{session.before}'")
            print(f"After: '{session.after}'")

            print("\n=== Test 2: Send response ===")
            session.sendline("Alice")

            # Now what happens?
            session.expect(prompt_marker, timeout=10)
            print(f"After response - Before: '{session.before}'")

            print("\n=== Test 3: Check variable ===")
            session.sendline("echo Hello $name")
            session.expect(prompt_marker, timeout=10)
            print(f"Variable test - Before: '{session.before}'")

        session.close()

    finally:
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_manual_pexpect()