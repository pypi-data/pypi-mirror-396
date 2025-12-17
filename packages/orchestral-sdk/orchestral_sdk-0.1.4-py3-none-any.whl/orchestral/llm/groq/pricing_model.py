from orchestral.llm.base.usage import PricingModel

# Groq pricing as of 2025
# Source: https://groq.com/pricing
# Note: Only active, non-deprecated models are included
pricing_model = PricingModel(
    {
        # Llama 4 models (active)
        'meta-llama/llama-4-scout-17b-16e-instruct':     {'prompt_tokens': 0.11, 'completion_tokens': 0.34},
        'meta-llama/llama-4-maverick-17b-128e-instruct': {'prompt_tokens': 0.20, 'completion_tokens': 0.60},

        # Llama 3 models (active)
        'llama-3.3-70b-versatile':          {'prompt_tokens': 0.59, 'completion_tokens': 0.79},
        'llama-3.1-8b-instant':             {'prompt_tokens': 0.05, 'completion_tokens': 0.08},
        'meta-llama/llama-guard-4-12b':     {'prompt_tokens': 0.20, 'completion_tokens': 0.20},

        # GPT-OSS models (active)
        'openai/gpt-oss-20b':               {'prompt_tokens': 0.075, 'completion_tokens': 0.30},
        'openai/gpt-oss-safeguard-20b':     {'prompt_tokens': 0.075, 'completion_tokens': 0.30},
        'openai/gpt-oss-120b':              {'prompt_tokens': 0.15, 'completion_tokens': 0.60},

        # Qwen models (active)
        'qwen/qwen3-32b':                   {'prompt_tokens': 0.29, 'completion_tokens': 0.59},

        # Kimi models (active)
        'kimi/k2-0905-1t':                  {'prompt_tokens': 1.00, 'completion_tokens': 3.00},
    }
)
