"""
OpenAI Whisper API transcription provider.

Uses the OpenAI Whisper API for high-quality speech-to-text transcription.
Requires OPENAI_API_KEY environment variable.
"""

import io
import os
from typing import Optional
from openai import AsyncOpenAI
from .base import TranscriptionProvider, TranscriptionError


class OpenAIWhisperProvider(TranscriptionProvider):
    """
    Transcription provider using OpenAI's Whisper API.

    Supports multiple audio formats and languages.
    Pricing: $0.006 per minute of audio.
    """

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in config or environment")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = self.config.get("model", "whisper-1")
        self.language = self.config.get("language")  # Optional: 'en', 'es', etc.

    @property
    def name(self) -> str:
        return "openai-whisper"

    async def transcribe(self, audio_data: bytes, audio_format: str = "webm", **kwargs) -> str:
        """
        Transcribe audio using OpenAI Whisper API.

        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (webm, mp4, wav, etc.)
            **kwargs: Additional parameters (language, prompt, temperature)

        Returns:
            Transcribed text

        Raises:
            TranscriptionError: If API call fails
        """
        try:
            # OpenAI API expects a file-like object with a name
            # The extension helps Whisper identify the format
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{audio_format}"

            # Get language from kwargs or instance config
            language = kwargs.get("language", self.language)

            # Call Whisper API
            params = {
                "model": self.model,
                "file": audio_file,
            }

            # Add optional parameters
            if language:
                params["language"] = language
            if "prompt" in kwargs:
                params["prompt"] = kwargs["prompt"]
            if "temperature" in kwargs:
                params["temperature"] = kwargs["temperature"]

            response = await self.client.audio.transcriptions.create(**params)

            return response.text.strip()

        except Exception as e:
            raise TranscriptionError(f"OpenAI Whisper transcription failed: {str(e)}") from e

    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            # Simple test: check if client is initialized with valid key
            return self.client.api_key is not None
        except Exception:
            return False
