from typing import Dict, Any
from orchestral.tools.base.tool_spec import ToolSpec


def convert_tool_to_openai(tool_spec: ToolSpec) -> Dict[str, Any]:
    """Convert ToolSpec to OpenAI's tool format."""
    return {
        "type": "function",
        "function": {
            "name": tool_spec.name,
            "description": tool_spec.description,
            "parameters": tool_spec.input_schema
        }
    }