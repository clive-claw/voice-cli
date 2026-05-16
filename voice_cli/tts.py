"""Text-to-speech using Kokoro."""

import asyncio
import io
import wave
from typing import Optional
import numpy as np


class TextToSpeech:
    """Generate speech using Kokoro TTS."""

    def __init__(self):
        self.model = None
        self.sample_rate = 24000

    async def initialize(self) -> None:
        """Load Kokoro model."""
        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(None, self._load_model)

    def _load_model(self):
        """Load Kokoro model synchronously."""
        try:
            # Import here to avoid hard dependency
            from kokoro import build

            return build("kokoro-v0_19.pth", device="cpu")
        except Exception:
            try:
                # Try alternative import path
                import kokoro

                return kokoro.build()
            except Exception:
                return None

    async def synthesize(self, text: str) -> Optional[bytes]:
        """Generate speech from text, return WAV bytes."""
        if not text or not self.model:
            return None

        loop = asyncio.get_event_loop()

        def synthesize_sync():
            """Generate speech synchronously."""
            try:
                # Call Kokoro model
                audio = self.model(text, voice="af", speed=1.0)

                # Convert to numpy if needed
                if isinstance(audio, list):
                    audio = np.array(audio)

                # Convert to WAV format
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, "wb") as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(self.sample_rate)

                    # Convert float32 to int16
                    if audio.dtype != np.int16:
                        audio = np.clip(audio * 32767, -32768, 32767).astype(np.int16)

                    wav_file.writeframes(audio.tobytes())

                return wav_buffer.getvalue()

            except Exception as e:
                return None

        return await loop.run_in_executor(None, synthesize_sync)
