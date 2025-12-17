from orchestral.context.message import Message
from orchestral.context.context import Context
from orchestral.llm.base.llm import LLM
from orchestral.llm.base.response import Response
from orchestral.llm.anthropic.parsers import (
    convert_message_to_anthropic, parse_anthropic_response, parse_anthropic_usage)
from orchestral.llm.anthropic.pricing_model import pricing_model
from orchestral.llm.anthropic.tool_adapter import convert_tool_to_anthropic

import os
from typing import Optional, List, Dict, Any
import anthropic
from dotenv import load_dotenv


def _apply_cache_control(system_prompt: Optional[str], messages: List[Dict[str, Any]]) -> tuple[Any, List[Dict[str, Any]]]:
    """
    Apply cache_control to system prompt and last message to enable prompt caching.

    Returns:
        Tuple of (modified_system, modified_messages)
    """
    # Convert system prompt from string to list format with cache_control
    modified_system = None
    if system_prompt:
        modified_system = [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }
        ]

    # Add cache_control to the last message
    modified_messages = messages.copy()
    if modified_messages:
        last_msg = modified_messages[-1].copy()

        # Convert content to list format if it's not already
        if isinstance(last_msg.get('content'), str):
            last_msg['content'] = [{"type": "text", "text": last_msg['content']}]
        elif isinstance(last_msg.get('content'), list):
            last_msg['content'] = last_msg['content'].copy()

        # Add cache_control to the last content block
        if last_msg['content']:
            last_msg['content'][-1] = {
                **last_msg['content'][-1],
                "cache_control": {"type": "ephemeral"}
            }

        modified_messages[-1] = last_msg

    return modified_system, modified_messages


class Claude(LLM):

    def __init__(self, 
            model='claude-3-5-haiku-latest', 
            api_key: Optional[str] = None,
            tools = None
        ):
        super().__init__(tools=tools)
        
        # Check that the model is supported
        supported_models = pricing_model.rates.keys()
        if model in supported_models:
            self.model = model
        else:
            raise ValueError(f"Model '{model}' is not supported.")
        
        self.load_api_key(api_key)
        self.client = anthropic.Client(api_key=self.api_key)

    # Preparation
    def load_api_key(self, api_key: Optional[str] = None):
        if api_key:
            self.api_key = api_key
        else:
            load_dotenv()  # Load .env file
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("The ANTHROPIC_API_KEY must be provided either as an argument or as an environment variable.")
        
    def process_api_input(self, context: Context):
        """Preprocess the input for the API call"""
        messages = []
        system_messages = []

        for msg in context.get_messages():
            if msg.role == "system":
                # Collect system messages separately
                if msg.text:
                    system_messages.append(msg.text)
            else:
                # Convert non-system messages
                messages.append(convert_message_to_anthropic(msg))

        # Combine system messages into a single string
        system_prompt = "\n\n".join(system_messages) if system_messages else None

        return {"messages": messages, "system": system_prompt}
    
    def _convert_tools_to_provider_format(self):
        """Convert tools to the provider-specific format"""
        return [convert_tool_to_anthropic(tool.get_tool_spec()) for tool in self.tools]

    # API
    def call_api(self, formatted_input, max_tokens=2048, use_prompt_cache=False, **kwargs):
        """Implement the specifics of the API call"""
        # formatted_input is now a dict with "messages" and "system" keys
        messages = formatted_input["messages"]
        system_prompt = formatted_input["system"]

        # Apply cache control if requested
        if use_prompt_cache:
            system_prompt, messages = _apply_cache_control(system_prompt, messages)

        # Build call parameters
        call_params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            **kwargs
        }

        # Add system prompt if provided
        if system_prompt:
            call_params["system"] = system_prompt

        # Add tools if any are provided
        if self.tool_schemas:
            call_params["tools"] = self.tool_schemas

        api_response = self.client.messages.create(**call_params)
        return api_response
    
    def call_streaming_api(self, formatted_input, use_prompt_cache=False, **kwargs):
        """Implement the specifics of the streaming API call"""
        # formatted_input is now a dict with "messages" and "system" keys
        messages = formatted_input["messages"]
        system_prompt = formatted_input["system"]

        # Apply cache control if requested
        if use_prompt_cache:
            system_prompt, messages = _apply_cache_control(system_prompt, messages)

        # Extract max_tokens from kwargs (required by Anthropic)
        max_tokens = kwargs.pop("max_tokens", 2048)

        call_params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            **kwargs
        }

        # Add system prompt if provided
        if system_prompt:
            call_params["system"] = system_prompt

        # Add tools if any are provided
        if self.tool_schemas:
            call_params["tools"] = self.tool_schemas

        # Create the stream manager
        stream_manager = self.client.messages.stream(**call_params)

        # Enter the context and store BOTH references
        # - stream_manager is needed for __exit__
        # - stream is needed for iteration and get_final_message()
        self._stream_manager = stream_manager
        self._stream = stream_manager.__enter__()

        # Return the iterator
        return self._stream
    

    # Extraction
    def process_api_response(self, api_response) -> Response:
        """Process the API response and return a Response object"""
        return parse_anthropic_response(api_response, model_name=self.model)

    def process_streaming_response(self, accumulated_chunks, accumulated_text, final_chunk) -> Response:
        """Process the streaming API response and return a Response object"""
        try:
            # Exit the context manager
            self._stream_manager.__exit__(None, None, None)

            # Get the final message from the stream (NOT the manager!)
            final_message = self._stream.get_final_message()

            # Use existing parser - it handles text, tool calls, usage, everything!
            return parse_anthropic_response(final_message, model_name=self.model)

        except Exception as e:
            # Ensure cleanup even on error
            if hasattr(self, '_stream_manager'):
                try:
                    self._stream_manager.__exit__(None, None, None)
                except:
                    pass
            raise e

    def extract_text_from_chunk(self, chunk) -> str:
        """Extract text from a streaming response chunk"""
        # Anthropic chunks are events with different types
        # Text comes in content_block_delta events with delta.text
        if hasattr(chunk, 'type') and chunk.type == 'content_block_delta':
            if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                return chunk.delta.text
        return ""

    def cleanup_stream(self):
        """Cleanup Anthropic stream context manager when stream is interrupted."""
        if hasattr(self, '_stream_manager'):
            try:
                self._stream_manager.__exit__(None, None, None)
            except Exception:
                pass  # Already cleaned up or never started