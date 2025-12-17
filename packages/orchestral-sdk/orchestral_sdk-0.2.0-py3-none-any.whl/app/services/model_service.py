"""
Model service for extracting and managing model information.
"""

from typing import Optional, Dict
from app.state import AppState


def get_model_info(state: AppState) -> Optional[Dict[str, str]]:
    """
    Get the current model provider and name from the agent.

    Args:
        state: Application state

    Returns:
        Dict with 'provider' and 'model' keys, or None if no agent
    """
    if state.agent is None:
        return None

    model_name = state.agent.llm.model

    # Determine provider from LLM class name
    llm_class_name = state.agent.llm.__class__.__name__
    if llm_class_name == "Claude":
        provider = "anthropic"
    elif llm_class_name == "GPT":
        provider = "openai"
    elif llm_class_name == "Gemini":
        provider = "google"
    elif llm_class_name == "Ollama":
        provider = "ollama"
    elif llm_class_name == "Groq":
        provider = "groq"
    else:
        provider = "unknown"

    return {
        "provider": provider,
        "model": model_name
    }
