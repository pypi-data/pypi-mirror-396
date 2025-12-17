"""
Voice transcription WebSocket handler.

Handles voice transcription requests from the browser.
"""

from fastapi import WebSocket
from app.state import AppState
from app.voice import get_transcription_service, parse_audio_data, AudioError, TranscriptionError


async def handle_voice_transcribe(websocket: WebSocket, data: dict, state: AppState):
    """
    Handle voice transcription request.

    Message format:
    {
        "type": "voice_transcribe",
        "audio_data": "base64-encoded-audio",
        "format": "webm",  // or MIME type like "audio/webm"
        "language": "en"   // optional
    }

    Response:
    {
        "type": "transcription",
        "text": "transcribed text"
    }

    Or error:
    {
        "type": "error",
        "error": "error message"
    }

    Args:
        websocket: WebSocket connection
        data: Message data containing audio_data and format
        state: Application state (unused for transcription)
    """
    try:
        print("[Voice] Received transcription request")

        # Parse and validate audio data
        audio_bytes, audio_format = parse_audio_data(data)
        language = data.get("language")  # Optional language hint

        print(f"[Voice] Audio size: {len(audio_bytes)} bytes, format: {audio_format}")

        # Get transcription service
        service = get_transcription_service()

        # Transcribe audio
        text = await service.transcribe(
            audio_data=audio_bytes,
            audio_format=audio_format,
            language=language
        )

        # Send transcription result
        await websocket.send_json({
            "type": "transcription",
            "text": text
        })

        print(f"[Voice] Transcription complete: {len(text)} characters")

    except AudioError as e:
        error_msg = f"Audio processing error: {str(e)}"
        print(f"[Voice] {error_msg}")
        await websocket.send_json({
            "type": "error",
            "error": error_msg
        })

    except TranscriptionError as e:
        error_msg = f"Transcription failed: {str(e)}"
        print(f"[Voice] {error_msg}")
        await websocket.send_json({
            "type": "error",
            "error": error_msg
        })

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"[Voice] {error_msg}")
        await websocket.send_json({
            "type": "error",
            "error": error_msg
        })
