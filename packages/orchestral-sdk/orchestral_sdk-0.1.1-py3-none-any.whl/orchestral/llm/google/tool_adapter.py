from typing import Dict, Any
from orchestral.tools.base.tool_spec import ToolSpec


def convert_tool_to_gemini(tool_spec: ToolSpec) -> Dict[str, Any]:
    """
    Convert ToolSpec to Gemini's tool format.

    Gemini uses a function declaration format similar to OpenAI but with
    'parameters' instead of 'input_schema' at the top level.
    """
    return {
        "function_declarations": [{
            "name": tool_spec.name,
            "description": tool_spec.description,
            "parameters": tool_spec.input_schema
        }]
    }
