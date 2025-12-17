from orchestral.context.message import Message
from orchestral.llm.base.response import Response
from orchestral.llm.base.tool_call import ToolCall
from orchestral.llm.base.usage import Usage
from orchestral.llm.anthropic.pricing_model import pricing_model


def convert_message_to_anthropic(message: Message) -> dict:

    # Handle user, assistant messages:
    if message.role in {"user", "assistant"}:
        formatted_message = {
            'role': message.role,
            'content': [],
        }
        if message.text:
            formatted_message['content'].append({
                "type": "text",
                "text": message.text
            })

        if message.tool_calls:
            for call in message.tool_calls:
                formatted_message['content'].append({
                    "type": "tool_use",
                    "name": call.tool_name,
                    "id": call.id,    # Note that this is just called `id`, that is correct for Anthropic
                    "input": call.arguments    # Anthropic calls this `input` rather than `arguments`
                })

        return formatted_message
    
    elif message.role == "tool":
        # Handle tool result messages. We handle them one at a time! Technically Anthropic supports multiple tool results in one message but we don't use that feature.
        return {
            "role": "user", # Anthropic expects tool results to be from the 'user' role
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": message.tool_call_id,   # Note that this is called `tool_use_id` rather than `id`
                    "content": message.text
                }
            ]
        }

    elif message.role == "system":
        # System messages should be handled separately by the client
        # They should not reach this function
        raise ValueError("System messages must be handled separately by the client, not passed to convert_message_to_anthropic")

    else:
        raise ValueError(f"Invalid role: {message.role}")


def parse_anthropic_response(api_response, model_name: str) -> Response:
    
    # Handle different content types (text blocks, tool use blocks, etc.)
    text_content = ""
    tool_calls = []
    
    for content_block in api_response.content:
        if hasattr(content_block, 'text'):
            # Text block
            text_content += content_block.text
        elif hasattr(content_block, 'name'):
            # Tool use block
            # tool_calls.append(content_block)
            tool_call = ToolCall(
                id=content_block.id,
                tool_name=content_block.name,
                arguments=content_block.input
            )
            tool_calls.append(tool_call)
    
    message = Message(
        text=text_content or None,
        role=api_response.role,
        tool_calls=tool_calls if tool_calls else None
    )

    usage = parse_anthropic_usage(api_response.usage, model_name)

    return Response(
        id=api_response.id,
        model=model_name,
        message_choices=[message],
        usage=usage
    )

def parse_anthropic_usage(usage, model_name: str) -> Usage:

    usage_tokens = {
        'prompt_tokens': usage.input_tokens,
        'completion_tokens': usage.output_tokens
    }

    # Add cache-specific tokens if present (only when prompt caching is enabled)
    cache_creation = 0
    cache_read = 0

    if hasattr(usage, 'cache_creation_input_tokens') and usage.cache_creation_input_tokens:
        usage_tokens['cache_creation_input_tokens'] = usage.cache_creation_input_tokens
        cache_creation = usage.cache_creation_input_tokens

    if hasattr(usage, 'cache_read_input_tokens') and usage.cache_read_input_tokens:
        usage_tokens['cache_read_input_tokens'] = usage.cache_read_input_tokens
        cache_read = usage.cache_read_input_tokens

    # Add total_tokens for cross-provider compatibility
    usage_tokens['total_tokens'] = usage.input_tokens + cache_creation + cache_read + usage.output_tokens

    cost = pricing_model.get_cost(usage_tokens, model_name=model_name)

    return Usage(
        model_name=model_name,
        tokens=usage_tokens,
        cost=cost
    )