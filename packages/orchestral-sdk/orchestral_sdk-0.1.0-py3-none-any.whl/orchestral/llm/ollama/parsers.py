from orchestral.context.message import Message
from orchestral.llm.base.response import Response
from orchestral.llm.base.tool_call import ToolCall
from orchestral.llm.base.usage import Usage
from orchestral.llm.ollama.pricing_model import pricing_model
import json


def convert_message_to_ollama(message: Message) -> dict:
    """Convert orchestral Message to Ollama format."""

    # Handle user, assistant, system messages:
    if message.role in {"user", "assistant", "system"}:
        formatted_message = {'role': message.role}

        if message.text:
            formatted_message['content'] = message.text
        elif not message.tool_calls:
            # If there's no text and no tool calls, this is likely an interrupted/empty message
            # Ollama requires content field, so provide empty string
            formatted_message['content'] = ""

        # Ollama uses the same tool_calls format as OpenAI
        if message.tool_calls:
            formatted_message['tool_calls'] = [
                {
                    'id': call.id,
                    "type": "function",
                    'function': {
                        'name': call.tool_name,
                        'arguments': call.arguments  # Ollama accepts dict directly (not JSON string)
                    }
                } for call in message.tool_calls
            ]

        return formatted_message

    elif message.role == "tool":
        # Handle tool result messages - Ollama uses same format as OpenAI
        return {
            "role": "tool",
            "content": message.text,
            "tool_call_id": message.tool_call_id
        }

    else:
        raise ValueError(f"Invalid role: {message.role}")


def parse_ollama_response(api_response, model_name: str) -> Response:
    """Parse non-streaming Ollama ChatResponse to orchestral Response."""

    # Ollama returns a single message, not choices
    message_obj = api_response.message

    role = message_obj.role
    text = message_obj.content if message_obj.content else None

    # Extract reasoning/thinking if present
    reasoning = None
    if hasattr(message_obj, 'thinking') and message_obj.thinking:
        # Skip the 'None' string that appears in final chunks
        if message_obj.thinking != 'None':
            reasoning = message_obj.thinking

    # Parse tool calls if present
    tool_calls = None
    if message_obj.tool_calls:
        tool_calls = parse_tool_calls(message_obj.tool_calls)

    # Package into Message object
    message = Message(
        text=text,
        reasoning=reasoning,
        role=role,
        tool_calls=tool_calls
    )

    # Parse usage
    usage = parse_ollama_usage(api_response, model_name)

    return Response(
        id=api_response.created_at,  # Ollama uses timestamp as ID
        model=api_response.model,
        message_choices=[message],  # Single message wrapped in list for consistency
        usage=usage
    )


def parse_ollama_usage(api_response, model_name: str) -> Usage:
    """Parse Ollama usage information to orchestral Usage."""

    # Ollama provides token counts directly on the response object
    usage_tokens = {
        'prompt_tokens': api_response.prompt_eval_count or 0,
        'completion_tokens': api_response.eval_count or 0,
        'total_tokens': (api_response.prompt_eval_count or 0) + (api_response.eval_count or 0)
    }

    # Calculate cost (likely $0 for local models)
    cost = pricing_model.get_cost(usage_tokens, model_name=model_name)

    return Usage(
        model_name=model_name,
        tokens=usage_tokens,
        cost=cost
    )


def parse_tool_calls(tool_calls) -> list:
    """Parse Ollama tool calls to orchestral ToolCall objects."""
    parsed_calls = []

    for i, call in enumerate(tool_calls):
        # Ollama doesn't provide IDs for tool calls, so we generate them
        tool_call_id = f"call_{i}"

        tool_call = ToolCall(
            id=tool_call_id,
            tool_name=call.function.name,
            arguments=call.function.arguments  # Already a dict, not JSON string
        )
        parsed_calls.append(tool_call)

    return parsed_calls
