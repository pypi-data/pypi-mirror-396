"""
Voice transcription providers.

Available providers:
- OpenAIWhisperProvider: Uses OpenAI's Whisper API
- LocalWhisperProvider: Uses local Whisper model
"""

from .base import TranscriptionProvider, TranscriptionError
from .openai_whisper import OpenAIWhisperProvider
from .local_whisper import LocalWhisperProvider

__all__ = [
    "TranscriptionProvider",
    "TranscriptionError",
    "OpenAIWhisperProvider",
    "LocalWhisperProvider",
]
