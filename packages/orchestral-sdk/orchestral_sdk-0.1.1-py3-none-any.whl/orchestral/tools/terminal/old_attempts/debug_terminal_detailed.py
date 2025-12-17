#!/usr/bin/env python3
"""Detailed debug of persistent mode output capture."""

import tempfile
import shutil
import pexpect

def debug_pexpect_directly():
    """Debug pexpect directly to see what's happening."""
    print("🔍 Testing pexpect directly...")

    base_dir = tempfile.mkdtemp()
    print(f"Base directory: {base_dir}")

    try:
        # Start pexpect session
        session = pexpect.spawn('bash', cwd=base_dir, timeout=10)

        # Wait for prompt
        session.expect(['$', '#'], timeout=5)
        print("✅ Initial prompt detected")

        # Send echo command
        session.sendline("echo 'Hello from pexpect'")
        print("📤 Sent command: echo 'Hello from pexpect'")

        # Wait for prompt return
        session.expect(['$', '#'], timeout=5)
        print("✅ Prompt returned")

        # Get all outputs
        print(f"📥 session.before: {session.before}")
        print(f"📥 session.after: {session.after}")
        print(f"📥 session.match: {session.match}")

        # Try reading buffer
        try:
            remaining = session.read_nonblocking(size=1000, timeout=0.1)
            print(f"📥 Remaining buffer: {remaining}")
        except:
            print("📥 No remaining buffer")

        # Get full session log if available
        if hasattr(session, 'logfile_read'):
            print(f"📥 Logfile: {session.logfile_read}")

        # The actual command output should be in session.before
        raw_output = session.before
        if isinstance(raw_output, bytes):
            decoded = raw_output.decode('utf-8', errors='replace')
        else:
            decoded = str(raw_output)

        print(f"📥 Final decoded: {repr(decoded)}")
        print(f"📥 Final lines: {decoded.split('\n') if decoded else 'EMPTY'}")

        session.close()

    finally:
        shutil.rmtree(base_dir)

if __name__ == "__main__":
    debug_pexpect_directly()