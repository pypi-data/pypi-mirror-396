from orchestral.llm.base.usage import PricingModel

pricing_model = PricingModel(
    {
        # Gemini 2.0 models (per million tokens)
        'gemini-2.0-flash-exp':              {'prompt_tokens': 0.00,  'completion_tokens': 0.00},  # Free during preview
        'gemini-2.0-flash-thinking-exp':     {'prompt_tokens': 0.00,  'completion_tokens': 0.00},  # Free during preview

        # Gemini 1.5 models (per million tokens)
        'gemini-1.5-pro':                    {'prompt_tokens': 1.25,  'completion_tokens': 5.00},
        'gemini-1.5-pro-latest':             {'prompt_tokens': 1.25,  'completion_tokens': 5.00},
        'gemini-1.5-flash':                  {'prompt_tokens': 0.075, 'completion_tokens': 0.30},
        'gemini-1.5-flash-latest':           {'prompt_tokens': 0.075, 'completion_tokens': 0.30},
        'gemini-1.5-flash-8b':               {'prompt_tokens': 0.0375,'completion_tokens': 0.15},
        'gemini-1.5-flash-8b-latest':        {'prompt_tokens': 0.0375,'completion_tokens': 0.15},

        # Gemini 1.0 models
        'gemini-1.0-pro':                    {'prompt_tokens': 0.50,  'completion_tokens': 1.50},
        'gemini-1.0-pro-latest':             {'prompt_tokens': 0.50,  'completion_tokens': 1.50},
    }
)
