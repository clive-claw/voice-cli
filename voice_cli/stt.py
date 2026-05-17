"""Speech-to-text using mlx-audio."""

import io
import wave
from typing import Optional

import numpy as np

from .async_mlx_model import AsyncMLXModel


def _load_whisper():
    """Load Whisper model synchronously; return None on failure."""
    try:
        from mlx_audio.models import load_model
        return load_model("whisper")
    except ImportError:
        try:
            import mlx_audio
            return mlx_audio.load("whisper")
        except Exception:
            return None


def _transcribe(model, audio_bytes: bytes) -> Optional[str]:
    """Transcribe WAV bytes to text using the loaded Whisper model."""
    with io.BytesIO(audio_bytes) as wav_buffer:
        with wave.open(wav_buffer, "rb") as wav_file:
            audio_data = wav_file.readframes(wav_file.getnframes())

    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    audio_float = audio_array.astype(np.float32) / 32767

    result = model.transcribe(audio_float)
    return result.get("text", "").strip() if result else None


class SpeechToText:
    """Transcribe audio to text using mlx-audio Whisper."""

    def __init__(self):
        self._wrapper: AsyncMLXModel[bytes, Optional[str]] = AsyncMLXModel(
            loader=_load_whisper,
            transform=_transcribe,
        )

    async def initialize(self) -> None:
        """Load the Whisper model (async wrapper)."""
        await self._wrapper.initialize()

    async def transcribe(self, audio_bytes: bytes) -> Optional[str]:
        """Transcribe WAV audio bytes to text."""
        if not audio_bytes:
            return None
        try:
            return await self._wrapper.run(audio_bytes)
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(str(e)) from e
