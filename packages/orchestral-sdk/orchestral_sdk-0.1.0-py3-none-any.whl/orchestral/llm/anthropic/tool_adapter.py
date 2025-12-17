from typing import Dict, Any
from orchestral.tools.base.tool_spec import ToolSpec


def convert_tool_to_anthropic(tool_spec: ToolSpec) -> Dict[str, Any]:
    """Convert ToolSpec to Anthropic's tool format."""
    return {
        "name": tool_spec.name,
        "description": tool_spec.description,
        "input_schema": tool_spec.input_schema
    }