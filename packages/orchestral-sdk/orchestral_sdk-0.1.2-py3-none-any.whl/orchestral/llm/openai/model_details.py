"""
Model details for OpenAI models.

Contains context window sizes and pricing information.
"""

MODEL_DETAILS = {
    # GPT-5 family
    'gpt-5.1': {
        'friendly_name': 'GPT-5.1',
        'context_window': 400000,
        'output_limit': 128000,
    },
    'gpt-5': {
        'friendly_name': 'GPT-5',
        'context_window': 400000,
        'output_limit': 128000,
    },
    'gpt-5-mini': {
        'friendly_name': 'GPT-5-mini',
        'context_window': 400000,
        'output_limit': 128000,
    },
    'gpt-5-nano': {
        'friendly_name': 'GPT-5-nano',
        'context_window': 400000,
        'output_limit': 128000,
    },

    # GPT-4.1 family
    'gpt-4.1': {
        'friendly_name': 'GPT-4.1',
        'context_window': 1000000,
        'output_limit': 100000,
    },
    'gpt-4.1-2025-04-14': {
        'friendly_name': 'GPT-4.1',
        'context_window': 1000000,
        'output_limit': 100000,
    },
    'gpt-4.1-mini': {
        'friendly_name': 'GPT-4.1-mini',
        'context_window': 1000000,
        'output_limit': 100000,
    },
    'gpt-4.1-mini-2025-04-14': {
        'friendly_name': 'GPT-4.1-mini',
        'context_window': 1000000,
        'output_limit': 100000,
    },
    'gpt-4.1-nano': {
        'friendly_name': 'GPT-4.1-nano',
        'context_window': 1000000,
        'output_limit': 100000,
    },

    # GPT-4o family
    'gpt-4o': {
        'friendly_name': 'GPT-4o',
        'context_window': 128000,
        'output_limit': 16384,
    },
    'gpt-4o-2024-08-06': {
        'friendly_name': 'GPT-4o',
        'context_window': 128000,
        'output_limit': 16384,
    },
    'gpt-4o-mini': {
        'friendly_name': 'GPT-4o-mini',
        'context_window': 128000,
        'output_limit': 16384,
    },
    'gpt-4o-mini-2024-07-18': {
        'friendly_name': 'GPT-4o-mini',
        'context_window': 128000,
        'output_limit': 16384,
    },

    # o-series reasoning models
    'o1': {
        'friendly_name': 'o1',
        'context_window': 200000,
        'output_limit': 100000,
    },
    'o1-mini': {
        'friendly_name': 'o1-mini',
        'context_window': 128000,
        'output_limit': 65536,
    },
    'o3': {
        'friendly_name': 'o3',
        'context_window': 128000,
        'output_limit': 100000,
    },
    'o3-mini': {
        'friendly_name': 'o3-mini',
        'context_window': 200000,
        'output_limit': 100000,
    },
    'o4-mini': {
        'friendly_name': 'o4-mini',
        'context_window': 128000,
        'output_limit': 100000,
    },
}


def get_context_window(model_name: str) -> int:
    """Get the context window size for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('context_window', 128000)  # Default to 128K


def get_output_limit(model_name: str) -> int:
    """Get the maximum output tokens for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('output_limit', 16384)  # Default to 16K
