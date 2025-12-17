"""
Persistent terminal tools for Orchestral.

This package provides terminal interaction capabilities with persistent
session state. Commands like 'cd', 'export', and 'source' maintain their
effects across multiple tool calls.

Main components:
- RunCommandTool: Orchestral tool interface
- PersistentTerminal: Core terminal implementation (platform-specific)
"""

from .tool import RunCommandTool
from .dummy_tool import DummyRunCommandTool

__all__ = ['RunCommandTool', 'DummyRunCommandTool']