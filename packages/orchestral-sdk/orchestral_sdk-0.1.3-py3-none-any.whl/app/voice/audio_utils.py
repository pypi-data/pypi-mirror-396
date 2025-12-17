"""
Audio utilities for voice transcription.

Provides helpers for audio format validation, conversion, and processing.
"""

import base64
from typing import Tuple


# Supported audio formats
SUPPORTED_FORMATS = {
    "webm", "mp4", "mpeg", "mpga", "m4a", "wav", "ogg", "flac"
}

# Common MIME type mappings
MIME_TO_FORMAT = {
    "audio/webm": "webm",
    "audio/webm;codecs=opus": "webm",
    "audio/mp4": "mp4",
    "audio/mpeg": "mpeg",
    "audio/mpga": "mpga",
    "audio/m4a": "m4a",
    "audio/wav": "wav",
    "audio/wave": "wav",
    "audio/x-wav": "wav",
    "audio/ogg": "ogg",
    "audio/ogg;codecs=opus": "ogg",
    "audio/flac": "flac",
}


class AudioError(Exception):
    """Raised when audio processing fails."""
    pass


def validate_audio_format(audio_format: str) -> str:
    """
    Validate and normalize audio format.

    Args:
        audio_format: Audio format string (e.g., "webm", "audio/webm", "audio/webm; codecs=opus")

    Returns:
        Normalized format string (e.g., "webm")

    Raises:
        AudioError: If format is not supported
    """
    # Check if it's a MIME type
    if "/" in audio_format:
        # Remove any parameters (e.g., "; codecs=opus") and whitespace
        # "audio/webm; codecs=opus" -> "audio/webm"
        base_mime = audio_format.split(';')[0].strip().lower()

        # Try exact match first
        normalized = MIME_TO_FORMAT.get(base_mime)
        if normalized:
            return normalized
    else:
        # Direct format string
        normalized = audio_format.lower().strip(".")
        if normalized in SUPPORTED_FORMATS:
            return normalized

    raise AudioError(
        f"Unsupported audio format: {audio_format}. "
        f"Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
    )


def decode_base64_audio(base64_data: str) -> bytes:
    """
    Decode base64-encoded audio data.

    Args:
        base64_data: Base64-encoded audio string (may include data URI prefix)

    Returns:
        Raw audio bytes

    Raises:
        AudioError: If decoding fails
    """
    try:
        # Remove data URI prefix if present (e.g., "data:audio/webm;base64,...")
        if base64_data.startswith("data:"):
            # Split on comma to remove prefix
            if "," in base64_data:
                base64_data = base64_data.split(",", 1)[1]

        # Decode base64
        audio_bytes = base64.b64decode(base64_data)
        return audio_bytes

    except Exception as e:
        raise AudioError(f"Failed to decode base64 audio: {str(e)}") from e


def parse_audio_data(data: dict) -> Tuple[bytes, str]:
    """
    Parse audio data from WebSocket message.

    Expected format:
    {
        "audio_data": "base64-encoded-data",
        "format": "webm"  # or MIME type
    }

    Args:
        data: WebSocket message data

    Returns:
        Tuple of (audio_bytes, normalized_format)

    Raises:
        AudioError: If parsing fails or format is invalid
    """
    # Get audio data
    audio_data_b64 = data.get("audio_data")
    if not audio_data_b64:
        raise AudioError("Missing 'audio_data' in request")

    # Get format
    audio_format = data.get("format", "webm")

    # Decode audio
    audio_bytes = decode_base64_audio(audio_data_b64)

    # Validate format
    normalized_format = validate_audio_format(audio_format)

    # Sanity checks
    if len(audio_bytes) == 0:
        raise AudioError("Audio data is empty")

    # Check for suspiciously small audio files (likely silence)
    # WebM header alone is ~200 bytes, real audio should be much larger
    if len(audio_bytes) < 1000:
        raise AudioError("Audio too short - please record a longer message (at least 1 second)")

    return audio_bytes, normalized_format


def estimate_audio_duration(audio_bytes: bytes, audio_format: str) -> float:
    """
    Estimate audio duration in seconds (rough approximation).

    Note: This is a very rough estimate based on file size and format.
    For accurate duration, would need to parse audio headers.

    Args:
        audio_bytes: Raw audio data
        audio_format: Audio format

    Returns:
        Estimated duration in seconds
    """
    # Rough bitrate estimates (kbps) for different formats
    bitrate_estimates = {
        "webm": 32,  # WebM Opus typical
        "ogg": 64,   # OGG Vorbis typical
        "mp4": 128,  # M4A AAC typical
        "m4a": 128,
        "wav": 1411, # WAV uncompressed (44.1kHz stereo 16-bit)
        "flac": 700, # FLAC lossless typical
        "mpeg": 128, # MP3 typical
        "mpga": 128,
    }

    bitrate = bitrate_estimates.get(audio_format, 64)  # Default to 64 kbps
    file_size_kb = len(audio_bytes) / 1024
    duration_seconds = (file_size_kb * 8) / bitrate

    return duration_seconds
