"""
Model details for Anthropic Claude models.

Contains context window sizes and pricing information.
"""

MODEL_DETAILS = {
    # === Exact Anthropic API Model IDs ===
    'claude-opus-4-1-20250805': {
        'friendly_name': 'Claude Opus 4.1',
        'context_window': 200000,
        'output_limit': 32000,
    },
    'claude-opus-4-20250514': {
        'friendly_name': 'Claude Opus 4',
        'context_window': 200000,
        'output_limit': 32000,
    },
    'claude-sonnet-4-5-20250929': {
        'friendly_name': 'Claude Sonnet 4.5',
        'context_window': 200000,
        'output_limit': 16384,
    },
    'claude-sonnet-4-20250514': {
        'friendly_name': 'Claude Sonnet 4',
        'context_window': 200000,
        'output_limit': 16384,
    },
    'claude-3-7-sonnet-20250219': {
        'friendly_name': 'Claude Sonnet 3.7',
        'context_window': 200000,
        'output_limit': 16384,
    },
    'claude-haiku-4-5-20251015': {
        'friendly_name': 'Claude Haiku 4.5',
        'context_window': 200000,
        'output_limit': 64000,
    },
    'claude-3-5-haiku-20241022': {
        'friendly_name': 'Claude Haiku 3.5',
        'context_window': 200000,
        'output_limit': 8192,
    },
    'claude-3-haiku-20240307': {
        'friendly_name': 'Claude Haiku 3.0',
        'context_window': 200000,
        'output_limit': 4096,
    },

    # === Alias Model Names (Convenience Only) ===
    'claude-opus-4-1': {
        'friendly_name': 'Claude Opus 4.1',
        'context_window': 200000,
        'output_limit': 32000,
    },
    'claude-opus-4-0': {
        'friendly_name': 'Claude Opus 4',
        'context_window': 200000,
        'output_limit': 32000,
    },
    'claude-sonnet-4-5': {
        'friendly_name': 'Claude Sonnet 4.5',
        'context_window': 200000,
        'output_limit': 16384,
    },
    'claude-sonnet-4-0': {
        'friendly_name': 'Claude Sonnet 4',
        'context_window': 200000,
        'output_limit': 16384,
    },
    'claude-3-7-sonnet-latest': {
        'friendly_name': 'Claude Sonnet 3.7',
        'context_window': 200000,
        'output_limit': 16384,
    },
    'claude-haiku-4-5': {
        'friendly_name': 'Claude Haiku 4.5',
        'context_window': 200000,
        'output_limit': 64000,
    },
    'claude-3-5-haiku-latest': {
        'friendly_name': 'Claude Haiku 3.5',
        'context_window': 200000,
        'output_limit': 8192,
    },
}


def get_context_window(model_name: str) -> int:
    """Get the context window size for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('context_window', 200000)  # Default to 200K


def get_output_limit(model_name: str) -> int:
    """Get the maximum output tokens for a model."""
    details = MODEL_DETAILS.get(model_name, {})
    return details.get('output_limit', 8192)  # Conservative default
