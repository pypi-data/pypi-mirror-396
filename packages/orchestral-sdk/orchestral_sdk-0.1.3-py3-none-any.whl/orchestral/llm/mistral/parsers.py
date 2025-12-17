"""
Parsers for Mistral AI API responses.

Converts between Mistral's format and Orchestral's internal format.
Mistral uses OpenAI-compatible format with minor differences.
"""

from orchestral.context.message import Message
from orchestral.llm.base.response import Response
from orchestral.llm.base.tool_call import ToolCall
from orchestral.llm.base.usage import Usage
from orchestral.llm.mistral.pricing_model import get_pricing_model
import json


def convert_message_to_mistral(message: Message) -> dict:
    """
    Convert Orchestral Message to Mistral format.

    Mistral uses OpenAI-compatible message format:
    - User/Assistant/System messages: {"role": "...", "content": "..."}
    - Tool calls: {"role": "assistant", "tool_calls": [...]}
    - Tool results: {"role": "tool", "content": "...", "tool_call_id": "..."}

    Args:
        message: Orchestral Message object

    Returns:
        Dictionary in Mistral's expected format
    """
    # Handle user, assistant, system messages
    if message.role in {"user", "assistant", "system"}:
        formatted_message = {'role': message.role}

        if message.text:
            formatted_message['content'] = message.text

        # Add tool calls if present
        if message.tool_calls:
            formatted_message['tool_calls'] = [
                {
                    'id': call.id,
                    'type': 'function',
                    'function': {
                        'name': call.tool_name,
                        'arguments': json.dumps(call.arguments)  # Mistral expects JSON string
                    }
                } for call in message.tool_calls
            ]

        return formatted_message

    elif message.role == "tool":
        # Handle tool result messages
        return {
            "role": "tool",
            "content": message.text,
            "tool_call_id": message.tool_call_id
        }

    else:
        raise ValueError(f"Invalid role: {message.role}")


def parse_mistral_response(api_response, model_name: str) -> Response:
    """
    Parse Mistral API response into Orchestral Response object.

    Args:
        api_response: Raw response from Mistral API
        model_name: The model identifier

    Returns:
        Response object with parsed data
    """
    # Parse message choices
    message_choices = []
    for choice in api_response.choices:
        role = choice.message.role
        text = choice.message.content

        # Parse tool calls if present
        tool_calls = None
        if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
            tool_calls = parse_tool_calls(choice.message.tool_calls)

        # Package into Message object
        message = Message(
            text=text,
            role=role,
            tool_calls=tool_calls
        )
        message_choices.append(message)

    # Parse usage
    usage = parse_mistral_usage(api_response.usage, model_name)

    return Response(
        id=api_response.id,
        model=api_response.model,
        message_choices=message_choices,
        usage=usage
    )


def parse_mistral_usage(usage, model_name: str) -> Usage:
    """
    Parse usage information from Mistral response.

    Mistral usage format:
    {
        "prompt_tokens": int,
        "completion_tokens": int,
        "total_tokens": int
    }

    Args:
        usage: Usage object from Mistral response
        model_name: The model identifier for pricing lookup

    Returns:
        Usage object with cost calculation
    """
    usage_tokens = {
        'prompt_tokens': usage.prompt_tokens,
        'completion_tokens': usage.completion_tokens,
        'total_tokens': usage.total_tokens,
    }

    # Get pricing model and calculate cost
    pricing_model = get_pricing_model(model_name)
    cost = pricing_model.get_cost(usage_tokens, model_name=model_name)

    return Usage(
        model_name=model_name,
        tokens=usage_tokens,
        cost=cost
    )


def parse_tool_calls(tool_calls) -> list:
    """
    Parse tool calls from Mistral response.

    Mistral tool call format (OpenAI-compatible):
    {
        "id": "...",
        "type": "function",
        "function": {
            "name": "...",
            "arguments": "..." (JSON string)
        }
    }

    Args:
        tool_calls: List of tool call objects from Mistral

    Returns:
        List of ToolCall objects
    """
    parsed_calls = []
    for call in tool_calls:
        tool_call = ToolCall(
            id=call.id,
            tool_name=call.function.name,
            arguments=json.loads(call.function.arguments)  # Parse JSON string to dict
        )
        parsed_calls.append(tool_call)
    return parsed_calls
