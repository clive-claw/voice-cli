"""Text-to-speech using kokoro-onnx."""

import io
import os
import wave
from pathlib import Path
from typing import Optional

import numpy as np

from .async_mlx_model import AsyncMLXModel

_SAMPLE_RATE = 24000
_MODEL_PATH = Path.home() / ".voice-cli" / "models" / "kokoro-v1.0.onnx"
_VOICES_PATH = Path.home() / ".voice-cli" / "models" / "voices-v1.0.bin"
_DEFAULT_VOICE = "af_heart"


def _load_kokoro():
    """Load Kokoro ONNX model synchronously; return None on failure."""
    try:
        from kokoro_onnx import Kokoro  # type: ignore
        return Kokoro(str(_MODEL_PATH), str(_VOICES_PATH))
    except Exception:
        return None


def _synthesize(model, text: str) -> Optional[bytes]:
    """Generate WAV bytes from text using the loaded kokoro-onnx model."""
    voice = os.environ.get("VOICE_CLI_VOICE", _DEFAULT_VOICE)
    audio, sr = model.create(text, voice=voice, speed=1.0)

    pcm = np.clip(audio * 32767, -32768, 32767).astype(np.int16)

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)   # Mono
        wav_file.setsampwidth(2)   # 16-bit
        wav_file.setframerate(sr)
        wav_file.writeframes(pcm.tobytes())

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
        if not text:
            return None
        try:
            return await self._wrapper.run(text)
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(str(e)) from e
