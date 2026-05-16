# GitHub Issues — Conventions

This project uses GitHub Issues for tracking all work: features, bugs, tasks, and questions.

## Filing an Issue

Create a new issue in the [clive-claw/voice-cli](https://github.com/clive-claw/voice-cli/issues) repository.

**Title**: Clear, action-oriented. Examples:
- "Add streaming TTS support"
- "Fix STT timeout on long utterances"
- "Document Kokoro voice selection"

**Description**: Provide context:
- What is the problem or goal?
- Why does it matter?
- Any relevant code snippets, error logs, or links?

**Labels**: Apply one from the triage vocabulary (see `triage-labels.md`).

## Triage and Assignment

Issues enter with the `needs-triage` label. They move through triage (see `triage-labels.md`) and are assigned to agents or humans as appropriate.

## Linking Issues

Use GitHub's linking syntax in PR descriptions, comments, and commit messages:
- `Fixes #123` — Close issue 123 when PR merges
- `Relates to #456` — Reference without closing
- `Blocked by #789` — Dependency tracking

## Closing Issues

Close issues via PR merge (if using `Fixes #NNN` syntax) or manually if the work is done without a PR.

Always add a closing comment explaining what was done or why the issue is no longer relevant.
