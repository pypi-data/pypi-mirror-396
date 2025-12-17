from orchestral.context.message import Message
from orchestral.llm.base.response import Response
from orchestral.llm.base.tool_call import ToolCall
from orchestral.llm.base.usage import Usage
from orchestral.llm.openai.pricing_model import pricing_model
import json


def convert_message_to_openai(message: Message) -> dict:
    
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
                        'arguments': json.dumps(call.arguments)  # Convert dict back to JSON string for OpenAI
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


def parse_openai_response(api_response, model_name: str) -> Response:

    # Parse message choices
    message_choices = []
    for choice in api_response.choices:
        # dict_keys(['content', 'refusal', 'role', 'annotations', 'audio', 'function_call', 'tool_calls'])
        role = choice.message.role
        text = choice.message.content
        refusal = choice.message.refusal
        annotations = choice.message.annotations
        audio = choice.message.audio
        function_call = choice.message.function_call

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
    usage = parse_openai_usage(api_response.usage, model_name)

    return Response(
        id=api_response.id,
        model=api_response.model,
        message_choices=message_choices, 
        usage=usage
    )


def parse_openai_usage(usage, model_name) -> Usage:

    usage_tokens = {
        'completion_tokens': usage.completion_tokens,
        'prompt_tokens': usage.prompt_tokens,
        'total_tokens': usage.total_tokens,
        'accepted_prediction_tokens': usage.completion_tokens_details.accepted_prediction_tokens,
        'rejected_prediction_tokens': usage.completion_tokens_details.rejected_prediction_tokens,
        'audio_tokens': usage.completion_tokens_details.audio_tokens,
        'reasoning_tokens': usage.completion_tokens_details.reasoning_tokens
    }

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