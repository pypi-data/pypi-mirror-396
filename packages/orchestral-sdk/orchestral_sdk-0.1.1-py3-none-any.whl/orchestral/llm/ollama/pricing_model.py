from orchestral.llm.base.usage import PricingModel

# Ollama runs models locally, so pricing is $0
# However, we still track token usage for monitoring/debugging
pricing_model = PricingModel(
    {
        'gpt-oss:20b': {
            'prompt_tokens': 0.0,
            'completion_tokens': 0.0,
            'total_tokens': 0.0
        },
        # Add more models as needed - all free for local inference
        'llama3.2': {
            'prompt_tokens': 0.0,
            'completion_tokens': 0.0,
            'total_tokens': 0.0
        },
        'llama3.1': {
            'prompt_tokens': 0.0,
            'completion_tokens': 0.0,
            'total_tokens': 0.0
        },
        'mistral': {
            'prompt_tokens': 0.0,
            'completion_tokens': 0.0,
            'total_tokens': 0.0
        },
        # Default catch-all for any Ollama model
        'default': {
            'prompt_tokens': 0.0,
            'completion_tokens': 0.0,
            'total_tokens': 0.0
        }
    }
)
