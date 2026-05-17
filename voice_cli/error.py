"""Error reporting: print to stderr and play a system beep."""

import sys
from typing import Optional


def report_failure(stage: str, exc: Optional[BaseException] = None) -> None:
    """Print a stage-tagged error message to stderr and play a system beep.

    Parameters
    ----------
    stage:
        Short label for the pipeline stage where the failure occurred, e.g.
        ``"STT"``, ``"TTS"``, ``"SUBPROCESS"``.
    exc:
        The exception that caused the failure, or ``None`` when the failure is
        detected without an exception (e.g. empty result).
    """
    print(f"⚠ [{stage}] {exc or '...'}", file=sys.stderr)
    # macOS / terminal system beep (ASCII BEL)
    sys.stdout.write("\a")
    sys.stdout.flush()
