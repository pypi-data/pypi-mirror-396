from orchestral.llm.base.llm import LLM
from orchestral.context.message import Message
from orchestral.context.context import Context
from orchestral.llm.base.response import Response
from orchestral.llm.openai.parsers import (
    convert_message_to_openai, parse_openai_response, parse_openai_usage)
from orchestral.llm.openai.tool_adapter import convert_tool_to_openai

import os
from typing import Optional
import openai
from dotenv import load_dotenv


class GPT(LLM):

    def __init__(self, 
            model='gpt-4o-mini', 
            api_key: Optional[str] = None,
            tools = None
    ):
        super().__init__(tools=tools)

        self.model = model
        self.load_api_key(api_key)
        self.client = openai.Client(api_key=self.api_key, timeout=30.0)
        # self.tools = tools or []
        # self.tool_router = {tool.get_name(): tool for tool in self.tools}
        # self.set_tool_schemas()


    # Preparation:
    def load_api_key(self, api_key: Optional[str] = None):
        if api_key:  # If API key is provided as an argument
            self.api_key = api_key
        else:  # Try loading from environment variable
            load_dotenv()  # Load .env file
            self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("The OPENAI_API_KEY must be provided either as an argument or via the OPENAI_API_KEY environment variable.")

    def process_api_input(self, context: Context):
        """Preprocess the input for the API call"""
        return [convert_message_to_openai(msg) for msg in context.get_messages()]

    def _convert_tools_to_provider_format(self):
        """Convert tools to the provider-specific format"""
        return [convert_tool_to_openai(tool.get_tool_spec()) for tool in self.tools]

    # API:
    def call_api(self, formatted_input, use_prompt_cache=False, **kwargs):
        """Implement the specifics of the API call"""
        # Note: use_prompt_cache is accepted but ignored (OpenAI doesn't support prompt caching)
        # Include tools if provided
        call_params = {
            "model": self.model,
            "messages": formatted_input,
            **kwargs
        }

        if self.tool_schemas:
            call_params["tools"] = self.tool_schemas

        api_response = self.client.chat.completions.create(**call_params)
        return api_response

    def call_streaming_api(self, formatted_input, use_prompt_cache=False, **kwargs):
        """Implement the specifics of the streaming API call"""
        # Note: use_prompt_cache is accepted but ignored (OpenAI doesn't support prompt caching)
        call_params = {
            "model": self.model,
            "messages": formatted_input,
            "stream": True,
            "stream_options": {"include_usage": True},
            **kwargs
        }

        # Add tools if any are provided
        if self.tool_schemas:
            call_params["tools"] = self.tool_schemas

        streaming_response = self.client.chat.completions.create(**call_params)
        return streaming_response


    # Extraction:
    def process_api_response(self, api_response) -> Response:
        """Process the API response and return a Response object"""
        return parse_openai_response(api_response, model_name=self.model)

    def process_streaming_response(self, accumulated_chunks, accumulated_text, final_chunk) -> Response:
        """Process the streaming API response and return a Response object"""
        import json
        from orchestral.llm.base.tool_call import ToolCall

        # Accumulate tool calls from chunks
        tool_calls_accumulator = {}  # index -> tool call data

        for chunk in accumulated_chunks:
            if chunk.choices:
                delta = chunk.choices[0].delta

                if hasattr(delta, 'tool_calls') and delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index

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
                            if tc_delta.function.name:
                                tool_calls_accumulator[idx]["function"]["name"] = tc_delta.function.name
                            if tc_delta.function.arguments:
                                tool_calls_accumulator[idx]["function"]["arguments"] += tc_delta.function.arguments

        # Parse tool calls
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

        usage = parse_openai_usage(final_chunk.usage, model_name=self.model)

        return Response(
            id=final_chunk.id,
            model=final_chunk.model,
            message=message,
            usage=usage
        )

    def extract_text_from_chunk(self, chunk) -> str:
        """Extract text from a streaming response chunk"""
        if chunk.choices:
            content = chunk.choices[0].delta.content
            return content if content is not None else ""

        # The final chunk has an empty choices list
        return ""