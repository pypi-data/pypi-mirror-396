from orchestral.context.message import Message
from orchestral.llm.base.response import Response
from orchestral.llm.base.tool_call import ToolCall
from orchestral.llm.base.usage import Usage
from orchestral.llm.google.pricing_model import pricing_model
import google.generativeai as genai


def convert_message_to_gemini(message: Message) -> dict:
    """
    Convert a Message to Gemini's format.

    Gemini uses a parts-based structure where each message has:
    - role: "user" or "model" (not "assistant")
    - parts: list of content parts (text, function_call, function_response)
    """

    # Map assistant role to model for Gemini
    role = "model" if message.role == "assistant" else message.role

    # Handle user, assistant/model messages:
    if message.role in {"user", "assistant"}:
        parts = []

        if message.text:
            parts.append({"text": message.text})

        if message.tool_calls:
            for call in message.tool_calls:
                parts.append({
                    "function_call": {
                        "name": call.tool_name,
                        "args": call.arguments
                    }
                })

        return {
            "role": role,
            "parts": parts
        }

    elif message.role == "tool":
        # Handle tool result messages
        # Gemini expects tool results as function_response in user messages
        # Extract function name from tool_call_id (format: "toolname_0", "toolname_1", etc.)
        # If no underscore, use the whole ID as the function name
        function_name = message.tool_call_id.rsplit('_', 1)[0] if '_' in message.tool_call_id else message.tool_call_id

        return {
            "role": "user",
            "parts": [{
                "function_response": {
                    "name": function_name,
                    "response": {
                        "result": message.text
                    }
                }
            }]
        }

    elif message.role == "system":
        # System messages should be handled separately by the client
        # They should not reach this function
        raise ValueError("System messages must be handled separately by the client, not passed to convert_message_to_gemini")

    else:
        raise ValueError(f"Invalid role: {message.role}")


def parse_gemini_response(api_response, model_name: str) -> Response:
    """
    Parse Gemini API response into unified Response object.

    Gemini responses have:
    - candidates: list of response candidates
    - Each candidate has parts (text, function_call)
    - usage_metadata: token counts
    """

    # Get the first candidate (most common case)
    if not api_response.candidates:
        # Handle empty response
        message = Message(text=None, role='model', tool_calls=None)
        usage = Usage(
            model_name=model_name,
            tokens={},
            cost=0.0
        )
        return Response(
            id=None,
            model=model_name,
            message_choices=[message],
            usage=usage
        )

    candidate = api_response.candidates[0]

    # Extract text and tool calls from parts
    text_content = ""
    tool_calls = []
    tool_call_counter = {}  # Track calls per tool name for unique IDs

    if hasattr(candidate.content, 'parts'):
        for part in candidate.content.parts:
            # Check for text
            if hasattr(part, 'text') and part.text:
                text_content += part.text

            # Check for function call
            if hasattr(part, 'function_call') and part.function_call:
                fc = part.function_call

                # Generate unique ID: Gemini doesn't provide IDs, so we create them
                # Format: toolname_0, toolname_1, etc. for multiple calls to same tool
                count = tool_call_counter.get(fc.name, 0)
                tool_call_counter[fc.name] = count + 1
                unique_id = f"{fc.name}_{count}"

                tool_call = ToolCall(
                    id=unique_id,
                    tool_name=fc.name,
                    arguments=dict(fc.args) if fc.args else {}
                )
                tool_calls.append(tool_call)

    # Create message
    message = Message(
        text=text_content or None,
        role='assistant',  # Map back to assistant from model
        tool_calls=tool_calls if tool_calls else None
    )

    # Parse usage
    usage = parse_gemini_usage(api_response.usage_metadata, model_name)

    return Response(
        id=None,  # Gemini doesn't provide response IDs
        model=model_name,
        message_choices=[message],
        usage=usage
    )


def parse_gemini_usage(usage_metadata, model_name: str) -> Usage:
    """
    Parse Gemini usage metadata into Usage object.

    Gemini provides:
    - prompt_token_count
    - candidates_token_count
    - total_token_count
    """

    if not usage_metadata:
        usage_tokens = {}
    else:
        usage_tokens = {
            'prompt_tokens': getattr(usage_metadata, 'prompt_token_count', 0),
            'completion_tokens': getattr(usage_metadata, 'candidates_token_count', 0),
            'total_tokens': getattr(usage_metadata, 'total_token_count', 0),
        }

    cost = pricing_model.get_cost(usage_tokens, model_name=model_name)

    return Usage(
        model_name=model_name,
        tokens=usage_tokens,
        cost=cost
    )
