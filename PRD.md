# Voice CLI: Local Voice-to-Claude Bridge

## Problem Statement

Adam wants to interact with Claude Code through voice without leaving the terminal. Currently, using Claude Code requires typing prompts; there's no native voice interface. Existing voice-to-text tools (like Whisper Flow) type into any focused app, but don't integrate the response back as audio, forcing the user to read the output.

The goal is a seamless voice workflow: speak a prompt → see the response in Claude Code terminal → hear it read aloud simultaneously.

## Solution

Build a local voice CLI that:

1. **Listens for spacebar hold** — User holds spacebar to initiate recording
2. **Captures and transcribes voice** — Records audio from mic, transcribes to text using mlx-audio (local, on M5 Apple Silicon)
3. **Pipes prompt to Claude Code** — Spawns `claude -p "transcribed text"` as a subprocess
4. **Captures and displays response** — Streams Claude Code's response to the terminal in real-time
5. **Generates and plays speech** — Pipes the same response to Kokoro TTS, plays audio to speakers
6. **Handles errors gracefully** — Beeps and prints errors to stderr if STT, Claude, or TTS fails

All processing is local (no external STT/TTS services) and optimized for M5 Apple Silicon. End-to-end latency: ~1–2 seconds from spacebar release to first audio output.

## User Stories

1. As a developer, I want to hold spacebar and speak a prompt, so that I can interact with Claude without typing
2. As a developer, I want the voice prompt to be transcribed accurately, so that Claude receives the correct intent
3. As a developer, I want Claude's response to appear in my terminal, so that I can read it while working
4. As a developer, I want Claude's response to be read aloud to me, so that I can listen while continuing to work
5. As a developer, I want the speech output to stream in real-time, so that I get immediate feedback
6. As a developer, I want the entire interaction to be local (no cloud dependencies), so that my voice and prompts stay private
7. As a developer, I want fast response latency (<2 seconds), so that the interaction feels natural and conversational
8. As a developer, I want the voice CLI to handle errors gracefully, so that I know when something fails
9. As a developer, I want voice transcription to work with background noise, so that I can use it in real-world environments
10. As a developer, I want to easily stop recording by releasing the spacebar, so that I have precise control over when I'm done speaking
11. As a developer, I want the audio playback to be synchronized with the terminal output, so that I can follow along visually and aurally
12. As a developer, I want the TTS voice to sound natural, so that listening is comfortable and engaging
13. As a developer, I want low memory overhead, so that it doesn't interfere with my other work
14. As a developer, I want the CLI to be easy to start and stop, so that I can toggle voice mode on demand
15. As a developer, I want clear error messages when things fail, so that I can troubleshoot issues

## Implementation Decisions

### Architecture

- **Subprocess Wrapper Pattern**: Voice CLI spawns `claude -p "prompt"` as a subprocess, captures stdout in real-time, and displays it to the user's terminal. This allows the response to flow naturally through Claude Code while giving the voice CLI access to stream it to TTS.

- **Async Orchestration**: Use Python `asyncio` to manage concurrent operations:
  - Keyboard input monitoring (spacebar hold detection)
  - Audio capture and transcription
  - Subprocess lifecycle and stdout streaming
  - TTS generation and audio playback

- **Local-First Stack**: All STT and TTS run locally on M5:
  - **mlx-audio** (Apple MLX framework): Local Whisper-class speech-to-text, optimized for Apple Silicon
  - **Kokoro**: 82M parameter local TTS, fast generation, natural voice
  - No cloud dependencies, no API keys for speech processing

### Modules

- **KeyboardListener**: Monitors keyboard input, detects spacebar press/release, signals start/stop to the orchestrator. Returns a future that resolves when spacebar is released.

- **AudioCapture**: Records from the system microphone while signaled. Uses a buffer (e.g., `sounddevice`) to collect audio chunks. Stops on signal and returns the buffer.

- **SpeechToText**: Takes raw audio buffer, runs mlx-audio Whisper model, returns transcribed text. Handles empty audio (beeps + returns error).

- **ClaudeSubprocess**: Spawns `claude -p "<prompt>"` as a subprocess with subprocess.Popen, configured for live stdout streaming. Manages stdin/stdout/stderr file descriptors.

- **ResponseCapture**: Reads subprocess stdout line-by-line in non-blocking mode. Yields each line as it arrives, allowing real-time display and concurrent TTS.

- **TextToSpeech**: Takes text, runs Kokoro TTS model, returns audio buffer. Handles empty text (returns empty audio gracefully).

