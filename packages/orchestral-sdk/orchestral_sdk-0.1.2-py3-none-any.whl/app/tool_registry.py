"""
Tool Registry for Serialization/Deserialization

Provides mapping from tool names to classes and utilities for saving/loading
tool configurations to/from JSON.
"""

from typing import List, Dict, Any, Optional
from orchestral.tools import (
    RunCommandTool,
    DummyRunCommandTool,
    WriteFileTool,
    ReadFileTool,
    RunPythonTool,
    WebSearchTool,
    TodoRead,
    TodoWrite,
)
from orchestral.tools.filesystem.edit_file_tool import EditFileTool
from orchestral.tools.filesystem.file_search_tool import FileSearchTool
from orchestral.tools.base.tool import BaseTool


# Registry mapping tool names to their classes
TOOL_REGISTRY = {
    'RunCommandTool': RunCommandTool,
    'DummyRunCommandTool': DummyRunCommandTool,
    'WriteFileTool': WriteFileTool,
    'ReadFileTool': ReadFileTool,
    'EditFileTool': EditFileTool,
    'FileSearchTool': FileSearchTool,
    'RunPythonTool': RunPythonTool,
    'WebSearchTool': WebSearchTool,
    'TodoRead': TodoRead,
    'TodoWrite': TodoWrite,
}


def _is_json_serializable(value: Any) -> bool:
    """Check if a value can be JSON serialized."""
    import json
    try:
        json.dumps(value)
        return True
    except (TypeError, ValueError):
        return False


def serialize_tools(tools: List[BaseTool]) -> List[Dict[str, Any]]:
    """
    Convert tool instances to JSON-serializable format.

    Extracts tool class name and any StateField values that are JSON-serializable.
    Automatically excludes:
    - base_directory/working_directory (stored separately in metadata)
    - Non-serializable fields like agent_context (runtime state)

    Args:
        tools: List of tool instances

    Returns:
        List of dicts with 'name' and 'kwargs' keys
    """
    result = []

    for tool in tools:
        tool_name = tool.__class__.__name__
        kwargs = {}

        # Get StateFields from the tool class
        state_fields = tool._get_state_fields()

        # Extract only StateField values that are JSON-serializable
        for field_name in state_fields:
            # Skip directory fields - these are handled via base_directory in metadata
            if field_name in ['base_directory', 'working_directory']:
                continue

            field_value = getattr(tool, field_name, None)

            # Only include if value exists and is JSON-serializable
            if field_value is not None and _is_json_serializable(field_value):
                kwargs[field_name] = field_value

        result.append({
            "name": tool_name,
            "kwargs": kwargs
        })

    return result


def deserialize_tools(
    tools_data: List[Dict[str, Any]],
    base_directory: str,
    available_tools: Optional[List[BaseTool]] = None,
    conversation_id: Optional[str] = None
) -> List[BaseTool]:
    """
    Recreate tool instances from JSON data using introspection-based matching.

    Matches saved tools against available tools by class name. This eliminates the
    need to manually register custom tools defined with @define_tool.

    Args:
        tools_data: List of dicts with 'name' and 'kwargs' keys
        base_directory: Base directory to inject into file-related tools
        available_tools: List of tool instances available in current session.
                        Used to match saved tools by class name (introspection).
        conversation_id: Optional conversation ID to inject into tools that support it

    Returns:
        List of instantiated tool objects (intersection of saved and available)
    """
    tools = []

    # Build lookup from available tools by class name (case-insensitive)
    available_by_name = {}
    if available_tools:
        for tool in available_tools:
            # Use lowercase for case-insensitive matching
            available_by_name[tool.__class__.__name__.lower()] = tool.__class__

    for item in tools_data:
        tool_name = item["name"]

        # If available_tools provided, use strict intersection (only load what's available)
        # Otherwise fall back to TOOL_REGISTRY for backward compatibility
        if available_tools is not None:
            # Case-insensitive lookup
            tool_class = available_by_name.get(tool_name.lower())
        else:
            tool_class = TOOL_REGISTRY.get(tool_name)

        if not tool_class:
            if available_tools is not None:
                print(f"[Tool Registry] Warning: Tool '{tool_name}' not available in current session, skipping")
            else:
                print(f"[Tool Registry] Warning: Tool '{tool_name}' not found in registry, skipping")
            continue

        # Copy kwargs to avoid mutating the original
        kwargs = item.get("kwargs", {}).copy()

        # Filter out any RuntimeFields that may have been incorrectly saved
        # (this handles legacy tools.json files with RuntimeField values)
        runtime_fields = tool_class._get_runtime_fields()
        for field_name in runtime_fields:
            if field_name in kwargs:
                del kwargs[field_name]

        # Inject base_directory for tools that support it
        if hasattr(tool_class, 'model_fields') and 'base_directory' in tool_class.model_fields:
            kwargs['base_directory'] = base_directory

        # Inject conversation_id for tools that support it (StateField only)
        if conversation_id and hasattr(tool_class, 'model_fields') and 'conversation_id' in tool_class.model_fields:
            from orchestral.tools.base.field_utils import is_state_field
            field_info = tool_class.model_fields['conversation_id']
            if is_state_field(field_info):
                kwargs['conversation_id'] = conversation_id

        try:
            tools.append(tool_class(**kwargs))
        except Exception as e:
            print(f"[Tool Registry] Error instantiating {tool_name}: {e}")
            continue

    return tools


def register_custom_tool(name: str, tool_class: type):
    """
    Register a custom tool class.

    Args:
        name: Name to use for serialization (typically class name)
        tool_class: The tool class to register
    """
    TOOL_REGISTRY[name] = tool_class
    print(f"[Tool Registry] Registered custom tool: {name}")
