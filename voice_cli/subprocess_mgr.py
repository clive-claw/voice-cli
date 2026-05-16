"""Manage Claude Code subprocess."""

import asyncio
import subprocess
from typing import Optional, List


class ClaudeSubprocess:
    """Spawn and manage claude -p subprocess."""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None

    async def spawn_and_get_response(self, prompt: str) -> List[str]:
        """Spawn claude -p with prompt and return all output lines."""
        loop = asyncio.get_event_loop()

        def run_subprocess():
            """Run subprocess synchronously."""
            try:
                # Spawn subprocess
                process = subprocess.Popen(
                    ["claude", "-p", prompt],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,  # Line buffered
                )

                lines = []
                # Read stdout line-by-line
                if process.stdout:
                    for line in process.stdout:
                        lines.append(line.rstrip("\n"))

                # Wait for process to complete
                process.wait()
                return lines

            except FileNotFoundError:
                raise RuntimeError("claude CLI not found. Is it installed?")
            except Exception as e:
                raise RuntimeError(f"Subprocess error: {e}")

        return await loop.run_in_executor(None, run_subprocess)

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
