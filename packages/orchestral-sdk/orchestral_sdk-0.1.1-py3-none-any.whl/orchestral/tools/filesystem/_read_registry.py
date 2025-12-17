"""
Global registry for tracking which files have been read and when.

DEPRECATED: This global registry is kept as a fallback for tools used without an Agent.
Prefer using context.metadata["files_read"] which is per-conversation and persistent.

When tools are used with an Agent (recommended):
- Agent injects context into tools via agent_context StateField
- Tools use context.metadata["files_read"] (per-conversation, saved/loaded)

When tools are used standalone (not recommended):
- Tools fall back to this global FILES_READ dict
- Not per-conversation, not persistent

This enables "read before edit" enforcement to prevent LLM hallucinations.
When a file is read via ReadFileTool, its absolute path and modification time are stored.
When EditFileTool is called, it checks:
1. Has the file been read? (prevents hallucination)
2. Has the file been modified since it was read? (prevents stale edits)
"""

from typing import Dict

# Global dict mapping absolute file paths to their modification time when read
# DEPRECATED: Use context.metadata["files_read"] instead (available via agent_context)
# This is only used as a fallback for tools used without an Agent
FILES_READ: Dict[str, float] = {}
