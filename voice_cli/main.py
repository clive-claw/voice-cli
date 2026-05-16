"""Main voice CLI orchestrator."""

import asyncio
import sys
from .keyboard import KeyboardListener
from .audio import AudioCapture, AudioPlayback
from .stt import SpeechToText
from .subprocess_mgr import ClaudeSubprocess
from .response import ResponseCapture
from .tts import TextToSpeech
from .error import ErrorHandler


class VoiceCLI:
    """Main async orchestrator for voice-to-Claude pipeline."""

    def __init__(self):
        self.keyboard = KeyboardListener()
        self.audio_capture = AudioCapture()
        self.audio_playback = AudioPlayback()
        self.stt = SpeechToText()
        self.subprocess = ClaudeSubprocess()
        self.response_capture = ResponseCapture()
        self.tts = TextToSpeech()
        self.running = True

    async def initialize(self) -> None:
        """Initialize all modules."""
        try:
            print("Initializing Voice CLI...", file=sys.stderr)
            await self.stt.initialize()
            await self.tts.initialize()
            print("Voice CLI ready. Hold SPACEBAR to speak, release to send.", file=sys.stderr)
        except Exception as e:
            ErrorHandler.handle_error("INIT", str(e))
            self.running = False

    async def run_cycle(self) -> None:
        """Run one complete voice interaction cycle."""
        try:
            # Wait for spacebar press
            await self.keyboard.wait_for_spacebar_hold()
            print("\n🎤 Recording... (release spacebar to send)", file=sys.stderr)

            # Record audio while spacebar is held
            stop_event = asyncio.Event()

            async def record_until_release():
                """Record until spacebar is released."""
                await self.keyboard.wait_for_spacebar_release()
                stop_event.set()

            # Start recording task and spacebar release watcher concurrently
            record_task = asyncio.create_task(self.audio_capture.record_until_signal(stop_event))
            release_task = asyncio.create_task(record_until_release())

            # Wait for both to complete
            audio_bytes = await record_task
            await release_task

            if not audio_bytes:
                ErrorHandler.handle_stt_error("No audio captured")
                return

            print("✓ Audio captured", file=sys.stderr)

            # Transcribe
            prompt = await self.stt.transcribe(audio_bytes)
            if not prompt:
                ErrorHandler.handle_stt_error("Transcription failed")
                return

            print(f"✓ Transcribed: {prompt}", file=sys.stderr)

            # Spawn Claude subprocess and get response
            print("\n📝 Claude:", file=sys.stderr)
            try:
                lines = await self.subprocess.spawn_and_get_response(prompt)
            except Exception as e:
                ErrorHandler.handle_subprocess_error(str(e))
                return

            if not lines:
                return

            # Capture and accumulate response
            accumulated_text, _ = self.response_capture.capture_and_accumulate(lines)

            print("", file=sys.stderr)  # Blank line after response

            # Generate and play speech
            audio_bytes = await self.tts.synthesize(accumulated_text)
            if audio_bytes:
                print("🔊 Playing audio...", file=sys.stderr)
                await self.audio_playback.play(audio_bytes)
                print("✓ Done", file=sys.stderr)
            else:
                ErrorHandler.handle_tts_error("Could not generate speech")

        except KeyboardInterrupt:
            self.running = False
        except Exception as e:
            ErrorHandler.handle_error("CYCLE", str(e))

    async def run(self) -> None:
        """Main event loop."""
        await self.initialize()

        while self.running:
            try:
                await self.run_cycle()
                await asyncio.sleep(0.1)  # Brief pause between cycles
            except KeyboardInterrupt:
                print("\nShutting down...", file=sys.stderr)
                self.running = False
            except Exception as e:
                ErrorHandler.handle_error("RUN", str(e))

        await self.subprocess.cleanup()


async def main():
    """Entry point."""
    cli = VoiceCLI()
    try:
        await cli.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


def run():
    """CLI entry point (from pyproject.toml scripts)."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
