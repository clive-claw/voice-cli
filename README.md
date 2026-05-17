# Voice CLI — Local Voice-to-Claude Bridge

A terminal-based voice interface for Claude Code. Hold spacebar to speak, get Claude's response read aloud.

## Setup

### Prerequisites

- macOS (M-series chip recommended)
- Python 3.11+
- Claude Code CLI (`claude` command available in PATH)
- Kokoro TTS model installed locally (optional for MVP, TTS will skip if unavailable)

### Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package
pip install -e .

# Verify installation
voice --help
```

## Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Run voice CLI
voice
```

**Interaction:**
1. **Hold spacebar** to start recording
2. **Speak naturally** — describe what you want Claude to do
3. **Release spacebar** to send the prompt to Claude
4. **Watch terminal** for Claude's response (displays in real-time)
5. **Hear audio** — response is read aloud to you (if Kokoro is available)
6. Repeat

## Architecture

See `CONTEXT.md` for domain concepts and `CLAUDE.md` for development.

### Modules

- **KeyboardListener** — Detects spacebar hold/release
- **AudioCapture** — Records from microphone (16 kHz)
- **SpeechToText** — Transcribes via mlx-audio Whisper (local, on Apple Silicon)
- **ClaudeSubprocess** — Spawns `claude -p` with prompt
- **ResponseCapture** — Displays subprocess output to terminal
- **TextToSpeech** — Generates speech via Kokoro (local, optional)
- **AudioPlayback** — Plays TTS audio to speakers
- **ErrorHandler** — Handles failures with stderr + beep
- **VoiceCLI** — Main async orchestrator

## Status

**MVP Complete** ✓

- Hold-to-talk interaction
- Local STT (mlx-audio Whisper)
- Subprocess integration with Claude Code CLI
- Response capture and display
- Error handling (stderr + beep)
- Local TTS support (Kokoro) — optional

**Known Issues**

- Keyboard listener uses pynput with threading — may have edge cases
- mlx-audio and Kokoro APIs subject to change; import paths may need adjustment
- No persistent conversation history (v2 feature)
- TTS voice is not customizable (v2 feature)

## Troubleshooting

### "claude CLI not found"
Ensure Claude Code is installed and `claude -p` works in your terminal:
```bash
echo "test" | claude -p "what is this?"
```

### STT not working
Verify mlx-audio is installed and working:
```bash
python3 -c "from mlx_audio.models import load_model; m = load_model('whisper'); print('✓ mlx-audio loaded')"
```

### TTS model files

Voice CLI uses `kokoro-onnx` for local TTS. The model files are not bundled — download them once (~350MB total) before first use:

```bash
mkdir -p ~/.voice-cli/models
curl -L -o ~/.voice-cli/models/kokoro-v1.0.onnx \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -L -o ~/.voice-cli/models/voices-v1.0.bin \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

The default voice is `af_heart`. Override with `VOICE_CLI_VOICE=<voice_name>` (54 voices available).

TTS is optional — if the model files are missing or `kokoro-onnx` is not installed, synthesis is silently skipped.

### TTS not working
Verify `kokoro-onnx` is installed and model files are present:
```bash
python3 -c "from kokoro_onnx import Kokoro; print('kokoro-onnx OK')"
ls ~/.voice-cli/models/
```

### Keyboard listener not detecting spacebar
Try holding the key for 1+ second and ensure the terminal has focus. The keyboard listener uses pynput which requires system permissions on macOS. Grant Terminal full disk access if prompted.

## Next Steps (v2)

- Persistent conversation history (Open Brain integration)
- Voice commands (`/voice summarize`, `/voice explain`)
- Streaming TTS for lower latency
- Multi-language support
- Custom TTS voice profiles
- Test coverage (unit + integration tests)
