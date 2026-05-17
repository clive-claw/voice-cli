"""Text-to-speech using Kokoro."""

import io
import wave
from typing import Optional

import numpy as np

from .async_mlx_model import AsyncMLXModel

_SAMPLE_RATE = 24000


def _load_kokoro():
    """Load Kokoro model synchronously; return None on failure."""
    try:
        from kokoro import build
        return build("kokoro-v0_19.pth", device="cpu")
    except Exception:
        try:
            import kokoro
            return kokoro.build()
        except Exception:
            return None


def _synthesize(model, text: str) -> Optional[bytes]:
    """Generate WAV bytes from text using the loaded Kokoro model."""
    audio = model(text, voice="af", speed=1.0)

    if isinstance(audio, list):
        audio = np.array(audio)

    if audio.dtype != np.int16:
        audio = np.clip(audio * 32767, -32768, 32767).astype(np.int16)

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)   # Mono
        wav_file.setsampwidth(2)   # 16-bit
        wav_file.setframerate(_SAMPLE_RATE)
        wav_file.writeframes(audio.tobytes())

    return wav_buffer.getvalue()


class TextToSpeech:
    """Generate speech using Kokoro TTS."""

    def __init__(self):
        self._wrapper: AsyncMLXModel[str, Optional[bytes]] = AsyncMLXModel(
            loader=_load_kokoro,
            transform=_synthesize,
        )

    async def initialize(self) -> None:
        """Load Kokoro model."""
        await self._wrapper.initialize()

    async def synthesize(self, text: str) -> Optional[bytes]:
        """Generate speech from text, return WAV bytes."""
        if not text or self._wrapper._model is None:
            return None
        try:
            return await self._wrapper.run(text)
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(str(e)) from e
