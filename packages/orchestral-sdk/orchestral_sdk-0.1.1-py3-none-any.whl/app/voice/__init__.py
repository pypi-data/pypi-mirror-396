"""
Voice transcription module for Orchestral.

Provides speech-to-text transcription with pluggable providers.

Usage:
    from app.voice import get_transcription_service

    service = get_transcription_service()
    text = await service.transcribe(audio_bytes, "webm")

Configuration:
    Set VOICE_PROVIDER environment variable to switch providers:
    - "openai" (default): OpenAI Whisper API
    - "local": Local Whisper model
"""

from .transcription_service import TranscriptionService, get_transcription_service
from .audio_utils import AudioError, parse_audio_data, validate_audio_format
from .providers.base import TranscriptionError

__all__ = [
    "TranscriptionService",
    "get_transcription_service",
    "AudioError",
    "TranscriptionError",
    "parse_audio_data",
    "validate_audio_format",
]
