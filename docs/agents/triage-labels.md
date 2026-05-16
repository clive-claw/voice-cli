# Triage Labels — Vocabulary

This project uses the **mattpocock default** label vocabulary for GitHub Issues. Labels follow a consistent naming pattern: `status-*`, `type-*`, and special markers.

## Status Labels

| Label | Meaning | When to Use |
|-------|---------|------------|
| `needs-triage` | Issue is new and hasn't been reviewed for priority/scope. | Automatically applied to new issues. Remove once triaged. |
| `needs-info` | Issue is blocked waiting for more information from the reporter. | When you need clarification, sample code, or reproduction steps before proceeding. |
| `ready-for-agent` | Issue is scoped, prioritized, and ready for an agent to pick up. | After triage; indicates the issue is well-defined and actionable. |
| `ready-for-human` | Issue requires human judgment (design decisions, policy, security review). | When an agent needs human input before continuing. |
| `wontfix` | Issue is intentionally not being fixed. | When out-of-scope, duplicate, or explicitly declined. Always add a closing comment explaining why. |

## Type Labels (Optional, for clarity)

| Label | Meaning |
|-------|---------|
| `feature` | New capability or behavior. |
| `bug` | Broken functionality. |
| `docs` | Documentation or examples. |
| `refactor` | Code quality, no behavior change. |
| `question` | User question or investigation. |

## Priority (Optional)

If your team uses priority:
| Label | Meaning |
|-------|---------|
| `priority-high` | Critical or blocking. |
| `priority-medium` | Important but not blocking. |
| `priority-low` | Nice-to-have. |

## How to Triage

1. **Read the issue.** Understand the problem and proposed solution.
2. **Ask clarifying questions.** If you need more info, apply `needs-info` and comment.
3. **Scope the work.** Break large issues into smaller ones if needed.
4. **Estimate effort.** Rough T-shirt size (small, medium, large).
5. **Assign status.**
   - **For agents**: Apply `ready-for-agent` and optionally a type label.
   - **For humans**: Apply `ready-for-human` with a comment explaining what decision is needed.
   - **Out of scope**: Apply `wontfix` with a closing comment.

## Label Lifecycle

```
New Issue
    ↓
needs-triage (auto)
    ↓
[Clarification needed?] ──→ needs-info ──→ [Reported back] ──→ [Re-triage]
    ↓ No
[Scope + prioritize]
    ↓
ready-for-agent   OR   ready-for-human   OR   wontfix
    ↓                       ↓                      ↓
 [Agent work]          [Human decision]      [Closed]
    ↓                       ↓
 [PR/Resolved]         [Ready-for-agent]
    ↓                       ↓
 [Closed]               [Agent work]
                            ↓
                        [Closed]
```

## Examples

**Feature request — ready for agent:**
```
Title: Add streaming TTS support
Labels: ready-for-agent, feature
Comment: Scope is in the PRD under "v2 features". Estimate: medium. No blocker.
```

**Bug — needs more info:**
```
Title: STT times out on utterances > 30 seconds
Labels: needs-info, bug
Comment: @reporter Can you provide:
1. Your exact MBP model and macOS version?
2. The exact utterance that timed out (or an example)?
3. Do shorter utterances work without timeout?
```

**Design decision — ready for human:**
```
Title: Should we persist voice history to Open Brain?
Labels: ready-for-human, feature
Comment: Scoped in PRD as "v2 feature". But this is a design choice about data privacy + storage. 
@adamharris: Should voice interactions be logged to Brain, or stay local-only?
```
