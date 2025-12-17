"""
AWS Bedrock provider for Orchestral.

Provides access to multiple model families through AWS Bedrock:
- Claude (Anthropic)
- Llama (Meta)
- Mistral
- Cohere
- Titan (Amazon)
"""

from orchestral.llm.bedrock.client import Bedrock

__all__ = ['Bedrock']
