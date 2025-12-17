from abc import ABC, abstractmethod
from orchestral.context.context import Context
from orchestral.llm.base.response import Response


class LLM(ABC):
    def __init__(self, tools=None):
        self.set_tools(tools or [])

    def set_tools(self, tools):
        self.tools = tools
        self.tool_router = {tool.get_name(): tool for tool in self.tools}
        self.tool_schemas = self._convert_tools_to_provider_format()

    def get_response(self, context: Context, **kwargs) -> Response:
        formatted_input = self.process_api_input(context)
        api_response = self.call_api(formatted_input, **kwargs)
        response = self.process_api_response(api_response)

        # Save the raw response for debugging/logging
        self.last_raw_response = api_response
        
        return response

    def stream_response(self, context: Context, **kwargs):
        formatted_input = self.process_api_input(context)

        accumulated_chunks = []
        accumulated_text = ''
        for chunk in self.call_streaming_api(formatted_input, **kwargs):
            text = self.extract_text_from_chunk(chunk)
            accumulated_chunks.append(chunk)  # accumulate for final response
            if text:
                accumulated_text += text
                yield text
        final_chunk = chunk

        # Build final Response from all chunks, also pass the final chunk
        return self.process_streaming_response(accumulated_chunks, accumulated_text, final_chunk)

    @abstractmethod
    def process_api_input(self, context: Context):
        """Take the standard context object and format it for the specific API"""
        pass

    @abstractmethod
    def call_api(self, formatted_input, **kwargs):
        """Implement the specifics of the API call"""
        pass

    @abstractmethod
    def process_api_response(self, api_response) -> Response:
        """Process the API response and return a Response object"""
        pass

    # =========
    # Streaming
    # =========

    @abstractmethod
    def process_streaming_response(self, accumulated_chunks, accumulated_text, final_chunk) -> Response:
        """Process the streaming response chunks and return a Response object"""
        pass

    @abstractmethod
    def call_streaming_api(self, formatted_input, **kwargs):
        """Implement the specifics of the streaming API call"""
        return []

    @abstractmethod
    def extract_text_from_chunk(self, chunk) -> str:
        """Extract text from a streaming response chunk"""
        
    # ========
    # Tool Use
    # ========
    @abstractmethod
    def _convert_tools_to_provider_format(self):
        """Convert tools to provider-specific schema format"""

    # ==================
    # Stream Cleanup
    # ==================
    def cleanup_stream(self):
        """
        Cleanup streaming resources when stream is abandoned (e.g., interrupted).

        Override in provider implementations if cleanup is needed.
        Default implementation does nothing (safe for most providers).
        """
        pass  # Default: no cleanup needed

