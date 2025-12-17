"""
Tool schema conversion for AWS Bedrock.

Different model families on Bedrock use different tool schema formats.
"""

from typing import Dict, Any
from orchestral.tools.base.tool_spec import ToolSpec


def convert_tool_to_bedrock_claude(tool_spec: ToolSpec) -> Dict[str, Any]:
    """
    Convert ToolSpec to Bedrock's Claude format.

    Claude models on Bedrock use the same format as the direct Anthropic API.
    """
    return {
        "name": tool_spec.name,
        "description": tool_spec.description,
        "input_schema": tool_spec.input_schema
    }


def convert_tool_to_bedrock_cohere(tool_spec: ToolSpec) -> Dict[str, Any]:
    """
    Convert ToolSpec to Bedrock's Cohere format.

    Cohere uses a different format with 'parameter_definitions'.
    """
    # Cohere uses a different schema format
    parameter_definitions = {}

    if 'properties' in tool_spec.input_schema:
        for prop_name, prop_schema in tool_spec.input_schema['properties'].items():
            parameter_definitions[prop_name] = {
                'description': prop_schema.get('description', ''),
                'type': prop_schema.get('type', 'string'),
                'required': prop_name in tool_spec.input_schema.get('required', [])
            }

    return {
        "name": tool_spec.name,
        "description": tool_spec.description,
        "parameter_definitions": parameter_definitions
    }


def convert_tool_to_bedrock(tool_spec: ToolSpec, model_family: str) -> Dict[str, Any]:
    """
    Convert ToolSpec to the appropriate Bedrock format based on model family.

    Args:
        tool_spec: The tool specification to convert
        model_family: The model family ('claude', 'cohere', 'llama', 'mistral', 'titan')

    Returns:
        Tool schema in the appropriate format for the model family
    """
    if model_family == 'claude':
        return convert_tool_to_bedrock_claude(tool_spec)
    elif model_family == 'cohere':
        return convert_tool_to_bedrock_cohere(tool_spec)
    elif model_family in ['llama', 'mistral']:
        # Llama and Mistral use similar format to Claude (JSON schema)
        return convert_tool_to_bedrock_claude(tool_spec)
    elif model_family == 'titan':
        # Titan doesn't support tool calling
        raise ValueError(f"Tool calling is not supported for Titan models")
    else:
        # Default to Claude format for unknown families
        return convert_tool_to_bedrock_claude(tool_spec)
