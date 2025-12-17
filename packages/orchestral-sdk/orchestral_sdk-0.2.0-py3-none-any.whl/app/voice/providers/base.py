"""
Base abstract class for voice transcription providers.

This module defines the interface that all transcription providers must implement,
allowing the system to swap between different speech-to-text services with minimal code changes.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class TranscriptionProvider(ABC):
    """
    Abstract base class for all transcription providers.

    Providers must implement the transcribe method to convert audio data to text.
    This allows for easy switching between OpenAI Whisper, local Whisper,
    Google Speech-to-Text, or other services.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the transcription provider.

        Args:
            config: Optional configuration dictionary specific to the provider
        """
        self.config = config or {}

    @abstractmethod
    async def transcribe(self, audio_data: bytes, audio_format: str = "webm", **kwargs) -> str:
        """
        Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes from the browser
            audio_format: Audio format (e.g., "webm", "mp4", "wav", "ogg")
            **kwargs: Additional provider-specific parameters (language, model, etc.)

        Returns:
            Transcribed text string

        Raises:
            TranscriptionError: If transcription fails
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name for logging/debugging."""
        pass

    async def health_check(self) -> bool:
        """
        Check if the provider is available and healthy.

        Returns:
            True if provider is ready, False otherwise
        """
        return True


class TranscriptionError(Exception):
    """Raised when transcription fails."""
    pass
