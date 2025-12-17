#!/usr/bin/env python3
"""
Fix all tools.json files by removing RuntimeFields and working_directory.
"""

import json
from pathlib import Path

# RuntimeFields that should never be saved
RUNTIME_FIELDS = ['command', 'code', 'filepath', 'content', 'query', 'filename', 'new_content']

# Directory fields handled by base_directory in metadata
DIRECTORY_FIELDS = ['working_directory', 'base_directory']

def fix_tools_json(filepath: Path):
    """Fix a single tools.json file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    modified = False

    for tool_config in data.get('tools', []):
        kwargs = tool_config.get('kwargs', {})

        # Remove RuntimeFields
        for field in RUNTIME_FIELDS:
            if field in kwargs:
                print(f"  Removing RuntimeField '{field}' from {tool_config['name']}")
                del kwargs[field]
                modified = True

        # Remove directory fields (except for tools that don't support base_directory injection)
        for field in DIRECTORY_FIELDS:
            if field in kwargs:
                print(f"  Removing '{field}' from {tool_config['name']}")
                del kwargs[field]
                modified = True

    if modified:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    return False

def main():
    conversations_dir = Path(__file__).parent / "conversations"

    if not conversations_dir.exists():
        print(f"Conversations directory not found: {conversations_dir}")
        return

    print(f"Scanning {conversations_dir}...")

    fixed_count = 0
    for tools_json in conversations_dir.glob("*/tools.json"):
        print(f"\nChecking {tools_json.parent.name}...")
        if fix_tools_json(tools_json):
            fixed_count += 1
            print(f"  ✓ Fixed")
        else:
            print(f"  ✓ Already clean")

    print(f"\n✅ Fixed {fixed_count} tools.json files")

if __name__ == "__main__":
    main()
