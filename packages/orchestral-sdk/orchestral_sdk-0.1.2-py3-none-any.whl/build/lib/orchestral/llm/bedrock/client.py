"""
AWS Bedrock LLM client implementation.

Provides access to multiple model families (Claude, Llama, Mistral, Cohere, Titan)
through AWS Bedrock's unified API.
"""

import json
import os
from typing import Optional, List, Dict, Any

import boto3
from dotenv import load_dotenv

from orchestral.context.message import Message
from orchestral.context.context import Context
from orchestral.llm.base.llm import LLM
from orchestral.llm.base.response import Response
from orchestral.llm.bedrock.parsers import (
    convert_message_to_bedrock,
    parse_bedrock_response,
)
from orchestral.llm.bedrock.pricing_model import pricing_model
from orchestral.llm.bedrock.tool_adapter import convert_tool_to_bedrock
from orchestral.llm.bedrock.model_details import get_model_family, MODEL_DETAILS


class Bedrock(LLM):
    """
    AWS Bedrock LLM client supporting multiple model families.

    Provides a unified interface to Claude, Llama, Mistral, Cohere, and Titan models
    through AWS Bedrock.
    """

    def __init__(
        self,
        model: str,
        region_name: str = 'us-east-1',
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        tools: Optional[List] = None
    ):
        """
        Initialize Bedrock client.

        Args:
            model: Bedrock model ID (e.g., 'anthropic.claude-3-5-sonnet-20241022-v2:0')
            region_name: AWS region (default: 'us-east-1')
            aws_access_key_id: AWS access key (optional, uses env/config if None)
            aws_secret_access_key: AWS secret key (optional, uses env/config if None)
            aws_session_token: AWS session token (optional, for temporary credentials)
            tools: List of tools to make available to the model
        """
        super().__init__(tools=tools)

        # Validate model
        if model not in MODEL_DETAILS:
            raise ValueError(
                f"Model '{model}' is not supported. "
                f"Available models: {list(MODEL_DETAILS.keys())}"
            )

        self.model = model
        self.model_family = get_model_family(model)
        self.region_name = region_name

        # Load AWS credentials
        self._load_aws_credentials(
            aws_access_key_id,
            aws_secret_access_key,
            aws_session_token
        )

        # Initialize Bedrock Runtime client
        session_kwargs = {
            'region_name': self.region_name,
        }
        if self.aws_access_key_id:
            session_kwargs['aws_access_key_id'] = self.aws_access_key_id
        if self.aws_secret_access_key:
            session_kwargs['aws_secret_access_key'] = self.aws_secret_access_key
        if self.aws_session_token:
            session_kwargs['aws_session_token'] = self.aws_session_token

        self.client = boto3.client('bedrock-runtime', **session_kwargs)

    def _load_aws_credentials(
        self,
        aws_access_key_id: Optional[str],
        aws_secret_access_key: Optional[str],
        aws_session_token: Optional[str]
    ):
        """Load AWS credentials from arguments or environment."""
        load_dotenv()

        self.aws_access_key_id = aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_session_token = aws_session_token or os.getenv('AWS_SESSION_TOKEN')

        # Note: boto3 will use default credential chain if these are not provided
        # (environment variables, ~/.aws/credentials, IAM role, etc.)

    def _convert_tools_to_provider_format(self):
        """Convert tools to Bedrock-specific format based on model family."""
        if not self.tools:
            return []

        # Check if model family supports tools
        if self.model_family == 'titan':
            # Titan doesn't support tool calling
            return []

        return [
            convert_tool_to_bedrock(tool.get_tool_spec(), self.model_family)
            for tool in self.tools
        ]

    def process_api_input(self, context: Context) -> Dict[str, Any]:
        """
        Convert Context to Bedrock format.

        Returns a dict with 'messages' and optionally 'system' for model families that support it.
        """
        messages = []
        system_messages = []

        for msg in context.get_messages():
            if msg.role == "system":
                # Collect system messages separately for model families that support them
                if msg.text:
                    system_messages.append(msg.text)
            else:
                # Convert to appropriate format for this model family
                messages.append(convert_message_to_bedrock(msg, self.model_family))

        # Combine system messages
        system_prompt = "\n\n".join(system_messages) if system_messages else None

        return {
            "messages": messages,
            "system": system_prompt
        }

    def _build_request_body(
        self,
        formatted_input: Dict[str, Any],
        max_tokens: int = 2048,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build the request body for Bedrock InvokeModel API.

        Different model families require different request body structures.
        """
        messages = formatted_input["messages"]
        system_prompt = formatted_input.get("system")

        if self.model_family == 'claude':
            # Claude uses Anthropic's format
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": messages,
                "max_tokens": max_tokens,
                **kwargs
            }
            if system_prompt:
                body["system"] = system_prompt
            if self.tool_schemas:
                body["tools"] = self.tool_schemas

        elif self.model_family == 'llama':
            # Llama format
            body = {
                "prompt": self._format_llama_prompt(messages, system_prompt),
                "max_gen_len": max_tokens,
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
            }

        elif self.model_family == 'mistral':
            # Mistral format
            body = {
                "prompt": self._format_mistral_prompt(messages, system_prompt),
                "max_tokens": max_tokens,
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
            }

        elif self.model_family == 'cohere':
            # Cohere format
            body = {
                "message": messages[-1].get("message", "") if messages else "",
                "chat_history": messages[:-1] if len(messages) > 1 else [],
                "max_tokens": max_tokens,
                "temperature": kwargs.get("temperature", 0.7),
            }
            if system_prompt:
                body["preamble"] = system_prompt
            if self.tool_schemas:
                body["tools"] = self.tool_schemas

        elif self.model_family == 'titan':
            # Titan format
            body = {
                "inputText": self._format_titan_prompt(messages, system_prompt),
                "textGenerationConfig": {
                    "maxTokenCount": max_tokens,
                    "temperature": kwargs.get("temperature", 0.7),
                    "topP": kwargs.get("top_p", 0.9),
                }
            }

        else:
            # Default to Claude format
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": messages,
                "max_tokens": max_tokens,
                **kwargs
            }

        return body

    def _format_llama_prompt(self, messages: List[Dict], system_prompt: Optional[str]) -> str:
        """Format messages into Llama prompt format."""
        prompt_parts = []

        if system_prompt:
            prompt_parts.append(f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{system_prompt}<|eot_id|>")

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"<|start_header_id|>{role}<|end_header_id|>\n{content}<|eot_id|>")

        prompt_parts.append("<|start_header_id|>assistant<|end_header_id|>")
        return "".join(prompt_parts)

    def _format_mistral_prompt(self, messages: List[Dict], system_prompt: Optional[str]) -> str:
        """Format messages into Mistral prompt format."""
        prompt_parts = []

        if system_prompt:
            prompt_parts.append(f"[INST] {system_prompt} [/INST]")

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                prompt_parts.append(f"[INST] {content} [/INST]")
            else:
                prompt_parts.append(content)

        return " ".join(prompt_parts)

    def _format_titan_prompt(self, messages: List[Dict], system_prompt: Optional[str]) -> str:
        """Format messages into Titan prompt format."""
        prompt_parts = []

        if system_prompt:
            prompt_parts.append(system_prompt)

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role.capitalize()}: {content}")

        return "\n\n".join(prompt_parts)

    def call_api(self, formatted_input: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Call Bedrock InvokeModel API.

        Args:
            formatted_input: Formatted messages from process_api_input
            **kwargs: Additional parameters (max_tokens, temperature, etc.)

        Returns:
            Parsed response body as dict
        """
        max_tokens = kwargs.pop('max_tokens', 2048)
        body = self._build_request_body(formatted_input, max_tokens, **kwargs)

        # Call Bedrock API
        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(body)
        )

        # Parse response
        response_body = json.loads(response['body'].read())
        return response_body

    def process_api_response(self, api_response: Dict[str, Any]) -> Response:
        """
        Parse Bedrock API response into unified Response object.

        Args:
            api_response: Raw response from Bedrock API

        Returns:
            Unified Response object
        """
        return parse_bedrock_response(api_response, self.model, self.model_family)

    def call_streaming_api(self, formatted_input: Dict[str, Any], **kwargs):
        """
        Call Bedrock InvokeModelWithResponseStream API.

        Args:
            formatted_input: Formatted messages from process_api_input
            **kwargs: Additional parameters (max_tokens, temperature, etc.)

        Yields:
            Stream chunks from the API
        """
        max_tokens = kwargs.pop('max_tokens', 2048)
        body = self._build_request_body(formatted_input, max_tokens, **kwargs)

        # Call streaming API
        response = self.client.invoke_model_with_response_stream(
            modelId=self.model,
            body=json.dumps(body)
        )

        # Store event stream for cleanup
        self._event_stream = response.get('body')

        # Yield chunks from event stream
        if self._event_stream:
            for event in self._event_stream:
                yield event

    def extract_text_from_chunk(self, chunk: Dict[str, Any]) -> str:
        """
        Extract text from a streaming response chunk.

        Args:
            chunk: A single event from the stream

        Returns:
            Extracted text content
        """
        # Check if this is a chunk event
        if 'chunk' not in chunk:
            return ""

        # Parse the chunk bytes
        chunk_data = json.loads(chunk['chunk']['bytes'])

        if self.model_family == 'claude':
            # Claude streaming format
            if chunk_data.get('type') == 'content_block_delta':
                delta = chunk_data.get('delta', {})
                if delta.get('type') == 'text_delta':
                    return delta.get('text', '')

        elif self.model_family == 'llama':
            # Llama streaming format
            return chunk_data.get('generation', '')

        elif self.model_family == 'mistral':
            # Mistral streaming format
            outputs = chunk_data.get('outputs', [])
            if outputs:
                return outputs[0].get('text', '')

        elif self.model_family == 'cohere':
            # Cohere streaming format
            if chunk_data.get('is_finished') is False:
                return chunk_data.get('text', '')

        elif self.model_family == 'titan':
            # Titan streaming format
            return chunk_data.get('outputText', '')

        return ""

    def process_streaming_response(
        self,
        accumulated_chunks: List[Dict[str, Any]],
        accumulated_text: str,
        final_chunk: Dict[str, Any]
    ) -> Response:
        """
        Build final Response from accumulated streaming chunks.

        Args:
            accumulated_chunks: All chunks from the stream
            accumulated_text: Accumulated text content
            final_chunk: The last chunk (may contain usage info)

        Returns:
            Unified Response object
        """
        # Build message from accumulated text
        message = Message(text=accumulated_text, role='assistant')

        # Try to extract usage from final chunk(s)
        usage_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

        # Look for usage data in chunks
        for chunk in accumulated_chunks:
            if 'chunk' in chunk:
                chunk_data = json.loads(chunk['chunk']['bytes'])

                if self.model_family == 'claude':
                    # Claude sends usage in message_stop event
                    if chunk_data.get('type') == 'message_delta':
                        usage_data = chunk_data.get('usage', {})
                        if usage_data:
                            usage_tokens['completion_tokens'] = usage_data.get('output_tokens', 0)
                    elif chunk_data.get('type') == 'message_start':
                        usage_data = chunk_data.get('message', {}).get('usage', {})
                        if usage_data:
                            usage_tokens['prompt_tokens'] = usage_data.get('input_tokens', 0)

                elif self.model_family == 'llama':
                    usage_tokens['prompt_tokens'] = chunk_data.get('prompt_token_count', 0)
                    usage_tokens['completion_tokens'] = chunk_data.get('generation_token_count', 0)

                elif self.model_family in ['mistral', 'cohere']:
                    usage_tokens['prompt_tokens'] = chunk_data.get('prompt_token_count', 0)
                    usage_tokens['completion_tokens'] = chunk_data.get('generation_token_count', 0)

                elif self.model_family == 'titan':
                    usage_tokens['prompt_tokens'] = chunk_data.get('inputTextTokenCount', 0)
                    results = chunk_data.get('results', [])
                    if results:
                        usage_tokens['completion_tokens'] = results[0].get('tokenCount', 0)

        usage_tokens['total_tokens'] = usage_tokens['prompt_tokens'] + usage_tokens['completion_tokens']

        # Calculate cost
        cost = pricing_model.get_cost(usage_tokens, model_name=self.model)

        from orchestral.llm.base.usage import Usage
        usage = Usage(
            model_name=self.model,
            tokens=usage_tokens,
            cost=cost
        )

        return Response(
            id='bedrock-streaming-response',
            model=self.model,
            message=message,
            usage=usage
        )

    def cleanup_stream(self):
        """Cleanup streaming resources when stream is interrupted."""
        if hasattr(self, '_event_stream'):
            try:
                # Close the event stream if it has a close method
                if hasattr(self._event_stream, 'close'):
                    self._event_stream.close()
            except Exception:
                pass  # Ignore cleanup errors
