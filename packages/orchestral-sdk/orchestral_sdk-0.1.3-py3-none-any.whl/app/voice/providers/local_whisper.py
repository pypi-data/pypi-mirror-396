"""
Local Whisper transcription provider.

Uses OpenAI's open-source Whisper model running locally.
Requires: pip install openai-whisper (or faster-whisper for better performance)
"""

import tempfile
import os
from typing import Optional
from .base import TranscriptionProvider, TranscriptionError


class LocalWhisperProvider(TranscriptionProvider):
    """
    Transcription provider using local Whisper model.

    Requires downloading Whisper models (tiny, base, small, medium, large).
    Model sizes: tiny=39MB, base=74MB, small=244MB, medium=769MB, large=1550MB

    Install: pip install openai-whisper
    Or for faster inference: pip install faster-whisper
    """

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.model_size = self.config.get("model_size", "base")  # tiny, base, small, medium, large
        self.use_faster = self.config.get("use_faster_whisper", False)
        self.device = self.config.get("device", "cpu")  # cpu or cuda
        self.model = None

    @property
    def name(self) -> str:
        return f"local-whisper-{self.model_size}"

    def _load_model(self):
        """Lazy load the Whisper model."""
        if self.model is not None:
            return

        try:
            if self.use_faster:
                # faster-whisper (CTranslate2-based, more efficient)
                from faster_whisper import WhisperModel
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type="int8" if self.device == "cpu" else "float16"
                )
            else:
                # Standard openai-whisper
                import whisper
                self.model = whisper.load_model(self.model_size, device=self.device)

        except ImportError as e:
            raise TranscriptionError(
                f"Whisper library not installed. "
                f"Install with: pip install {'faster-whisper' if self.use_faster else 'openai-whisper'}"
            ) from e

    async def transcribe(self, audio_data: bytes, audio_format: str = "webm", **kwargs) -> str:
        """
        Transcribe audio using local Whisper model.

        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (webm, mp4, wav, etc.)
            **kwargs: Additional parameters (language, task)

        Returns:
            Transcribed text

        Raises:
            TranscriptionError: If transcription fails
        """
        try:
            self._load_model()

            # Write audio to temporary file (Whisper needs file path)
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name

            try:
                language = kwargs.get("language")
                task = kwargs.get("task", "transcribe")  # "transcribe" or "translate"

                if self.use_faster:
                    # faster-whisper API
                    segments, info = self.model.transcribe(
                        temp_audio_path,
                        language=language,
                        task=task
                    )
                    text = " ".join([segment.text for segment in segments])
                else:
                    # Standard whisper API
                    result = self.model.transcribe(
                        temp_audio_path,
                        language=language,
                        task=task
                    )
                    text = result["text"]

                return text.strip()

            finally:
                # Clean up temporary file
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)

        except Exception as e:
            raise TranscriptionError(f"Local Whisper transcription failed: {str(e)}") from e

    async def health_check(self) -> bool:
        """Check if Whisper library is available."""
        try:
            if self.use_faster:
                import faster_whisper
            else:
                import whisper
            return True
        except ImportError:
            return False
