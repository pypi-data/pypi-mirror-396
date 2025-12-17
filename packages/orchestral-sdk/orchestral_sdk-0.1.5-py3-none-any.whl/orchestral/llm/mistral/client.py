"""
Mistral AI client implementation for Orchestral framework.

Provides unified interface to Mistral AI models with full streaming
and tool calling support.
"""

from orchestral.llm.base.llm import LLM
from orchestral.context.message import Message
from orchestral.context.context import Context
from orchestral.llm.base.response import Response
from orchestral.llm.mistral.parsers import (
    convert_message_to_mistral, parse_mistral_response, parse_mistral_usage)
from orchestral.llm.mistral.tool_adapter import convert_tool_to_mistral

import os
from typing import Optional
from mistralai import Mistral
from dotenv import load_dotenv


class MistralAI(LLM):
    """
    Mistral AI provider implementation.

    Supports all Mistral models including:
    - Mistral Large (mistral-large-latest)
    - Mistral Small (mistral-small-latest)
    - Mistral NeMo (open-mistral-nemo)
    - Codestral (codestral-latest)
    - Open Mistral family (7B, 8x7B, 8x22B)

    Example:
        >>> from orchestral.llm import MistralAI
        >>> llm = MistralAI(model='mistral-large-latest')
        >>> response = llm.get_response(context)
    """

    def __init__(
        self,
        model: str = 'mistral-small-latest',
        api_key: Optional[str] = None,
        tools=None
    ):
        """
        Initialize Mistral client.

        Args:
            model: Mistral model identifier (default: mistral-small-latest)
            api_key: Mistral API key (if None, loads from MISTRAL_API_KEY env var)
            tools: List of tools to make available to the model
        """
        super().__init__(tools=tools)

        self.model = model
        self.load_api_key(api_key)
        self.client = Mistral(api_key=self.api_key)

    # Preparation
    def load_api_key(self, api_key: Optional[str] = None):
        """Load API key from argument or environment variable."""
        if api_key:
            self.api_key = api_key
        else:
            load_dotenv()
            self.api_key = os.getenv("MISTRAL_API_KEY")

        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY must be provided either as an argument "
                "or via the MISTRAL_API_KEY environment variable."
            )

    def process_api_input(self, context: Context):
        """Convert Context to Mistral message format."""
        return [convert_message_to_mistral(msg) for msg in context.get_messages()]

    def _convert_tools_to_provider_format(self):
        """Convert tools to Mistral's function calling format."""
        return [convert_tool_to_mistral(tool.get_tool_spec()) for tool in self.tools]

    # API calls
    def call_api(self, formatted_input, use_prompt_cache=False, **kwargs):
        """
        Make non-streaming API call to Mistral.

        Args:
            formatted_input: Messages in Mistral format
            use_prompt_cache: Ignored (Mistral doesn't support prompt caching)
            **kwargs: Additional parameters for the API call

        Returns:
            Raw API response from Mistral
        """
        call_params = {
            "model": self.model,
            "messages": formatted_input,
            **kwargs
        }

        # Add tools if provided
        if self.tool_schemas:
            call_params["tools"] = self.tool_schemas

        api_response = self.client.chat.complete(**call_params)
        return api_response

    def call_streaming_api(self, formatted_input, use_prompt_cache=False, **kwargs):
        """
        Make streaming API call to Mistral.

        Args:
            formatted_input: Messages in Mistral format
            use_prompt_cache: Ignored (Mistral doesn't support prompt caching)
            **kwargs: Additional parameters for the API call

        Returns:
            Streaming response iterator
        """
        call_params = {
            "model": self.model,
            "messages": formatted_input,
            **kwargs
        }

        # Add tools if provided
        if self.tool_schemas:
            call_params["tools"] = self.tool_schemas

        streaming_response = self.client.chat.stream(**call_params)
        return streaming_response

    # Response processing
    def process_api_response(self, api_response) -> Response:
        """Parse non-streaming API response."""
        return parse_mistral_response(api_response, model_name=self.model)

    def process_streaming_response(self, accumulated_chunks, accumulated_text, final_chunk) -> Response:
        """
        Process streaming API response and build final Response object.

        Mistral streams tool calls incrementally like OpenAI, so we need
        to accumulate tool call deltas across chunks.

        Args:
            accumulated_chunks: All chunks received during streaming
            accumulated_text: Accumulated text content
            final_chunk: The final chunk (contains usage info)

        Returns:
            Response object with parsed message and usage
        """
        import json
        from orchestral.llm.base.tool_call import ToolCall

        # Accumulate tool calls from chunks
        tool_calls_accumulator = {}  # index -> tool call data

        for chunk in accumulated_chunks:
            if hasattr(chunk, 'data') and chunk.data and hasattr(chunk.data, 'choices'):
                if chunk.data.choices:
                    delta = chunk.data.choices[0].delta

                    # Check for tool calls in delta
                    if hasattr(delta, 'tool_calls') and delta.tool_calls:
                        for tc_delta in delta.tool_calls:
                            # Mistral uses index like OpenAI
                            idx = tc_delta.index if hasattr(tc_delta, 'index') else 0

                            # Initialize on first encounter
                            if idx not in tool_calls_accumulator:
                                tool_calls_accumulator[idx] = {
                                    "id": None,
                                    "type": None,
                                    "function": {
                                        "name": None,
                                        "arguments": ""
                                    }
                                }

                            # Update from delta
                            if hasattr(tc_delta, 'id') and tc_delta.id:
                                tool_calls_accumulator[idx]["id"] = tc_delta.id
                            if hasattr(tc_delta, 'type') and tc_delta.type:
                                tool_calls_accumulator[idx]["type"] = tc_delta.type
                            if hasattr(tc_delta, 'function') and tc_delta.function:
                                if hasattr(tc_delta.function, 'name') and tc_delta.function.name:
                                    tool_calls_accumulator[idx]["function"]["name"] = tc_delta.function.name
                                if hasattr(tc_delta.function, 'arguments') and tc_delta.function.arguments:
                                    tool_calls_accumulator[idx]["function"]["arguments"] += tc_delta.function.arguments

        # Parse accumulated tool calls
        tool_calls = []
        if tool_calls_accumulator:
            for idx in sorted(tool_calls_accumulator.keys()):
                tc_data = tool_calls_accumulator[idx]

                # Parse JSON arguments
                try:
                    arguments = json.loads(tc_data["function"]["arguments"])
                except json.JSONDecodeError:
                    # If JSON is malformed, use raw string
                    arguments = {"raw": tc_data["function"]["arguments"]}

                tool_call = ToolCall(
                    id=tc_data["id"],
                    tool_name=tc_data["function"]["name"],
                    arguments=arguments
                )
                tool_calls.append(tool_call)

        # Create message with text and tool calls
        message = Message(
            text=accumulated_text if accumulated_text else None,
            role='assistant',
            tool_calls=tool_calls if tool_calls else None
        )

        # Parse usage from final chunk
        usage = None
        if hasattr(final_chunk, 'data') and final_chunk.data and hasattr(final_chunk.data, 'usage'):
            usage = parse_mistral_usage(final_chunk.data.usage, model_name=self.model)

        # Get response ID and model from final chunk
        response_id = None
        response_model = self.model
        if hasattr(final_chunk, 'data') and final_chunk.data:
            if hasattr(final_chunk.data, 'id'):
                response_id = final_chunk.data.id
            if hasattr(final_chunk.data, 'model'):
                response_model = final_chunk.data.model

        return Response(
            id=response_id,
            model=response_model,
            message=message,
            usage=usage
        )

    def extract_text_from_chunk(self, chunk) -> str:
        """
        Extract text content from a streaming chunk.

        Args:
            chunk: Single streaming chunk from Mistral

        Returns:
            Text content from the chunk, or empty string
        """
        # Mistral streaming chunks have structure: chunk.data.choices[0].delta.content
        if hasattr(chunk, 'data') and chunk.data:
            if hasattr(chunk.data, 'choices') and chunk.data.choices:
                delta = chunk.data.choices[0].delta
                if hasattr(delta, 'content') and delta.content is not None:
                    return delta.content

        return ""
