from orchestral.context.message import Message
from orchestral.llm.base.response import Response
from orchestral.llm.base.tool_call import ToolCall
from orchestral.llm.base.usage import Usage
from orchestral.llm.groq.pricing_model import pricing_model
import json


def convert_message_to_groq(message: Message) -> dict:
    
    # Handle user, assistant, system messages:
    if message.role in {"user", "assistant", "system"}:
        formatted_message = {'role': message.role}
        if message.text:
            formatted_message['content'] = message.text

        if message.tool_calls:
            formatted_message['tool_calls'] = [
                {
                    'id': call.id,
                    "type": "function",
                    'function': {
                        'name': call.tool_name,
                        'arguments': json.dumps(call.arguments)  # Convert dict back to JSON string for Groq
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


def parse_groq_response(api_response, model_name: str) -> Response:

    # Parse message choices
    message_choices = []
    for choice in api_response.choices:
        # Groq's ChatCompletionMessage has: content, role, tool_calls, function_call
        # It does NOT have: refusal, annotations, audio (those are OpenAI-specific)
        role = choice.message.role
        text = choice.message.content
        refusal = getattr(choice.message, 'refusal', None)
        annotations = getattr(choice.message, 'annotations', None)
        audio = getattr(choice.message, 'audio', None)
        function_call = getattr(choice.message, 'function_call', None)

        # Parse tool calls
        tool_calls = choice.message.tool_calls # This is None if there are no tool calls, but if there are tool calls then it needs to be parsed.
        if tool_calls:
            tool_calls = parse_tool_calls(tool_calls)

        # Package into Message object
        message=Message(
            text=text,
            role=role,
            refusal=refusal,
            annotations=annotations,
            audio=audio,
            function_call=function_call,
            tool_calls=tool_calls
        )
        message_choices.append(message)

    # Parse usage
    usage = parse_groq_usage(api_response.usage, model_name)

    return Response(
        id=api_response.id,
        model=api_response.model,
        message_choices=message_choices, 
        usage=usage
    )


def parse_groq_usage(usage, model_name) -> Usage:

    # Groq usage has: completion_tokens, prompt_tokens, total_tokens
    # It does NOT have: completion_tokens_details (OpenAI-specific)
    usage_tokens = {
        'completion_tokens': usage.completion_tokens,
        'prompt_tokens': usage.prompt_tokens,
        'total_tokens': usage.total_tokens,
    }

    # Add cached tokens if available (Groq may add this in the future)
    if hasattr(usage, 'prompt_tokens_details'):
        usage_tokens['cached_prompt_tokens'] = usage.prompt_tokens_details.get('cached_tokens', 0)

    cost = pricing_model.get_cost(usage_tokens, model_name=model_name)

    return Usage(
        model_name=model_name,
        tokens=usage_tokens,
        cost=cost
    )


def parse_tool_calls(tool_calls) -> list:
    parsed_calls = []
    for call in tool_calls:
        tool_call = ToolCall(
            id=call.id,
            tool_name=call.function.name,
            arguments=json.loads(call.function.arguments)  # Parse JSON string to dict
        )
        parsed_calls.append(tool_call)
    return parsed_calls