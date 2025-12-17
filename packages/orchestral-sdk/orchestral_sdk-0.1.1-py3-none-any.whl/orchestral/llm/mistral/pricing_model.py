"""
Pricing model for Mistral AI.

Pricing is in USD per 1M tokens, based on Mistral's official pricing.
https://mistral.ai/technology/#pricing
"""

from orchestral.llm.base.usage import PricingModel

# Pricing in USD per 1M tokens
MISTRAL_PRICING = {
    # Mistral Large family - $2/$6 per 1M tokens
    'mistral-large-latest': {
        'prompt_tokens': 2.00,
        'completion_tokens': 6.00,
    },
    'mistral-large-2411': {
        'prompt_tokens': 2.00,
        'completion_tokens': 6.00,
    },
    'mistral-large-2407': {
        'prompt_tokens': 2.00,
        'completion_tokens': 6.00,
    },

    # Mistral Small family - $0.20/$0.60 per 1M tokens
    'mistral-small-latest': {
        'prompt_tokens': 0.20,
        'completion_tokens': 0.60,
    },
    'mistral-small-2409': {
        'prompt_tokens': 0.20,
        'completion_tokens': 0.60,
    },

    # Mistral NeMo - $0.15/$0.15 per 1M tokens (same price for input/output)
    'open-mistral-nemo': {
        'prompt_tokens': 0.15,
        'completion_tokens': 0.15,
    },
    'open-mistral-nemo-2407': {
        'prompt_tokens': 0.15,
        'completion_tokens': 0.15,
    },

    # Codestral - $0.20/$0.60 per 1M tokens
    'codestral-latest': {
        'prompt_tokens': 0.20,
        'completion_tokens': 0.60,
    },
    'codestral-2405': {
        'prompt_tokens': 0.20,
        'completion_tokens': 0.60,
    },

    # Open Mistral 7B - $0.25/$0.25 per 1M tokens
    'open-mistral-7b': {
        'prompt_tokens': 0.25,
        'completion_tokens': 0.25,
    },

    # Mixtral 8x7B - $0.70/$0.70 per 1M tokens
    'open-mixtral-8x7b': {
        'prompt_tokens': 0.70,
        'completion_tokens': 0.70,
    },

    # Mixtral 8x22B - $2.00/$6.00 per 1M tokens
    'open-mixtral-8x22b': {
        'prompt_tokens': 2.00,
        'completion_tokens': 6.00,
    },

    # Mistral Medium (deprecated) - $2.70/$8.10 per 1M tokens
    'mistral-medium-latest': {
        'prompt_tokens': 2.70,
        'completion_tokens': 8.10,
    },

    # Mistral Tiny (deprecated) - $0.25/$0.25 per 1M tokens
    'mistral-tiny': {
        'prompt_tokens': 0.25,
        'completion_tokens': 0.25,
    },
}


def get_pricing_model(model_name: str) -> PricingModel:
    """
    Get the pricing model for a specific Mistral model.

    Args:
        model_name: The Mistral model identifier

    Returns:
        PricingModel instance with the appropriate rates
    """
    rates = MISTRAL_PRICING.get(
        model_name,
        {'prompt_tokens': 0.20, 'completion_tokens': 0.60}  # Default to small pricing
    )

    return PricingModel(
        input_cost_per_million=rates['prompt_tokens'],
        output_cost_per_million=rates['completion_tokens']
    )
