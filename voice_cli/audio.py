"""Audio capture and playback."""

import asyncio
import io
import threading
import numpy as np
import sounddevice as sd
from typing import Tuple
import wave


class AudioCapture:
    """Record audio from microphone."""

    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    CHANNELS = 1

    async def record_until_signal(self, stop_event: threading.Event) -> bytes:
        """Record audio until stop_event is set. Returns WAV bytes.

        stop_event must be a threading.Event (not asyncio.Event) because
        record_chunk runs in a thread executor and asyncio.Event is not
        thread-safe.
        """
        loop = asyncio.get_event_loop()
        audio_buffer = []

        def record_chunk():
            """Record audio chunks in a thread until stop_event is set."""
            while not stop_event.is_set():
                # Record chunk synchronously
                chunk = sd.rec(
                    self.CHUNK_SIZE,
                    samplerate=self.SAMPLE_RATE,
                    channels=self.CHANNELS,
                    dtype=np.float32,
                )
                sd.wait()  # Wait for recording to complete
                audio_buffer.append(chunk)

        # Run recording in executor and wait for it to finish.
        # The caller is responsible for setting stop_event (via
        # loop.call_soon_threadsafe) to terminate the loop.
        await loop.run_in_executor(None, record_chunk)

        # Convert recorded chunks to WAV format
        if audio_buffer:
            audio_data = np.concatenate(audio_buffer)
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(self.CHANNELS)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.SAMPLE_RATE)
                # Convert float32 to int16
                int_audio = np.int16(audio_data * 32767)
                wav_file.writeframes(int_audio.tobytes())
            return wav_buffer.getvalue()

        return b""


class AudioPlayback:
    """Play audio to speakers."""

    async def play(self, audio_bytes: bytes) -> None:
        """Play audio buffer (WAV format) to speakers."""
        if not audio_bytes:
            return

        loop = asyncio.get_event_loop()

        def play_chunk():
            """Play audio synchronously."""
            with io.BytesIO(audio_bytes) as wav_buffer:
                with wave.open(wav_buffer, "rb") as wav_file:
                    sample_rate = wav_file.getframerate()
                    channels = wav_file.getnchannels()
                    audio_data = wav_file.readframes(wav_file.getnframes())
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    audio_float = audio_array.astype(np.float32) / 32767
                    # Play audio
                    sd.play(audio_float, samplerate=sample_rate)
                    sd.wait()

        await loop.run_in_executor(None, play_chunk)
