"""
Pricing model for AWS Bedrock.

Rates are per million tokens in USD, based on AWS Bedrock pricing.
Source: https://aws.amazon.com/bedrock/pricing/
Last updated: December 2025
"""

from orchestral.llm.base.usage import PricingModel

pricing_model = PricingModel(
    {
        # === Claude models via Bedrock ===
        # Note: Bedrock pricing differs from direct Anthropic API pricing

        'anthropic.claude-3-5-sonnet-20241022-v2:0': {
            'prompt_tokens': 3.00,      # Input: $3.00 per 1M tokens
            'completion_tokens': 15.00,  # Output: $15.00 per 1M tokens
        },
        'anthropic.claude-3-5-sonnet-20240620-v1:0': {
            'prompt_tokens': 3.00,
            'completion_tokens': 15.00,
        },
        'anthropic.claude-3-5-haiku-20241022-v1:0': {
            'prompt_tokens': 1.00,      # Input: $1.00 per 1M tokens
            'completion_tokens': 5.00,   # Output: $5.00 per 1M tokens
        },
        'anthropic.claude-3-opus-20240229-v1:0': {
            'prompt_tokens': 15.00,     # Input: $15.00 per 1M tokens
            'completion_tokens': 75.00,  # Output: $75.00 per 1M tokens
        },
        'anthropic.claude-3-sonnet-20240229-v1:0': {
            'prompt_tokens': 3.00,
            'completion_tokens': 15.00,
        },
        'anthropic.claude-3-haiku-20240307-v1:0': {
            'prompt_tokens': 0.25,      # Input: $0.25 per 1M tokens
            'completion_tokens': 1.25,   # Output: $1.25 per 1M tokens
        },

        # === Llama models via Bedrock ===
        'meta.llama3-3-70b-instruct-v1:0': {
            'prompt_tokens': 0.99,      # Input: $0.99 per 1M tokens
            'completion_tokens': 0.99,   # Output: $0.99 per 1M tokens
        },
        'meta.llama3-1-405b-instruct-v1:0': {
            'prompt_tokens': 5.32,      # Input: $5.32 per 1M tokens
            'completion_tokens': 16.00,  # Output: $16.00 per 1M tokens
        },
        'meta.llama3-1-70b-instruct-v1:0': {
            'prompt_tokens': 0.99,
            'completion_tokens': 0.99,
        },
        'meta.llama3-1-8b-instruct-v1:0': {
            'prompt_tokens': 0.22,      # Input: $0.22 per 1M tokens
            'completion_tokens': 0.22,   # Output: $0.22 per 1M tokens
        },
        'meta.llama3-70b-instruct-v1:0': {
            'prompt_tokens': 2.65,      # Input: $2.65 per 1M tokens
            'completion_tokens': 3.50,   # Output: $3.50 per 1M tokens
        },
        'meta.llama3-8b-instruct-v1:0': {
            'prompt_tokens': 0.30,      # Input: $0.30 per 1M tokens
            'completion_tokens': 0.60,   # Output: $0.60 per 1M tokens
        },

        # === Mistral models via Bedrock ===
        'mistral.mistral-large-2407-v1:0': {
            'prompt_tokens': 3.00,      # Input: $3.00 per 1M tokens
            'completion_tokens': 9.00,   # Output: $9.00 per 1M tokens
        },
        'mistral.mistral-large-2402-v1:0': {
            'prompt_tokens': 8.00,      # Input: $8.00 per 1M tokens
            'completion_tokens': 24.00,  # Output: $24.00 per 1M tokens
        },
        'mistral.mistral-small-2402-v1:0': {
            'prompt_tokens': 1.00,      # Input: $1.00 per 1M tokens
            'completion_tokens': 3.00,   # Output: $3.00 per 1M tokens
        },
        'mistral.mixtral-8x7b-instruct-v0:1': {
            'prompt_tokens': 0.45,      # Input: $0.45 per 1M tokens
            'completion_tokens': 0.70,   # Output: $0.70 per 1M tokens
        },
        'mistral.mistral-7b-instruct-v0:2': {
            'prompt_tokens': 0.15,      # Input: $0.15 per 1M tokens
            'completion_tokens': 0.20,   # Output: $0.20 per 1M tokens
        },

        # === Cohere models via Bedrock ===
        'cohere.command-r-plus-v1:0': {
            'prompt_tokens': 3.00,      # Input: $3.00 per 1M tokens
            'completion_tokens': 15.00,  # Output: $15.00 per 1M tokens
        },
        'cohere.command-r-v1:0': {
            'prompt_tokens': 0.50,      # Input: $0.50 per 1M tokens
            'completion_tokens': 1.50,   # Output: $1.50 per 1M tokens
        },

        # === Amazon Titan models via Bedrock ===
        'amazon.titan-text-premier-v1:0': {
            'prompt_tokens': 0.50,      # Input: $0.50 per 1M tokens
            'completion_tokens': 1.50,   # Output: $1.50 per 1M tokens
        },
        'amazon.titan-text-express-v1': {
            'prompt_tokens': 0.20,      # Input: $0.20 per 1M tokens
            'completion_tokens': 0.60,   # Output: $0.60 per 1M tokens
        },
        'amazon.titan-text-lite-v1': {
            'prompt_tokens': 0.15,      # Input: $0.15 per 1M tokens
            'completion_tokens': 0.20,   # Output: $0.20 per 1M tokens
        },
    }
)
