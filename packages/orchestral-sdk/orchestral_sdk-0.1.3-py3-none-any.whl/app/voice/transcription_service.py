"""
Voice transcription service.

Main service for handling speech-to-text transcription with provider abstraction.
"""

import importlib
from typing import Optional, Dict, Any
from .config import VOICE_PROVIDER, get_provider_config, get_provider_class_path
from .providers.base import TranscriptionProvider, TranscriptionError


class TranscriptionService:
    """
    Main transcription service with provider abstraction.

    This service handles:
    - Dynamic provider loading based on configuration
    - Provider lifecycle management
    - Common transcription interface

    Example:
        service = TranscriptionService()
        text = await service.transcribe(audio_bytes, "webm")
    """

    def __init__(self, provider_name: Optional[str] = None, provider_config: Optional[Dict[str, Any]] = None):
        """
        Initialize transcription service.

        Args:
            provider_name: Provider to use (defaults to config.VOICE_PROVIDER)
            provider_config: Override provider configuration
        """
        self.provider_name = provider_name or VOICE_PROVIDER
        self.provider_config = provider_config or get_provider_config(self.provider_name)
        self._provider: Optional[TranscriptionProvider] = None

    def _load_provider(self) -> TranscriptionProvider:
        """
        Lazy load the transcription provider.

        Returns:
            Initialized TranscriptionProvider instance

        Raises:
            ValueError: If provider class cannot be loaded
        """
        if self._provider is not None:
            return self._provider

        try:
            # Get provider class path from config
            class_path = get_provider_class_path(self.provider_name)
            module_path, class_name = class_path.rsplit(".", 1)

            # Dynamically import provider class
            module = importlib.import_module(module_path)
            provider_class = getattr(module, class_name)

            # Instantiate provider
            self._provider = provider_class(config=self.provider_config)

            print(f"[Voice] Loaded transcription provider: {self._provider.name}")
            return self._provider

        except Exception as e:
            raise ValueError(f"Failed to load provider '{self.provider_name}': {str(e)}") from e

    async def transcribe(
        self,
        audio_data: bytes,
        audio_format: str = "webm",
        language: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Transcribe audio to text using the configured provider.

        Args:
            audio_data: Raw audio bytes from browser
            audio_format: Audio format (webm, mp4, wav, ogg, etc.)
            language: Optional language code (e.g., "en", "es", "fr")
            **kwargs: Additional provider-specific parameters

        Returns:
            Transcribed text string

        Raises:
            TranscriptionError: If transcription fails
        """
        provider = self._load_provider()

        # Add language to kwargs if provided
        if language:
            kwargs["language"] = language

        try:
            text = await provider.transcribe(audio_data, audio_format, **kwargs)
            print(f"[Voice] Transcribed {len(audio_data)} bytes -> {len(text)} chars using {provider.name}")
            return text

        except TranscriptionError:
            raise
        except Exception as e:
            raise TranscriptionError(f"Unexpected transcription error: {str(e)}") from e

    async def health_check(self) -> bool:
        """
        Check if the transcription service is healthy.

        Returns:
            True if provider is available and ready
        """
        try:
            provider = self._load_provider()
            return await provider.health_check()
        except Exception:
            return False

    @property
    def provider(self) -> Optional[TranscriptionProvider]:
        """Get the current provider instance (if loaded)."""
        return self._provider

    @property
    def is_loaded(self) -> bool:
        """Check if provider is already loaded."""
        return self._provider is not None


# Global service instance (singleton pattern)
_service_instance: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """
    Get the global transcription service instance.

    Returns:
        Singleton TranscriptionService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = TranscriptionService()
    return _service_instance
