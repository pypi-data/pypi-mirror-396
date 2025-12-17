"""
Model details for Groq models.

Contains context window sizes and pricing information.
"""

MODEL_DETAILS = {
    # Llama 4 models
    'meta-llama/llama-4-scout-17b-16e-instruct': {
        'friendly_name': 'Llama 4 Scout 17B',
        'context_window': 128000,
        'output_limit': 32768,
    },
    'meta-llama/llama-4-maverick-17b-128e-instruct': {
        'friendly_name': 'Llama 4 Maverick 17B',
        'context_window': 128000,
        'output_limit': 32768,
    },

    # Llama 3 models
    'llama-3.3-70b-versatile': {
        'friendly_name': 'Llama 3.3 70B',
        'context_window': 128000,
        'output_limit': 32768,
    },
    'llama-3.1-8b-instant': {
        'friendly_name': 'Llama 3.1 8B',
        'context_window': 128000,
        'output_limit': 8192,
    },
    'meta-llama/llama-guard-4-12b': {
        'friendly_name': 'Llama Guard 4 12B',
        'context_window': 128000,
        'output_limit': 8192,
    },

    # GPT-OSS models
    'openai/gpt-oss-20b': {
        'friendly_name': 'GPT-OSS 20B',
        'context_window': 128000,
        'output_limit': 32768,
    },
    'openai/gpt-oss-safeguard-20b': {
        'friendly_name': 'GPT-OSS Safeguard 20B',
        'context_window': 128000,
        'output_limit': 32768,
    },
    'openai/gpt-oss-120b': {
        'friendly_name': 'GPT-OSS 120B',
        'context_window': 128000,
        'output_limit': 32768,
    },

    # Qwen models
    'qwen/qwen3-32b': {
        'friendly_name': 'Qwen 3 32B',
        'context_window': 131000,
        'output_limit': 32768,
    },

    # Kimi models
    'kimi/k2-0905-1t': {
        'friendly_name': 'Kimi K2 0905 1T',
        'context_window': 256000,
        'output_limit': 32768,
    },
}


def get_context_window(model_name: str) -> int:
    """Get the context window size for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('context_window', 128000)  # Default to 128K


def get_output_limit(model_name: str) -> int:
    """Get the maximum output tokens for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('output_limit', 8192)
