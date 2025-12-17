from orchestral.llm.base.usage import PricingModel

pricing_model = PricingModel(
    {
        # GPT-5 family
        'gpt-5.1':       {'prompt_tokens': 1.25,  'cached_prompt_tokens': 0.125,  'completion_tokens': 10.00},
        'gpt-5':         {'prompt_tokens': 1.25,  'cached_prompt_tokens': 0.125,  'completion_tokens': 10.00},
        'gpt-5-mini':    {'prompt_tokens': 0.25,  'cached_prompt_tokens': 0.025,  'completion_tokens': 2.00},
        'gpt-5-nano':    {'prompt_tokens': 0.05,  'cached_prompt_tokens': 0.005,  'completion_tokens': 0.40},

        # GPT-4.1 family
        'gpt-4.1':       {'prompt_tokens': 2.00,  'cached_prompt_tokens': 0.50,   'completion_tokens': 8.00},
        'gpt-4.1-mini':  {'prompt_tokens': 0.40,  'cached_prompt_tokens': 0.10,   'completion_tokens': 1.60},
        'gpt-4.1-nano':  {'prompt_tokens': 0.10,  'cached_prompt_tokens': 0.025,  'completion_tokens': 0.40},

        # GPT-4o family
        'gpt-4o':        {'prompt_tokens': 2.50,  'cached_prompt_tokens': 1.25,   'completion_tokens': 10.00},
        'gpt-4o-mini':   {'prompt_tokens': 0.15,  'cached_prompt_tokens': 0.075,  'completion_tokens': 0.60},

        # o-series reasoning models
        'o1':            {'prompt_tokens': 15.00, 'cached_prompt_tokens': 7.50,   'completion_tokens': 60.00},
        'o1-mini':       {'prompt_tokens': 1.10,  'cached_prompt_tokens': 0.55,   'completion_tokens': 4.40},
        'o3':            {'prompt_tokens': 2.00,  'cached_prompt_tokens': 0.50,   'completion_tokens': 8.00},
        'o3-mini':       {'prompt_tokens': 1.10,  'cached_prompt_tokens': 0.55,   'completion_tokens': 4.40},
        'o4-mini':       {'prompt_tokens': 1.10,  'cached_prompt_tokens': 0.275,  'completion_tokens': 4.40},
    }
)