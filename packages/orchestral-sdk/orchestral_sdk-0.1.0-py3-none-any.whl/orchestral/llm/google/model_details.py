"""
Model details for Google Gemini models.

Contains context window sizes and pricing information.
"""

MODEL_DETAILS = {
    'gemini-2.0-flash-exp': {
        'friendly_name': 'Gemini 2.0 Flash',
        'context_window': 1000000,  # 1M tokens
        'output_limit': 8192,
    },
    'gemini-1.5-pro': {
        'friendly_name': 'Gemini 1.5 Pro',
        'context_window': 2000000,  # 2M tokens
        'output_limit': 8192,
    },
    'gemini-1.5-flash': {
        'friendly_name': 'Gemini 1.5 Flash',
        'context_window': 1000000,  # 1M tokens
        'output_limit': 8192,
    },
    'gemini-1.5-flash-8b': {
        'friendly_name': 'Gemini 1.5 Flash-8B',
        'context_window': 1000000,  # 1M tokens
        'output_limit': 8192,
    },
    'gemini-1.0-pro': {
        'friendly_name': 'Gemini 1.0 Pro',
        'context_window': 32000,
        'output_limit': 8192,
    },
}


def get_context_window(model_name: str) -> int:
    """Get the context window size for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('context_window', 1000000)  # Default to 1M


def get_output_limit(model_name: str) -> int:
    """Get the maximum output tokens for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('output_limit', 8192)
