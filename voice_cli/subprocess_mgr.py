"""Manage Claude Code subprocess."""

import asyncio
import subprocess
from typing import AsyncIterator, Optional


class ClaudeSubprocess:
    """Spawn and manage claude -p subprocess."""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None

    async def spawn_and_stream(self, prompt: str) -> AsyncIterator[str]:
        """Spawn claude -p with prompt and stream stdout line-by-line."""
        loop = asyncio.get_event_loop()

        try:
            # Spawn subprocess
            self.process = subprocess.Popen(
                ["claude", "-p", prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
            )

            # Stream stdout line-by-line
            if self.process.stdout:
                for line in self.process.stdout:
                    yield line.rstrip("\n")

            # Wait for process to complete
            self.process.wait()

        except FileNotFoundError:
            raise RuntimeError("claude CLI not found. Is it installed?")
        except Exception as e:
            raise RuntimeError(f"Subprocess error: {e}")
        finally:
            if self.process:
                self.process.stdout.close() if self.process.stdout else None
                self.process.stderr.close() if self.process.stderr else None
                self.process = None

    async def cleanup(self) -> None:
        """Clean up subprocess if still running."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            finally:
                self.process = None
