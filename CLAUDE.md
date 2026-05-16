# Voice CLI — Claude Project Configuration

## Overview

Voice CLI is a local voice-to-Claude bridge for the terminal. Users hold spacebar to speak, the prompt is transcribed via mlx-audio, piped to Claude Code CLI, and Claude's response is both displayed in the terminal and read aloud via Kokoro TTS.

See `CONTEXT.md` for domain vocabulary and core concepts.

## Agent Skills

### Issue tracker

Issues live in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Uses mattpocock default label vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context (one CONTEXT.md at root). See `docs/agents/domain.md`.

## Development

### Project Structure

```
voice-cli/
├── voice_cli/              # Main Python package
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── keyboard.py         # Spacebar hold detection
│   ├── audio.py            # Audio capture and playback
│   ├── stt.py              # Speech-to-text (mlx-audio)
│   ├── subprocess.py       # Claude subprocess management
│   ├── response.py         # Response capture and streaming
│   ├── tts.py              # Text-to-speech (Kokoro)
│   └── error.py            # Error handling
├── pyproject.toml          # Dependencies
├── PRD.md                  # Product requirements
├── CLAUDE.md               # This file
├── CONTEXT.md              # Domain vocabulary
└── docs/agents/            # Agent skill documentation
```

### Running Locally

```bash
# Install dependencies
pip install -e .

# Run voice CLI
voice
```

Hold spacebar to record, release to transcribe and send to Claude Code.

### Tech Stack

- **mlx-audio** — Local Whisper STT (Apple Silicon optimized)
- **Kokoro** — Local TTS (82M parameter model)
- **Claude API** — Via `claude -p` CLI
- **asyncio** — Concurrent I/O orchestration
- **pydub** — Audio playback

All processing is local and private — no cloud STT/TTS.
