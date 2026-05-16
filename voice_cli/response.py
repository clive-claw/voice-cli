"""Response capture and accumulation."""

from typing import AsyncIterator


class ResponseCapture:
    """Capture and accumulate subprocess response."""

    async def capture_and_accumulate(
        self, line_iterator: AsyncIterator[str]
    ) -> tuple[str, list[str]]:
        """
        Consume lines from iterator, print each, and accumulate for TTS.
        Returns (accumulated_text, lines_list).
        """
        lines = []
        async for line in line_iterator:
            lines.append(line)
            # Print to terminal as it arrives (real-time display)
            print(line)

        # Join all lines for TTS
        accumulated_text = "\n".join(lines)
        return accumulated_text, lines
