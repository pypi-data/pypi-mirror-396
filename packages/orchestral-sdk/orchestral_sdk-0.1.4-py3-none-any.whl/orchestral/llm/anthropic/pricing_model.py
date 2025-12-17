from orchestral.llm.base.usage import PricingModel

pricing_model = PricingModel(
    {
        # === Exact Anthropic API Model IDs ===
        # Rates are per million tokens in USD
        # Cache rates: 5m cache writes = 1.25x base, 1h cache writes = 2x base, cache hits = 0.1x base
        'claude-opus-4-1-20250805':     {
            'prompt_tokens': 15.00,
            'completion_tokens': 75.00,
            'cache_creation_input_tokens': 18.75,  # 5m cache writes: 1.25 × 15.00
            'cache_read_input_tokens': 1.50,       # cache hits: 0.1 × 15.00
        },
        'claude-opus-4-20250514':       {
            'prompt_tokens': 15.00,
            'completion_tokens': 75.00,
            'cache_creation_input_tokens': 18.75,
            'cache_read_input_tokens': 1.50,
        },
        'claude-sonnet-4-5-20250929':   {
            'prompt_tokens': 3.00,
            'completion_tokens': 15.00,
            'cache_creation_input_tokens': 3.75,   # 5m cache writes: 1.25 × 3.00
            'cache_read_input_tokens': 0.30,       # cache hits: 0.1 × 3.00
        },
        'claude-sonnet-4-20250514':     {
            'prompt_tokens': 3.00,
            'completion_tokens': 15.00,
            'cache_creation_input_tokens': 3.75,
            'cache_read_input_tokens': 0.30,
        },
        'claude-3-7-sonnet-20250219':   {
            'prompt_tokens': 3.00,
            'completion_tokens': 15.00,
            'cache_creation_input_tokens': 3.75,
            'cache_read_input_tokens': 0.30,
        },
        'claude-haiku-4-5-20251015':    {
            'prompt_tokens': 1.00,
            'completion_tokens': 5.00,
            'cache_creation_input_tokens': 1.25,   # 5m cache writes: 1.25 × 1.00
            'cache_read_input_tokens': 0.10,       # cache hits: 0.1 × 1.00
        },
        'claude-3-5-haiku-20241022':    {
            'prompt_tokens': 0.80,
            'completion_tokens': 4.00,
            'cache_creation_input_tokens': 1.00,   # 5m cache writes: 1.25 × 0.80
            'cache_read_input_tokens': 0.08,       # cache hits: 0.1 × 0.80
        },
        'claude-3-haiku-20240307':      {
            'prompt_tokens': 0.25,
            'completion_tokens': 1.25,
            'cache_creation_input_tokens': 0.30,   # 5m cache writes: 1.25 × 0.25 (rounded)
            'cache_read_input_tokens': 0.03,       # cache hits: 0.1 × 0.25 (rounded)
        },

        # === Alias Model Names (Convenience Only) ===
        'claude-opus-4-1':              {
            'prompt_tokens': 15.00,
            'completion_tokens': 75.00,
            'cache_creation_input_tokens': 18.75,
            'cache_read_input_tokens': 1.50,
        },
        'claude-opus-4-0':              {
            'prompt_tokens': 15.00,
            'completion_tokens': 75.00,
            'cache_creation_input_tokens': 18.75,
            'cache_read_input_tokens': 1.50,
        },
        'claude-sonnet-4-5':            {
            'prompt_tokens': 3.00,
            'completion_tokens': 15.00,
            'cache_creation_input_tokens': 3.75,
            'cache_read_input_tokens': 0.30,
        },
        'claude-sonnet-4-0':            {
            'prompt_tokens': 3.00,
            'completion_tokens': 15.00,
            'cache_creation_input_tokens': 3.75,
            'cache_read_input_tokens': 0.30,
        },
        'claude-3-7-sonnet-latest':     {
            'prompt_tokens': 3.00,
            'completion_tokens': 15.00,
            'cache_creation_input_tokens': 3.75,
            'cache_read_input_tokens': 0.30,
        },
        'claude-haiku-4-5':             {
            'prompt_tokens': 1.00,
            'completion_tokens': 5.00,
            'cache_creation_input_tokens': 1.25,
            'cache_read_input_tokens': 0.10,
        },
        'claude-3-5-haiku-latest':      {
            'prompt_tokens': 0.80,
            'completion_tokens': 4.00,
            'cache_creation_input_tokens': 1.00,
            'cache_read_input_tokens': 0.08,
        },
    }
)