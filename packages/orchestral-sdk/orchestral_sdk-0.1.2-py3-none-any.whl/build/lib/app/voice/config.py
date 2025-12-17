"""
Voice transcription configuration.

Change VOICE_PROVIDER to switch between transcription services.
"""

import os
from typing import Dict, Any, Optional


# ============================================================================
# PROVIDER SELECTION - Change this line to switch providers
# ============================================================================
VOICE_PROVIDER = os.getenv("VOICE_PROVIDER", "openai")  # "openai" or "local"


# ============================================================================
# Provider Registry
# ============================================================================
PROVIDER_CLASSES = {
    "openai": "app.voice.providers.openai_whisper.OpenAIWhisperProvider",
    "local": "app.voice.providers.local_whisper.LocalWhisperProvider",
}


# ============================================================================
# Provider-Specific Configurations
# ============================================================================
PROVIDER_CONFIGS: Dict[str, Dict[str, Any]] = {
    "openai": {
        # API key loaded from environment (OPENAI_API_KEY)
        "model": "whisper-1",
        "language": None,  # Auto-detect, or set to "en", "es", etc.
    },
    "local": {
        "model_size": "base",  # Options: tiny, base, small, medium, large
        "use_faster_whisper": False,  # Set to True for faster-whisper library
        "device": "cpu",  # "cpu" or "cuda"
    },
}


def get_provider_config(provider_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get configuration for the specified provider.

    Args:
        provider_name: Provider name (defaults to VOICE_PROVIDER)

    Returns:
        Provider configuration dictionary
    """
    provider = provider_name or VOICE_PROVIDER
    return PROVIDER_CONFIGS.get(provider, {})


def get_provider_class_path(provider_name: Optional[str] = None) -> str:
    """
    Get the import path for the specified provider.

    Args:
        provider_name: Provider name (defaults to VOICE_PROVIDER)

    Returns:
        Full import path to provider class

    Raises:
        ValueError: If provider not found
    """
    provider = provider_name or VOICE_PROVIDER
    if provider not in PROVIDER_CLASSES:
        available = ", ".join(PROVIDER_CLASSES.keys())
        raise ValueError(f"Unknown provider '{provider}'. Available: {available}")
    return PROVIDER_CLASSES[provider]