- **AudioPlayback**: Takes audio buffer from TTS, plays to speakers using pydub + system audio. Non-blocking, runs concurrently.

- **ErrorHandler**: Catches exceptions from any module. Prints error message to stderr, plays a beep to alert user. Returns gracefully to ready state.

- **VoiceCLI**: Main async function that orchestrates all modules:
  1. Wait for spacebar hold
  2. Record audio
  3. Transcribe to text
  4. Spawn Claude subprocess with text
  5. For each line from subprocess:
     - Print to terminal (real-time display)
     - Accumulate for TTS
  6. Once subprocess exits, generate TTS from accumulated text
  7. Play audio concurrently with terminal display
  8. Return to waiting for spacebar

### Input Flow

1. User holds spacebar → KeyboardListener signals AudioCapture to start
2. User speaks
3. User releases spacebar → KeyboardListener signals stop
4. AudioCapture returns buffer
5. SpeechToText transcribes buffer to text
6. ClaudeSubprocess spawns with `-p "text"`
7. ResponseCapture streams output line-by-line
8. Each line: printed to terminal + accumulated for TTS
9. Subprocess exits
10. TextToSpeech converts accumulated text to audio
11. AudioPlayback plays audio while user reads terminal
12. Return to step 1

### Error Handling

- **STT failure** (no speech detected, transcription error): Print to stderr, beep, return to ready
- **Subprocess failure** (Claude API error, network timeout): Print to stderr, beep, return to ready
- **TTS failure** (Kokoro error): Print to stderr, beep, skip audio playback, return to ready
- **Keyboard interrupt** (Ctrl+C): Clean shutdown, exit gracefully

### Configuration

- Microphone input device: default system input
- Audio sample rate: 16 kHz (mlx-audio standard)
- Audio chunk size: optimized for real-time capture (e.g., 512 samples)
- TTS buffer size: accumulate full response before TTS (not streaming chunks)
- Beep frequency/duration: system alert (macOS)

## Testing Decisions

**For MVP**: No automated tests. Validation is manual:
- Speak a simple question ("what is 2+2?")
- Verify transcription accuracy
- Verify Claude response displays in terminal
- Verify TTS plays back response
- Verify spacebar hold/release is responsive
- Verify errors print to stderr and beep

**For v2**: Add tests for:
- SpeechToText module (mock audio buffer, verify transcription)
- ClaudeSubprocess module (mock subprocess, verify arg passing)
- ResponseCapture module (mock subprocess stdout, verify line-by-line streaming)
- TextToSpeech module (mock Kokoro, verify audio generation)
- ErrorHandler module (verify beep + stderr on exception)

## Out of Scope

- **Persistent conversation history** — Each interaction is independent. (Can be added in v2 via Brain integration.)
- **Wake-word detection** — Uses explicit hold-to-talk only. (Always-listening would require background listener, adds complexity.)
- **Multi-language support** — English only for MVP. (Can add language selection in v2.)
- **Custom TTS voice training** — Uses Kokoro default voices. (Can add voice design in v2 if switching to Qwen3 TTS.)
- **Cloud STT/TTS fallback** — Local-only. If hardware insufficient, user must have mlx-audio + Kokoro working.
- **GUI/TUI** — Pure CLI, no visual UI during interaction. (Terminal output from subprocess is the interface.)
- **Integration with Claude Code history** — Each voice prompt is a fresh interaction.
- **Streaming TTS** — Full response is accumulated, then generated as one block. (Can optimize to streaming TTS in v2 if latency becomes an issue.)

## Further Notes

- **Latency expectations**: ~1–2 seconds end-to-end from spacebar release to first audio:
  - STT transcription: 200–400ms
  - Claude API (streaming): 500ms to first token
  - TTS generation (Kokoro): 100–300ms
  - Audio playback: <100ms
  
- **Hardware assumptions**: M5 MBP with 48GB unified memory. All models (mlx-audio Whisper, Kokoro, Claude API calls) fit comfortably without swap.

- **Dependencies**:
  - `mlx-audio >= 0.4.0` — Apple MLX STT
  - `pydub >= 0.25.1` — Audio I/O and playback
  - `anthropic >= 0.34.0` — Claude API (for future cloud TTS fallback, not MVP)
  - Kokoro installed locally (check for binary/model availability on M5)
  - System Python 3.11+ with asyncio

- **Next steps post-MVP**:
  - Persist voice interactions to Open Brain
  - Add support for voice commands (`/voice summarize`, `/voice explain`)
  - Streaming TTS for lower latency
  - Language selection
  - Custom voice profiles
  - Integration with Claude Code context (auto-include codebase in prompts)
