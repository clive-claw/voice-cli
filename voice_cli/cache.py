"""Session-scoped cache for the most recent voice CLI turn.

Each terminal tab gets its own directory under ~/.voice-cli/sessions/, keyed
by the terminal's session ID, so concurrent `voice` instances in different
tabs do not overwrite each other's last response.
"""

import os
import shutil
import sys
import time
from pathlib import Path
from typing import Optional

STALE_AFTER_SECONDS = 7 * 24 * 60 * 60

_warned = False


def session_id() -> str:
    """Identify the current terminal tab.

    iTerm2 sets ITERM_SESSION_ID, Apple Terminal sets TERM_SESSION_ID. Both
    are stable for the life of the tab, so a `voice` restart within the same
    tab reuses the same cache slot. Fallback to parent shell PID keeps plain
    terminals from colliding.
    """
    raw = (
        os.environ.get("ITERM_SESSION_ID")
        or os.environ.get("TERM_SESSION_ID")
        or f"ppid-{os.getppid()}"
    )
    return raw.replace(":", "_").replace("/", "_")


def session_dir() -> Path:
    """Return the per-session cache directory, creating it 0700 if needed.

    Tightening the whole tree to 0700 keeps transcripts unreadable to other
    users and to anything that scans home dirs (backup tools, sync clients).
    """
    root = Path.home() / ".voice-cli"
    sessions = root / "sessions"
    d = sessions / session_id()
    d.mkdir(parents=True, exist_ok=True)
    for p in (root, sessions, d):
        try:
            os.chmod(p, 0o700)
        except OSError:
            pass
    return d


def write_last(wav_bytes: bytes, prompt: str, response: str) -> Optional[Path]:
    """Best-effort persist of the most recent turn for this session.

    Returns the wav path on success, None on failure. Cache write failures
    are non-fatal — playback should proceed even if disk is full or perms
    are wrong — so we swallow OSError and warn once per process.
    """
    global _warned
    try:
        d = session_dir()
        wav_path = d / "last.wav"
        wav_path.write_bytes(wav_bytes)
        os.chmod(wav_path, 0o600)
        txt_path = d / "last.txt"
        txt_path.write_text(f"PROMPT: {prompt}\n\nRESPONSE: {response}\n")
        os.chmod(txt_path, 0o600)
        return wav_path
    except OSError as e:
        if not _warned:
            print(f"⚠ cache disabled: {e}", file=sys.stderr)
            _warned = True
        return None


def gc_stale(max_age_seconds: int = STALE_AFTER_SECONDS) -> int:
    """Delete session dirs untouched for longer than max_age_seconds.

    Activity is judged by the mtime of last.wav (or the directory itself if
    no wav has been written yet). Returns the number of dirs removed.
    """
    root = Path.home() / ".voice-cli" / "sessions"
    if not root.exists():
        return 0

    now = time.time()
    removed = 0
    for child in root.iterdir():
        if not child.is_dir():
            continue
        wav = child / "last.wav"
        ref = wav if wav.exists() else child
        try:
            age = now - ref.stat().st_mtime
        except OSError:
            continue
        if age > max_age_seconds:
            try:
                shutil.rmtree(child)
                removed += 1
            except OSError:
                pass
    return removed
