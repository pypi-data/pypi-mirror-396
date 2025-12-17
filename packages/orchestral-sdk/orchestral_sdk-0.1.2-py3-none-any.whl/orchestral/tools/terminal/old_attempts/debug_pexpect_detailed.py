#!/usr/bin/env python3
"""
Very detailed debugging of pexpect session state.
"""

import pexpect
import tempfile
import time


def debug_detailed():
    """Debug pexpect session in detail."""
    temp_dir = tempfile.mkdtemp()

    try:
        # Start session exactly like our tool does
        session = pexpect.spawn(
            'bash --norc --noprofile',
            cwd=temp_dir,
            timeout=30,
            encoding='utf-8',
            codec_errors='replace'
        )

        prompt_marker = "ORCHTERM_READY>"
        session.sendline(f'PS1="{prompt_marker} "')
        session.expect(prompt_marker, timeout=10)

        # Clear buffer
        try:
            session.read_nonblocking(size=1000, timeout=0.1)
        except:
            pass

        print("=== Session initialized ===")

        # Send read command exactly like our tool does
        print("Sending: read -p 'Enter name: ' name")
        session.sendline("read -p 'Enter name: ' name")

        # Wait for interactive prompt exactly like our tool does
        interactive_patterns = [
            r'.*\?\s*$',
            r'.*\(y/n\)\s*$',
            r'.*\(Y/n\)\s*$',
            r'.*\(yes/no\)\s*$',
            r'.*:\s*$'
        ]
        patterns = [prompt_marker] + interactive_patterns

        print("Waiting for patterns...")
        index = session.expect(patterns, timeout=30)
        print(f"Got pattern index: {index}")

        if index == 0:
            print("❌ Got prompt immediately - no interactive")
        else:
            print(f"✅ Got interactive pattern: {patterns[index]}")
            print(f"Session before: '{session.before}'")
            print(f"Session after: '{session.after}'")

            print(f"Session alive: {session.isalive()}")

            # Now send Alice exactly like our tool does
            print("\nSending Alice...")
            session.sendline("Alice")

            # Wait for completion
            print("Waiting for completion...")
            session.expect(prompt_marker, timeout=30)
            print(f"Completion - before: '{session.before}'")

            # Test variable
            print("\nTesting variable...")
            session.sendline("echo Variable: $name")
            session.expect(prompt_marker, timeout=30)
            print(f"Variable test - before: '{session.before}'")

        session.close()

    finally:
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    debug_detailed()