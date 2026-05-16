"""Manage Claude Code subprocess."""

import asyncio
import subprocess
import threading
from typing import Optional, List


class ClaudeSubprocess:
    """Spawn and manage claude -p subprocess."""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        # Guards assignment/read of self.process across threads (the
        # subprocess is created inside an executor thread, but cleanup()
        # may be called from the event-loop thread).
        self._process_lock = threading.Lock()

    async def spawn_and_get_response(self, prompt: str) -> List[str]:
        """Spawn claude -p with prompt and return all output lines."""
        loop = asyncio.get_event_loop()

        def run_subprocess():
            """Run subprocess synchronously."""
            try:
                # Spawn subprocess and publish it on self so cleanup()
                # can reach it, before entering the (potentially long)
                # read loop.
                process = subprocess.Popen(
                    ["claude", "-p", prompt],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,  # Line buffered
                )
                with self._process_lock:
                    self.process = process

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
            finally:
                # Clear the reference once the process has exited so
                # cleanup() doesn't try to terminate a finished process.
                with self._process_lock:
                    self.process = None

        return await loop.run_in_executor(None, run_subprocess)

    async def cleanup(self) -> None:
        """Clean up subprocess if still running."""
        with self._process_lock:
            process = self.process
        if process is None:
            return
        try:
            process.terminate()
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
        finally:
            with self._process_lock:
                self.process = None
