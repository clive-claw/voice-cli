# Voice CLI — Domain Context

## Overview

Voice CLI is a local voice-to-Claude interface for terminal-based development. It bridges voice input and Claude's text responses through real-time transcription, subprocess spawning, and text-to-speech playback. The system is designed for hands-free interaction with Claude Code while preserving full control over when recording starts and stops.

**What Voice CLI is NOT**: It is not a persistent chat application, a cloud-based service, or a replacement for Claude Code's native interface. It is purely a voice input layer on top of Claude Code's subprocess.

## Core Concepts

### Hold-to-Talk Interaction

The primary interaction model. User holds spacebar to signal intent to record, speaks naturally, then releases spacebar to finalize recording and trigger transcription. Explicit start/stop gives the user precise control.

**Related**: Voice activation (always-listening with wake words) is out of scope for MVP.

### Audio Pipeline

The sequence of processing steps:
1. **Capture** — Raw audio from microphone microphone (16 kHz, real-time)
2. **Transcription** — Convert audio buffer to text via mlx-audio Whisper
3. **Prompt** — Text sent to Claude Code CLI via subprocess stdin
4. **Response** — Claude's text output captured line-by-line as it streams
5. **Synthesis** — Response text converted to speech via Kokoro TTS
6. **Playback** — Audio output to system speakers

All steps happen asynchronously and concurrently (e.g., TTS can begin before Claude finishes responding).

### Subprocess Wrapper Pattern

Voice CLI doesn't invoke Claude API directly. Instead, it spawns the `claude -p "prompt"` CLI as a subprocess, allowing the user's terminal to display Claude's native output format while giving the Voice CLI access to the response stream for TTS.

**Invariant**: The subprocess represents one complete user-prompt → Claude-response cycle. Once the subprocess exits, the cycle is complete and Voice CLI returns to listening.

### Local Processing

All speech-related models (STT and TTS) run on-device using Apple Silicon optimizations:
- **mlx-audio** — Whisper-class speech-to-text
- **Kokoro** — 82M parameter text-to-speech

No audio is sent to external services. User speech and Claude responses remain private and on-device.

### Response Capture

The act of reading Claude's subprocess stdout in real-time, yielding lines as they arrive. This happens concurrently with:
- Terminal display (lines printed as they stream)
- Text accumulation (for later TTS conversion)

**Invariant**: The entire response is accumulated before TTS begins, not streamed in chunks. This simplifies latency guarantees.

### Error Handling

When STT, Claude subprocess, or TTS fails, Voice CLI:
1. Prints error message to stderr (user-facing feedback)
2. Plays a system beep (audio alert)
3. Returns to listening state (ready for next prompt)

Failed interactions are not retried automatically; user must speak again.

## Status Lifecycles

### Voice CLI State Machine

```
┌─────────────┐
│   READY     │  (waiting for spacebar hold)
└──────┬──────┘
       │ [spacebar pressed]
       ▼
┌─────────────┐
│  RECORDING  │  (capturing audio from mic)
└──────┬──────┘
       │ [spacebar released]
       ▼
┌─────────────┐
│ TRANSCRIBE  │  (mlx-audio STT)
└──────┬──────┘
       │ [error] ──→ [BEEP + ERROR] ──→ [READY]
       │ [success]
       ▼
┌─────────────┐
│  SPAWNING   │  (launch claude -p subprocess)
└──────┬──────┘
       │ [error] ──→ [BEEP + ERROR] ──→ [READY]
       │ [success]
       ▼
┌─────────────┐
│ STREAMING   │  (read subprocess stdout, display + accumulate)
└──────┬──────┘
       │ [subprocess exits]
       ▼
┌─────────────┐
│  SYNTHESIS  │  (Kokoro TTS on accumulated response)
└──────┬──────┘
       │ [error] ──→ [BEEP + ERROR] ──→ [READY]
       │ [success]
       ▼
┌─────────────┐
│  PLAYBACK   │  (play audio to speakers)
└──────┬──────┘
       │ [audio finished]
       ▼
┌─────────────┐
│   READY     │  (return to listening)
└─────────────┘
```

### Subprocess Lifecycle

Claude subprocess runs for one complete prompt-response cycle:
1. **Spawned** with `claude -p "<transcribed_prompt>"` and subprocess.Popen
2. **Streaming** — stdout read line-by-line in non-blocking mode
3. **Exited** — subprocess.wait() returns; lines accumulated from stdout
4. **Disposed** — subprocess cleaned up; Voice CLI continues

## Glossary

| Term | Definition | Avoid |
|------|-----------|-------|
| **Hold-to-talk** | Interaction model where spacebar press signals recording start, release signals recording stop. | Always-listening, wake words |
| **Subprocess wrapper** | Pattern where Voice CLI spawns Claude Code CLI as a child process, not invoking Claude API directly. | Direct API calls, background threads |
| **mlx-audio** | Apple MLX framework for local speech-to-text, optimized for Apple Silicon. | OpenAI API, cloud STT |
| **Kokoro** | Local text-to-speech model (82M parameters) that runs on-device. | ElevenLabs, Google TTS, cloud TTS |
| **Response capture** | Real-time reading of subprocess stdout, yielding lines as they arrive. | File I/O, polling |
| **Audio pipeline** | End-to-end sequence from microphone capture → transcription → spawning → response capture → synthesis → playback. | Individual steps in isolation |
| **Local processing** | All models and audio handling on-device; no external services. | Hybrid (local + cloud fallback) |
| **Cycle** | One complete interaction: spacebar hold → speak → release → transcription → Claude response → TTS playback → ready. | Session, conversation, history |
| **Beep** | System audio alert (macOS) played on STT, subprocess, or TTS failure. | Silent failure, logging only |
| **Streaming** | Subprocess stdout arrives line-by-line and is processed in real-time, not buffered fully before processing. | Full buffer before processing |
