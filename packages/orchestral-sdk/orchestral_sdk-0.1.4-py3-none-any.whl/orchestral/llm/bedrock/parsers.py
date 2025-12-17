"""
Message conversion and response parsing for AWS Bedrock.

Handles different message formats for different model families:
- Claude: Uses Anthropic's format
- Llama/Mistral: Uses chat completion format
- Cohere: Uses Cohere's format
- Titan: Uses Amazon's format
"""

import json
from typing import Dict, Any, List
from orchestral.context.message import Message
from orchestral.llm.base.response import Response
from orchestral.llm.base.tool_call import ToolCall
from orchestral.llm.base.usage import Usage
from orchestral.llm.bedrock.pricing_model import pricing_model


def convert_message_to_bedrock_claude(message: Message) -> Dict[str, Any]:
    """
    Convert Message to Bedrock Claude format.

    Claude models use the same format as direct Anthropic API.
    """
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
                    "id": call.id,
                    "input": call.arguments
                })

        return formatted_message

    elif message.role == "tool":
        # Claude expects tool results as user messages
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": message.tool_call_id,
                    "content": message.text
                }
            ]
        }

    elif message.role == "system":
        raise ValueError("System messages must be handled separately by the client")

    else:
        raise ValueError(f"Invalid role: {message.role}")


def convert_message_to_bedrock_llama(message: Message) -> Dict[str, Any]:
    """
    Convert Message to Bedrock Llama format.

    Llama uses a simpler chat completion format.
    """
    if message.role == "system":
        return {
            "role": "system",
            "content": message.text
        }
    elif message.role == "user":
        return {
            "role": "user",
            "content": message.text or ""
        }
    elif message.role == "assistant":
        return {
            "role": "assistant",
            "content": message.text or ""
        }
    elif message.role == "tool":
        # Llama doesn't have native tool support, format as user message
        return {
            "role": "user",
            "content": f"Tool result: {message.text}"
        }
    else:
        raise ValueError(f"Invalid role: {message.role}")


def convert_message_to_bedrock_mistral(message: Message) -> Dict[str, Any]:
    """
    Convert Message to Bedrock Mistral format.

    Mistral uses a similar format to standard chat completions.
    """
    # Mistral is similar to Llama for basic messages
    return convert_message_to_bedrock_llama(message)


def convert_message_to_bedrock_cohere(message: Message) -> Dict[str, Any]:
    """
    Convert Message to Bedrock Cohere format.

    Cohere uses a different message structure.
    """
    if message.role == "system":
        # Cohere handles system messages separately
        return {
            "role": "SYSTEM",
            "message": message.text
        }
    elif message.role == "user":
        return {
            "role": "USER",
            "message": message.text or ""
        }
    elif message.role == "assistant":
        return {
            "role": "CHATBOT",
            "message": message.text or ""
        }
    elif message.role == "tool":
        # Cohere tool results
        return {
            "role": "USER",
            "message": f"Tool result: {message.text}"
        }
    else:
        raise ValueError(f"Invalid role: {message.role}")


def convert_message_to_bedrock(message: Message, model_family: str) -> Dict[str, Any]:
    """
    Convert Message to appropriate Bedrock format based on model family.

    Args:
        message: The message to convert
        model_family: The model family ('claude', 'llama', 'mistral', 'cohere', 'titan')

    Returns:
        Message in the appropriate format for the model family
    """
    if model_family == 'claude':
        return convert_message_to_bedrock_claude(message)
    elif model_family == 'llama':
        return convert_message_to_bedrock_llama(message)
    elif model_family == 'mistral':
        return convert_message_to_bedrock_mistral(message)
    elif model_family == 'cohere':
        return convert_message_to_bedrock_cohere(message)
    elif model_family == 'titan':
        return convert_message_to_bedrock_llama(message)  # Titan uses simple format
    else:
        # Default to Claude format
        return convert_message_to_bedrock_claude(message)


def parse_bedrock_claude_response(body: Dict[str, Any], model_name: str) -> Response:
    """
    Parse Bedrock Claude response.

    Claude responses match the Anthropic API format.
    """
    text_content = ""
    tool_calls = []

    for content_block in body.get('content', []):
        if content_block.get('type') == 'text':
            text_content += content_block.get('text', '')
        elif content_block.get('type') == 'tool_use':
            tool_call = ToolCall(
                id=content_block.get('id'),
                tool_name=content_block.get('name'),
                arguments=content_block.get('input', {})
            )
            tool_calls.append(tool_call)

    message = Message(
        text=text_content or None,
        role=body.get('role', 'assistant'),
        tool_calls=tool_calls if tool_calls else None
    )

    # Parse usage
    usage_data = body.get('usage', {})
    usage = parse_bedrock_usage(usage_data, model_name)

    return Response(
        id=body.get('id', 'bedrock-response'),
        model=model_name,
        message_choices=[message],
        usage=usage
    )


