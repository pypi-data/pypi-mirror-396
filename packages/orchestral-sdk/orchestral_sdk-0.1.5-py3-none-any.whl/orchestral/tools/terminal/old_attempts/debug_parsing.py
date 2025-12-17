#!/usr/bin/env python3
"""
Debug the output parsing logic with real data.
"""

def debug_parsing():
    """Debug parsing logic with known good data."""
    # This is the real output we saw from pexpect
    raw_output = ' "\r\nls\r\ntest_folder.txt\r\n'
    command = "ls"

    print(f"Raw output: {repr(raw_output)}")
    print(f"Command: {repr(command)}")

    # Current parsing logic
    if not raw_output:
        output = ""
    else:
        # Clean up carriage returns and normalize line endings
        cleaned = raw_output.replace('\r\n', '\n').replace('\r', '\n')
        print(f"Cleaned: {repr(cleaned)}")

        # Split into lines
        lines = cleaned.split('\n')
        print(f"Lines: {lines}")

        # Remove empty lines at start
        while lines and not lines[0].strip():
            lines.pop(0)
        print(f"After removing empty start: {lines}")

        # Remove command echo if it's the first line
        if lines and lines[0].strip() == command.strip():
            lines.pop(0)
        print(f"After removing command echo: {lines}")

        # Remove empty lines at end
        while lines and not lines[-1].strip():
            lines.pop()
        print(f"After removing empty end: {lines}")

        # Join output
        output = '\n'.join(lines)

    print(f"Final output: {repr(output)}")

if __name__ == "__main__":
    debug_parsing()