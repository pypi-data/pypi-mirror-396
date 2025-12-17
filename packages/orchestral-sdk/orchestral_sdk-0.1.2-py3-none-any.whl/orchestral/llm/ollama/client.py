from orchestral.llm.base.llm import LLM
from orchestral.context.message import Message
from orchestral.context.context import Context
from orchestral.llm.base.response import Response
from orchestral.llm.ollama.parsers import (
    convert_message_to_ollama, parse_ollama_response, parse_ollama_usage)
from orchestral.llm.ollama.tool_adapter import convert_tool_to_ollama

from typing import Optional
from ollama import Client


def get_available_model_names():
    client = Client()
    models = client.list()
    return [model.model for model in models.models] # Hey! now model doesn't look like a real word!


class Ollama(LLM):
    """
    Ollama LLM client for local model inference.

    Ollama runs models locally and provides an OpenAI-compatible API.
    This implementation follows the same patterns as the GPT client.
    """

    def __init__(self,
                 model=None,
                 host: Optional[str] = None,
                 tools=None,
                 think: bool = False,
                 stream_thinking: bool = True):
        """
        Initialize Ollama client.

        Args:
            model: The model name (e.g., 'gpt-oss:20b', 'llama3.2', 'mistral')
            host: Ollama server host (default: http://localhost:11434)
            tools: List of tools available for the model to use
            think: Enable chain-of-thought reasoning (default: False)
            stream_thinking: Stream thinking tokens to user (default: True).
                           If False, only content is streamed.
        """
        super().__init__(tools=tools)

        # Handle model selection and validation
        available_models = get_available_model_names()

        if len(available_models) == 0:
            raise ValueError("No Ollama models are available. Please install Ollama, run `ollama pull <model>`, run the model `ollama run <model>`. Then try again.")
        
        if model is not None and model not in available_models:
            raise ValueError(f"Model '{model}' is not available in Ollama. Available models: {available_models}")

        self.model = model or available_models[0]

        # Handle other stuff
        self.host = host
        self.client = Client(host=host) if host else Client()
        self.think = think ### TODO! Think might not always a valid argument for some models?? Check this.
        self.stream_thinking = stream_thinking

    # Preparation:
    def process_api_input(self, context: Context):
        """Preprocess the input for the API call."""
        return [convert_message_to_ollama(msg) for msg in context.get_messages()]

    def _convert_tools_to_provider_format(self):
        """Convert tools to Ollama's format (same as OpenAI)."""
        return [convert_tool_to_ollama(tool.get_tool_spec()) for tool in self.tools]

    # API:
    def call_api(self, formatted_input, use_prompt_cache=False, **kwargs):
        """Call Ollama chat API (non-streaming)."""
        # Note: use_prompt_cache is accepted but ignored (Ollama doesn't support prompt caching)
        call_params = {
            "model": self.model,
            "messages": formatted_input,
            "think": self.think,
            **kwargs
        }

        # Include tools if provided
        if self.tool_schemas:
            call_params["tools"] = self.tool_schemas

        api_response = self.client.chat(**call_params)
        return api_response

    def call_streaming_api(self, formatted_input, use_prompt_cache=False, **kwargs):
        """Call Ollama chat API with streaming enabled."""
        # Note: use_prompt_cache is accepted but ignored (Ollama doesn't support prompt caching)
        call_params = {
            "model": self.model,
            "messages": formatted_input,
            "stream": True,
            "think": self.think,
            **kwargs
        }

        # Add tools if any are provided
        if self.tool_schemas:
            call_params["tools"] = self.tool_schemas

        streaming_response = self.client.chat(**call_params)
        return streaming_response

    # Extraction:
    def process_api_response(self, api_response) -> Response:
        """Process the API response and return a Response object."""
        return parse_ollama_response(api_response, model_name=self.model)

    def process_streaming_response(self, accumulated_chunks, accumulated_text, final_chunk) -> Response:
        """
        Process streaming response chunks.

        Key differences from OpenAI:
        - Ollama streams 'thinking' token-by-token, not 'content'
        - Tool calls appear ALL AT ONCE in the final chunk only
        - No incremental tool call building needed

        We separately accumulate thinking and content from chunks.
        """
        import json
        from orchestral.llm.base.tool_call import ToolCall

        # Separately accumulate thinking and content from all chunks
        accumulated_thinking = ""
        accumulated_content = ""

        for chunk in accumulated_chunks:
            if hasattr(chunk, 'message'):
                # Accumulate thinking
                if hasattr(chunk.message, 'thinking') and chunk.message.thinking:
                    if chunk.message.thinking != 'None':  # Skip final chunk's 'None' string
                        accumulated_thinking += chunk.message.thinking

                # Accumulate content
                if hasattr(chunk.message, 'content') and chunk.message.content:
                    accumulated_content += chunk.message.content

        # Extract tool calls from final chunk (they only appear there)
        tool_calls = []
        if final_chunk.message.tool_calls:
            for i, tc in enumerate(final_chunk.message.tool_calls):
                # Ollama doesn't provide tool call IDs, generate them
                tool_call = ToolCall(
                    id=f"call_{i}",
                    tool_name=tc.function.name,
                    arguments=tc.function.arguments  # Already a dict, not JSON string
                )
                tool_calls.append(tool_call)

        # Create message with content as text and thinking as reasoning
        message = Message(
            text=accumulated_content if accumulated_content else None,
            reasoning=accumulated_thinking if accumulated_thinking else None,
            role='assistant',
            tool_calls=tool_calls if tool_calls else None
        )

        # Parse usage from final chunk
        usage = parse_ollama_usage(final_chunk, model_name=self.model)

        return Response(
            id=final_chunk.created_at,
            model=final_chunk.model,
            message=message,
            usage=usage
        )

    def extract_text_from_chunk(self, chunk) -> str:
        """
        Extract text from a streaming response chunk.

        For Ollama:
        - 'content' field contains the actual response content (streamed to user)
        - 'thinking' field contains reasoning (saved but NOT streamed)
        - We only stream content; thinking is captured in process_streaming_response

        Future: Option 3 would add a separate stream for thinking.
        """
        if hasattr(chunk, 'message'):
            # Only stream content to the user
            if hasattr(chunk.message, 'content') and chunk.message.content:
                return chunk.message.content

        return ""
