"""Speech-to-text using mlx-audio."""

import asyncio
import io
import wave
from typing import Optional
from mlx_audio.models import load_model as load_stt_model


class SpeechToText:
    """Transcribe audio to text using mlx-audio Whisper."""

    def __init__(self):
        self.model = None

    async def initialize(self) -> None:
        """Load the Whisper model (async wrapper)."""
        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(None, self._load_model)

    def _load_model(self):
        """Load Whisper model synchronously."""
        try:
            return load_stt_model("whisper")
        except Exception:
            return None

    async def transcribe(self, audio_bytes: bytes) -> Optional[str]:
        """Transcribe WAV audio bytes to text."""
        if not audio_bytes:
            return None

        loop = asyncio.get_event_loop()

        def transcribe_sync():
            """Transcribe audio synchronously."""
            if self.model is None:
                return None

            try:
                # Parse WAV bytes to numpy array
                with io.BytesIO(audio_bytes) as wav_buffer:
                    with wave.open(wav_buffer, "rb") as wav_file:
                        sample_rate = wav_file.getframerate()
                        audio_data = wav_file.readframes(wav_file.getnframes())
                        import numpy as np

                        audio_array = np.frombuffer(audio_data, dtype=np.int16)
                        audio_float = audio_array.astype(np.float32) / 32767

                        # Transcribe
                        result = self.model.transcribe(audio_float)
                        return result.get("text", "").strip() if result else None
            except Exception as e:
                return None

        return await loop.run_in_executor(None, transcribe_sync)
