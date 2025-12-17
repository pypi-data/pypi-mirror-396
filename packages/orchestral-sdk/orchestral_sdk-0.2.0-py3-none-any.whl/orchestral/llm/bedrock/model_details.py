"""
Model details for AWS Bedrock models.

Contains context window sizes and model information for multiple model families
available through AWS Bedrock.
"""

MODEL_DETAILS = {
    # === Claude models via Bedrock ===
    'anthropic.claude-3-5-sonnet-20241022-v2:0': {
        'friendly_name': 'Claude 3.5 Sonnet v2',
        'context_window': 200000,
        'output_limit': 8192,
        'family': 'claude',
    },
    'anthropic.claude-3-5-sonnet-20240620-v1:0': {
        'friendly_name': 'Claude 3.5 Sonnet',
        'context_window': 200000,
        'output_limit': 8192,
        'family': 'claude',
    },
    'anthropic.claude-3-5-haiku-20241022-v1:0': {
        'friendly_name': 'Claude 3.5 Haiku',
        'context_window': 200000,
        'output_limit': 8192,
        'family': 'claude',
    },
    'anthropic.claude-3-opus-20240229-v1:0': {
        'friendly_name': 'Claude 3 Opus',
        'context_window': 200000,
        'output_limit': 4096,
        'family': 'claude',
    },
    'anthropic.claude-3-sonnet-20240229-v1:0': {
        'friendly_name': 'Claude 3 Sonnet',
        'context_window': 200000,
        'output_limit': 4096,
        'family': 'claude',
    },
    'anthropic.claude-3-haiku-20240307-v1:0': {
        'friendly_name': 'Claude 3 Haiku',
        'context_window': 200000,
        'output_limit': 4096,
        'family': 'claude',
    },

    # === Llama models via Bedrock ===
    'meta.llama3-3-70b-instruct-v1:0': {
        'friendly_name': 'Llama 3.3 70B Instruct',
        'context_window': 128000,
        'output_limit': 2048,
        'family': 'llama',
    },
    'meta.llama3-1-405b-instruct-v1:0': {
        'friendly_name': 'Llama 3.1 405B Instruct',
        'context_window': 128000,
        'output_limit': 2048,
        'family': 'llama',
    },
    'meta.llama3-1-70b-instruct-v1:0': {
        'friendly_name': 'Llama 3.1 70B Instruct',
        'context_window': 128000,
        'output_limit': 2048,
        'family': 'llama',
    },
    'meta.llama3-1-8b-instruct-v1:0': {
        'friendly_name': 'Llama 3.1 8B Instruct',
        'context_window': 128000,
        'output_limit': 2048,
        'family': 'llama',
    },
    'meta.llama3-70b-instruct-v1:0': {
        'friendly_name': 'Llama 3 70B Instruct',
        'context_window': 8192,
        'output_limit': 2048,
        'family': 'llama',
    },
    'meta.llama3-8b-instruct-v1:0': {
        'friendly_name': 'Llama 3 8B Instruct',
        'context_window': 8192,
        'output_limit': 2048,
        'family': 'llama',
    },

    # === Mistral models via Bedrock ===
    'mistral.mistral-large-2407-v1:0': {
        'friendly_name': 'Mistral Large 2 (24.07)',
        'context_window': 128000,
        'output_limit': 8192,
        'family': 'mistral',
    },
    'mistral.mistral-large-2402-v1:0': {
        'friendly_name': 'Mistral Large (24.02)',
        'context_window': 32000,
        'output_limit': 8192,
        'family': 'mistral',
    },
    'mistral.mistral-small-2402-v1:0': {
        'friendly_name': 'Mistral Small',
        'context_window': 32000,
        'output_limit': 8192,
        'family': 'mistral',
    },
    'mistral.mixtral-8x7b-instruct-v0:1': {
        'friendly_name': 'Mixtral 8x7B Instruct',
        'context_window': 32000,
        'output_limit': 8192,
        'family': 'mistral',
    },
    'mistral.mistral-7b-instruct-v0:2': {
        'friendly_name': 'Mistral 7B Instruct',
        'context_window': 32000,
        'output_limit': 8192,
        'family': 'mistral',
    },

    # === Cohere models via Bedrock ===
    'cohere.command-r-plus-v1:0': {
        'friendly_name': 'Command R+',
        'context_window': 128000,
        'output_limit': 4096,
        'family': 'cohere',
    },
    'cohere.command-r-v1:0': {
        'friendly_name': 'Command R',
        'context_window': 128000,
        'output_limit': 4096,
        'family': 'cohere',
    },

    # === Amazon Titan models via Bedrock ===
    'amazon.titan-text-premier-v1:0': {
        'friendly_name': 'Titan Text Premier',
        'context_window': 32000,
        'output_limit': 3072,
        'family': 'titan',
    },
    'amazon.titan-text-express-v1': {
        'friendly_name': 'Titan Text Express',
        'context_window': 8000,
        'output_limit': 8000,
        'family': 'titan',
    },
    'amazon.titan-text-lite-v1': {
        'friendly_name': 'Titan Text Lite',
        'context_window': 4000,
        'output_limit': 4000,
        'family': 'titan',
    },
}


def get_context_window(model_name: str) -> int:
    """Get the context window size for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('context_window', 200000)  # Default to 200K


def get_output_limit(model_name: str) -> int:
    """Get the maximum output tokens for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('output_limit', 4096)  # Conservative default


def get_model_family(model_name: str) -> str:
    """Get the model family (claude, llama, mistral, cohere, titan) for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('family', 'unknown')
