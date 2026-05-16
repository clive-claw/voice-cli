"""Error handling with beep and stderr output."""

import os
import sys
from typing import Optional


class ErrorHandler:
    """Catch errors, print to stderr, and beep."""

    @staticmethod
    def beep() -> None:
        """Play system beep alert."""
        # macOS system beep (ASCII 0x07)
        sys.stdout.write("\a")
        sys.stdout.flush()

    @staticmethod
    def handle_error(error_type: str, message: str) -> None:
        """Print error to stderr and beep."""
        error_msg = f"[ERROR] {error_type}: {message}"
        print(error_msg, file=sys.stderr)
        ErrorHandler.beep()

    @staticmethod
    def handle_stt_error(message: Optional[str] = None) -> None:
        """Handle speech-to-text error."""
        ErrorHandler.handle_error("STT", message or "Failed to transcribe audio")

    @staticmethod
    def handle_subprocess_error(message: Optional[str] = None) -> None:
        """Handle subprocess error."""
        ErrorHandler.handle_error("SUBPROCESS", message or "Claude process failed")

    @staticmethod
    def handle_tts_error(message: Optional[str] = None) -> None:
        """Handle text-to-speech error."""
        ErrorHandler.handle_error("TTS", message or "Failed to generate speech")

    @staticmethod
    def handle_keyboard_error(message: Optional[str] = None) -> None:
        """Handle keyboard listener error."""
        ErrorHandler.handle_error("KEYBOARD", message or "Keyboard input failed")
