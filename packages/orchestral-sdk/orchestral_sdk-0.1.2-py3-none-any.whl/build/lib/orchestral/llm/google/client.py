from orchestral.context.message import Message
from orchestral.context.context import Context
from orchestral.llm.base.llm import LLM
from orchestral.llm.base.response import Response
from orchestral.llm.google.parsers import (
    convert_message_to_gemini, parse_gemini_response, parse_gemini_usage)
from orchestral.llm.google.pricing_model import pricing_model
from orchestral.llm.google.tool_adapter import convert_tool_to_gemini

import os
from typing import Optional
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv


class Gemini(LLM):

    def __init__(self,
            model='gemini-2.0-flash-exp',
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
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model_name=self.model)

    # Preparation
    def load_api_key(self, api_key: Optional[str] = None):
        if api_key:
            self.api_key = api_key
        else:
            load_dotenv()  # Load .env file
            self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("The GOOGLE_API_KEY must be provided either as an argument or as an environment variable.")

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
                messages.append(convert_message_to_gemini(msg))

        # Combine system messages into a single string
        system_instruction = "\n\n".join(system_messages) if system_messages else None

        return {"messages": messages, "system_instruction": system_instruction}

    def _convert_tools_to_provider_format(self):
        """Convert tools to the provider-specific format

        Gemini expects tools as a list with a single dict containing
        all function_declarations in an array.
        """
        if not self.tools:
            return []

        # Collect all function declarations
        function_declarations = []
        for tool in self.tools:
            tool_dict = convert_tool_to_gemini(tool.get_tool_spec())
            # Each tool returns {function_declarations: [...]}
            # We need to merge them all into one
            function_declarations.extend(tool_dict['function_declarations'])

        # Return as a single tools object with all declarations
        return [{"function_declarations": function_declarations}]

    def _handle_quota_error(self, error):
        """Format quota/rate limit errors nicely"""
        error_msg = str(error)

        # Check if it's a quota error
        if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            if "free_tier" in error_msg and "limit: 0" in error_msg:
                raise ValueError(
                    f"Google Gemini API quota error: Your API key has no free tier quota.\n\n"
                    f"This usually means:\n"
                    f"  1. Your API key is from Google Cloud (requires billing) not Google AI Studio\n"
                    f"  2. Free tier hasn't been enabled for this key\n\n"
                    f"To fix:\n"
                    f"  • Get a new API key from https://aistudio.google.com/apikey (free tier)\n"
                    f"  • OR enable billing in Google Cloud Console\n"
                    f"  • Check usage at https://ai.dev/usage?tab=rate-limit\n\n"
                    f"Model: {self.model}"
                ) from error
            else:
                # Extract retry delay if present
                import re
                retry_match = re.search(r'retry in (\d+(?:\.\d+)?)', error_msg.lower())
                retry_delay = retry_match.group(1) if retry_match else "unknown"

                raise ValueError(
                    f"Google Gemini API rate limit exceeded.\n\n"
                    f"Retry in: {retry_delay} seconds\n"
                    f"Check usage: https://ai.dev/usage?tab=rate-limit\n\n"
                    f"Model: {self.model}"
                ) from error

        # Re-raise if not a quota error
        raise error

    # API
    def call_api(self, formatted_input, use_prompt_cache=False, **kwargs):
        """Implement the specifics of the API call"""
        # Note: use_prompt_cache is accepted but ignored (Gemini doesn't support prompt caching)
        messages = formatted_input["messages"]
        system_instruction = formatted_input["system_instruction"]

        # Build generation config
        generation_config = kwargs.pop("generation_config", {})

        # Create model with system instruction if provided
        if system_instruction:
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_instruction
            )
        else:
            model = self.client

        # Add tools if any are provided
        if self.tool_schemas:
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_instruction,
                tools=self.tool_schemas
            )

        try:
            api_response = model.generate_content(
                messages,
                generation_config=generation_config,
                **kwargs
            )
            return api_response
        except google_exceptions.ResourceExhausted as e:
            self._handle_quota_error(e)

    def call_streaming_api(self, formatted_input, use_prompt_cache=False, **kwargs):
        """Implement the specifics of the streaming API call"""
        # Note: use_prompt_cache is accepted but ignored (Gemini doesn't support prompt caching)
        messages = formatted_input["messages"]
        system_instruction = formatted_input["system_instruction"]

        # Build generation config
        generation_config = kwargs.pop("generation_config", {})

        # Create model with system instruction if provided
        if system_instruction:
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_instruction
            )
        else:
            model = self.client

        # Add tools if any are provided
        if self.tool_schemas:
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_instruction,
                tools=self.tool_schemas
            )

        try:
            streaming_response = model.generate_content(
                messages,
                generation_config=generation_config,
                stream=True,
                **kwargs
            )
            return streaming_response
        except google_exceptions.ResourceExhausted as e:
            self._handle_quota_error(e)

    # Extraction
    def process_api_response(self, api_response) -> Response:
        """Process the API response and return a Response object"""
        return parse_gemini_response(api_response, model_name=self.model)

    def process_streaming_response(self, accumulated_chunks, accumulated_text, final_chunk) -> Response:
        """Process the streaming API response and return a Response object"""
        # For Gemini, the final chunk contains the complete response
        return parse_gemini_response(final_chunk, model_name=self.model)

    def extract_text_from_chunk(self, chunk) -> str:
        """Extract text from a streaming response chunk"""
        # Use Gemini's .text property which properly extracts text from parts
        # It handles all the edge cases and returns just the delta text
        try:
            if hasattr(chunk, 'text'):
                return chunk.text
            return ""
        except (ValueError, AttributeError):
            # .text can raise ValueError if there's no text content (e.g., function calls)
            return ""
