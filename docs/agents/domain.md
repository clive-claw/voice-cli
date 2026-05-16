# Domain Documentation

This project uses a **single-context** model: all domain vocabulary and core concepts are in one file at the repo root.

## Primary Sources

- **`CONTEXT.md`** — Domain vocabulary, core concepts, state machines, glossary of terms specific to voice CLI.
- **`CLAUDE.md`** — Development setup, project structure, tech stack, how to run locally.
- **`PRD.md`** — Product requirements, user stories, implementation decisions, scope.

## When to Reference Each

| Document | Use When | Example |
|----------|----------|---------|
| `CONTEXT.md` | You need to understand domain concepts, terminology, or how parts relate. | "What is the subprocess wrapper pattern?", "What is a 'cycle'?" |
| `CLAUDE.md` | You're setting up the project, running it locally, or need file structure. | "How do I install dependencies?", "Where is the STT module?" |
| `PRD.md` | You're implementing a feature and need to understand the original requirements or user stories. | "What was the original motivation for hold-to-talk?", "What's in MVP vs v2?" |

## Adding Domain Content

If you discover new domain concepts or need to clarify terminology:

1. **Update `CONTEXT.md`** with the new concept or refinement.
2. **Reference it from other docs** using links: `See [Subprocess Wrapper Pattern](../CONTEXT.md#subprocess-wrapper-pattern) in CONTEXT.md`.
3. **No other file should duplicate domain definitions.** If you find yourself re-explaining a concept, link to CONTEXT.md instead.

## Architecture Records (ADRs)

For major design decisions (e.g., "Why did we choose asyncio over threading?"), consider adding an ADR in `docs/adr/` once the project has matured. For now, design rationale lives in the PRD and CONTEXT.md.
