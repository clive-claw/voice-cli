"""Response capture and accumulation."""

from typing import List


class ResponseCapture:
    """Capture and accumulate subprocess response."""

    def capture_and_accumulate(self, lines: List[str]) -> tuple[str, List[str]]:
        """
        Display lines and accumulate for TTS.
        Returns (accumulated_text, lines_list).
        """
        for line in lines:
            # Print to terminal
            print(line)

        # Join all lines for TTS
        accumulated_text = "\n".join(lines)
        return accumulated_text, lines