def parse_bedrock_llama_response(body: Dict[str, Any], model_name: str) -> Response:
    """
    Parse Bedrock Llama response.

    Llama responses have generation, prompt_token_count, and generation_token_count.
    """
    text_content = body.get('generation', '')

    message = Message(
        text=text_content,
        role='assistant',
        tool_calls=None
    )

    # Parse usage
    usage_tokens = {
        'prompt_tokens': body.get('prompt_token_count', 0),
        'completion_tokens': body.get('generation_token_count', 0),
    }
    usage_tokens['total_tokens'] = usage_tokens['prompt_tokens'] + usage_tokens['completion_tokens']

    cost = pricing_model.get_cost(usage_tokens, model_name=model_name)
    usage = Usage(
        model_name=model_name,
        tokens=usage_tokens,
        cost=cost
    )

    return Response(
        id='bedrock-llama-response',
        model=model_name,
        message_choices=[message],
        usage=usage
    )


def parse_bedrock_mistral_response(body: Dict[str, Any], model_name: str) -> Response:
    """
    Parse Bedrock Mistral response.

    Mistral responses have outputs array with text field.
    """
    outputs = body.get('outputs', [])
    text_content = outputs[0].get('text', '') if outputs else ''

    message = Message(
        text=text_content,
        role='assistant',
        tool_calls=None
    )

    # Parse usage
    usage_tokens = {
        'prompt_tokens': body.get('prompt_token_count', 0),
        'completion_tokens': body.get('generation_token_count', 0),
    }
    usage_tokens['total_tokens'] = usage_tokens['prompt_tokens'] + usage_tokens['completion_tokens']

    cost = pricing_model.get_cost(usage_tokens, model_name=model_name)
    usage = Usage(
        model_name=model_name,
        tokens=usage_tokens,
        cost=cost
    )

    return Response(
        id='bedrock-mistral-response',
        model=model_name,
        message_choices=[message],
        usage=usage
    )


def parse_bedrock_cohere_response(body: Dict[str, Any], model_name: str) -> Response:
    """
    Parse Bedrock Cohere response.

    Cohere responses have text field and token counts.
    """
    text_content = body.get('text', '')

    message = Message(
        text=text_content,
        role='assistant',
        tool_calls=None
    )

    # Parse usage
    usage_tokens = {
        'prompt_tokens': body.get('prompt_token_count', 0),
        'completion_tokens': body.get('generation_token_count', 0),
    }
    usage_tokens['total_tokens'] = usage_tokens['prompt_tokens'] + usage_tokens['completion_tokens']

    cost = pricing_model.get_cost(usage_tokens, model_name=model_name)
    usage = Usage(
        model_name=model_name,
        tokens=usage_tokens,
        cost=cost
    )

    return Response(
        id=body.get('generation_id', 'bedrock-cohere-response'),
        model=model_name,
        message_choices=[message],
        usage=usage
    )


def parse_bedrock_titan_response(body: Dict[str, Any], model_name: str) -> Response:
    """
    Parse Bedrock Titan response.

    Titan responses have results array with outputText.
    """
    results = body.get('results', [])
    text_content = results[0].get('outputText', '') if results else ''

    message = Message(
        text=text_content,
        role='assistant',
        tool_calls=None
    )

    # Parse usage
    usage_tokens = {
        'prompt_tokens': body.get('inputTextTokenCount', 0),
        'completion_tokens': results[0].get('tokenCount', 0) if results else 0,
    }
    usage_tokens['total_tokens'] = usage_tokens['prompt_tokens'] + usage_tokens['completion_tokens']

    cost = pricing_model.get_cost(usage_tokens, model_name=model_name)
    usage = Usage(
        model_name=model_name,
        tokens=usage_tokens,
        cost=cost
    )

    return Response(
        id='bedrock-titan-response',
        model=model_name,
        message_choices=[message],
        usage=usage
    )


def parse_bedrock_response(api_response: Dict[str, Any], model_name: str, model_family: str) -> Response:
    """
    Parse Bedrock API response based on model family.

    Args:
        api_response: The raw Bedrock API response (already parsed from JSON)
        model_name: The model name/ID
        model_family: The model family ('claude', 'llama', 'mistral', 'cohere', 'titan')

    Returns:
        Unified Response object
    """
    # api_response is the parsed JSON body from Bedrock
    body = api_response.get('body') if isinstance(api_response, dict) and 'body' in api_response else api_response

    if model_family == 'claude':
        return parse_bedrock_claude_response(body, model_name)
    elif model_family == 'llama':
        return parse_bedrock_llama_response(body, model_name)
    elif model_family == 'mistral':
        return parse_bedrock_mistral_response(body, model_name)
    elif model_family == 'cohere':
        return parse_bedrock_cohere_response(body, model_name)
    elif model_family == 'titan':
        return parse_bedrock_titan_response(body, model_name)
    else:
        # Default to Claude parser
        return parse_bedrock_claude_response(body, model_name)


def parse_bedrock_usage(usage_data: Dict[str, Any], model_name: str) -> Usage:
    """
    Parse usage data from Bedrock response.

    Args:
        usage_data: Usage dictionary from API response
        model_name: The model name for cost calculation

    Returns:
        Usage object with token counts and cost
    """
    usage_tokens = {
        'prompt_tokens': usage_data.get('input_tokens', 0),
        'completion_tokens': usage_data.get('output_tokens', 0),
    }
    usage_tokens['total_tokens'] = usage_tokens['prompt_tokens'] + usage_tokens['completion_tokens']

    cost = pricing_model.get_cost(usage_tokens, model_name=model_name)

    return Usage(
        model_name=model_name,
        tokens=usage_tokens,
        cost=cost
    )
