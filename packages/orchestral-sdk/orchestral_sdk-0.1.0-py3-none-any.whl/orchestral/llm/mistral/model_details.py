"""
Model details for Mistral AI models.

Contains context window sizes and output limits for Mistral models.
"""

MODEL_DETAILS = {
    # Mistral Large family
    'mistral-large-latest': {
        'friendly_name': 'Mistral Large',
        'context_window': 128000,
        'output_limit': 8192,
    },
    'mistral-large-2411': {
        'friendly_name': 'Mistral Large 2 (2411)',
        'context_window': 128000,
        'output_limit': 8192,
    },
    'mistral-large-2407': {
        'friendly_name': 'Mistral Large 2 (2407)',
        'context_window': 128000,
        'output_limit': 8192,
    },

    # Mistral Medium (deprecated but may still be used)
    'mistral-medium-latest': {
        'friendly_name': 'Mistral Medium',
        'context_window': 32000,
        'output_limit': 8192,
    },

    # Mistral Small family
    'mistral-small-latest': {
        'friendly_name': 'Mistral Small',
        'context_window': 32000,
        'output_limit': 8192,
    },
    'mistral-small-2409': {
        'friendly_name': 'Mistral Small (2409)',
        'context_window': 32000,
        'output_limit': 8192,
    },

    # Mistral NeMo (Nvidia partnership)
    'open-mistral-nemo': {
        'friendly_name': 'Mistral NeMo',
        'context_window': 128000,
        'output_limit': 8192,
    },
    'open-mistral-nemo-2407': {
        'friendly_name': 'Mistral NeMo (2407)',
        'context_window': 128000,
        'output_limit': 8192,
    },

    # Codestral (code generation)
    'codestral-latest': {
        'friendly_name': 'Codestral',
        'context_window': 32000,
        'output_limit': 8192,
    },
    'codestral-2405': {
        'friendly_name': 'Codestral (2405)',
        'context_window': 32000,
        'output_limit': 8192,
    },

    # Open Mistral family (older)
    'open-mistral-7b': {
        'friendly_name': 'Mistral 7B',
        'context_window': 32000,
        'output_limit': 8192,
    },
    'open-mixtral-8x7b': {
        'friendly_name': 'Mixtral 8x7B',
        'context_window': 32000,
        'output_limit': 8192,
    },
    'open-mixtral-8x22b': {
        'friendly_name': 'Mixtral 8x22B',
        'context_window': 64000,
        'output_limit': 8192,
    },

    # Mistral Tiny (deprecated)
    'mistral-tiny': {
        'friendly_name': 'Mistral Tiny',
        'context_window': 32000,
        'output_limit': 8192,
    },
}


def get_context_window(model_name: str) -> int:
    """Get the context window size for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('context_window', 32000)  # Default to 32K


def get_output_limit(model_name: str) -> int:
    """Get the maximum output tokens for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('output_limit', 8192)  # Default to 8K
