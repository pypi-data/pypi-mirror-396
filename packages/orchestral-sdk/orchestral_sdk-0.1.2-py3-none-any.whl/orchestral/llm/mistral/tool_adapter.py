"""
Tool adapter for Mistral AI.

Converts Orchestral tool specifications to Mistral's function calling format.
Mistral uses OpenAI-compatible tool format.
"""

from typing import Dict, Any
from orchestral.tools.base.tool_spec import ToolSpec


def convert_tool_to_mistral(tool_spec: ToolSpec) -> Dict[str, Any]:
    """
    Convert ToolSpec to Mistral's tool format.

    Mistral uses OpenAI-compatible function calling format:
    {
        "type": "function",
        "function": {
            "name": "...",
            "description": "...",
            "parameters": {...}
        }
    }

    Args:
        tool_spec: Orchestral tool specification

    Returns:
        Dictionary in Mistral's expected format
    """
    return {
        "type": "function",
        "function": {
            "name": tool_spec.name,
            "description": tool_spec.description,
            "parameters": tool_spec.input_schema
        }
    }
