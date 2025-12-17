#!/usr/bin/env python3
"""
Debug raw pexpect behavior to understand output capture issues.
"""

import tempfile
import os
import pexpect

def debug_raw_pexpect():
    """Debug raw pexpect to see what's happening."""
    print("🔍 Debugging raw pexpect...")

    base_dir = tempfile.mkdtemp()
    print(f"Base directory: {base_dir}")

    try:
        # Create test file
        with open(os.path.join(base_dir, "test.txt"), "w") as f:
            f.write("hello world")

        # Start raw pexpect session
        session = pexpect.spawn(
            'bash --norc --noprofile',
            cwd=base_dir,
            timeout=30,
            encoding='utf-8',
            codec_errors='replace'
        )

        print("✅ Session started")

        # Set prompt
        prompt = "DEBUG_READY>"
        session.sendline(f'PS1="{prompt} "')
        session.expect(prompt, timeout=10)
        print("✅ Prompt set")

        # Clear buffer
        try:
            session.read_nonblocking(size=1000, timeout=0.1)
        except:
            pass

        # Send ls command
        print("\n--- Sending ls command ---")
        session.sendline("ls")
        session.expect(prompt, timeout=10)

        raw_output = session.before
        print(f"Raw output type: {type(raw_output)}")
        print(f"Raw output: {repr(raw_output)}")

        if raw_output:
            lines = raw_output.split('\n')
            print(f"Lines: {lines}")

        session.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        import shutil
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    debug_raw_pexpect()