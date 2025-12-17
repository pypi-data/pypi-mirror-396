# LLM package - convenient imports for main clients
from orchestral.llm.openai.client import GPT
from orchestral.llm.anthropic.client import Claude
from orchestral.llm.google.client import Gemini
from orchestral.llm.ollama.client import Ollama
from orchestral.llm.groq.client import Groq
from orchestral.llm.mistral.client import MistralAI
from orchestral.llm.bedrock.client import Bedrock
from orchestral.llm.base.llm import LLM
from orchestral.llm.routers import CheapLLM

__all__ = ['GPT', 'Claude', 'Gemini', 'Ollama', 'Groq', 'MistralAI', 'Bedrock', 'LLM', 'CheapLLM', 'get_available_models']


def get_available_models():
    """
    Get all available models across all providers.

    Returns:
        dict: Dictionary organized by provider with model details.
            Example:
            {
                'openai': [
                    {'model_id': 'gpt-4o-mini', 'friendly_name': 'GPT-4o-mini', ...},
                    ...
                ],
                'anthropic': [...],
                ...
            }
    """
    from orchestral.llm.anthropic.model_details import MODEL_DETAILS as anthropic_models
    from orchestral.llm.openai.model_details import MODEL_DETAILS as openai_models
    from orchestral.llm.google.model_details import MODEL_DETAILS as google_models
    from orchestral.llm.groq.model_details import MODEL_DETAILS as groq_models
    from orchestral.llm.mistral.model_details import MODEL_DETAILS as mistral_models
    from orchestral.llm.bedrock.model_details import MODEL_DETAILS as bedrock_models

    def format_models(models_dict, provider):
        """Convert model details dict to list format for API."""
        result = []
        seen_names = set()  # Avoid duplicates with same friendly_name

        for model_id, details in models_dict.items():
            friendly_name = details.get('friendly_name', model_id)

            # Skip duplicates (e.g., dated versions with same friendly name)
            if friendly_name in seen_names:
                continue
            seen_names.add(friendly_name)

            result.append({
                'model_id': model_id,
                'friendly_name': friendly_name,
                'context_window': details.get('context_window', 0),
                'output_limit': details.get('output_limit', 0),
            })

        return result

    return {
        'openai': format_models(openai_models, 'openai'),
        'anthropic': format_models(anthropic_models, 'anthropic'),
        'google': format_models(google_models, 'google'),
        'groq': format_models(groq_models, 'groq'),
        'mistral': format_models(mistral_models, 'mistral'),
        'bedrock': format_models(bedrock_models, 'bedrock'),
    }