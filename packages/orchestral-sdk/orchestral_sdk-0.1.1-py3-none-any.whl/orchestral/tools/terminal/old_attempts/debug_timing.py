#!/usr/bin/env python3
"""
Debug timing issue with interactive commands.
"""

import pexpect
import tempfile
import time


def debug_timing():
    """Debug timing of interactive commands."""
    temp_dir = tempfile.mkdtemp()

    try:
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

        print("=== Sending read command ===")
        session.sendline("read -p 'Enter name: ' name")

        # Wait for interactive prompt
        interactive_patterns = [r'.*:\s*$']
        patterns = [prompt_marker] + interactive_patterns
        index = session.expect(patterns, timeout=30)

        if index != 0:
            print("✅ Got interactive prompt")

            # SIMULATE THE DELAY BETWEEN TOOL CALLS
            print("⏰ Sleeping for 2 seconds to simulate tool call delay...")
            time.sleep(2)

            print("Session alive after delay:", session.isalive())

            # Now send Alice
            print("Sending Alice after delay...")
            session.sendline("Alice")

            # Wait for completion
            session.expect(prompt_marker, timeout=30)
            print(f"After Alice: '{session.before}'")

            # Test variable
            session.sendline("echo Variable: $name")
            session.expect(prompt_marker, timeout=30)
            print(f"Variable test: '{session.before}'")

        session.close()

    finally:
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    debug_timing()