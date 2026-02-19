# AI Hub Agent Memory

## Purpose
This file stores recurring mistakes, lessons learned, and prevention rules so future tasks avoid repeating failures.

## How To Use
1. Before starting substantial work, quickly scan:
- `Recurring Mistakes`
- `Active Guardrails`
- `Recent Lessons`
2. During execution, apply relevant guardrails.
3. At task end, add a memory entry only if a new, reusable lesson was discovered.
4. Keep entries concise, specific, and actionable.

## Entry Rules
- Write concrete facts, not vague advice.
- Focus on patterns likely to recur.
- Include prevention checks that can be executed in future tasks.
- If a lesson becomes obsolete, mark it as superseded instead of deleting history.

## Active Guardrails
- Always run an adversarial second pass before completion.
- Do not mark tasks done without verification evidence.
- Remove dead code in touched files.
- Sync documentation with behavior changes in the same task.

## Recurring Mistakes
| ID | Mistake Pattern | Typical Trigger | Prevention Check | Status |
|---|---|---|---|---|
| M-001 | Assuming completion without full verification | Time pressure near task end | Explicitly list run checks and blocked checks in final summary | Active |
| M-002 | Leaving stale docs after code changes | Narrow focus on implementation only | For each behavior/API/config change, update docs before completion gate | Active |
| M-003 | Missing edge cases on first pass | Single-solution tunnel vision | Record at least 3 failure modes during adversarial review | Active |

## Recent Lessons
### 2026-02-19 - Run a markdown link audit after roadmap/docs edits
- Context: Multiple docs referenced files that did not exist (`docs/DEPLOYMENT.md`, `CONTRIBUTING.md`).
- Lesson: After status/doc sweeps, run an internal-link check across all primary docs to catch broken references early.
- Action: Added missing docs and validated internal markdown links across project docs.
- Reuse Trigger: Any roadmap/changelog/readme or architecture/HLD update.

### 2026-02-19 - Frontend CI install requires peer-deps workaround
- Context: `npm ci` fails due React 19 and `@testing-library/react` v14 peer-dependency conflict.
- Lesson: Until dependencies are aligned, CI must use `npm ci --legacy-peer-deps` for frontend install steps.
- Action: Applied `--legacy-peer-deps` in `.github/workflows/ci.yml` for frontend and e2e-smoke jobs.
- Reuse Trigger: Any CI workflow edits or local verification that runs frontend install in this repo.

### 2026-02-19 - Prevent cross-doc status drift
- Context: Roadmap and other docs diverged after status updates (progress %, planned phases, and linked docs).
- Lesson: Treat `ROADMAP.md` as source of truth for status/milestones and run a link+consistency pass on core docs.
- Action: Added doc-audit findings and flagged broken internal links + phase/progress mismatch for cleanup.
- Reuse Trigger: Any roadmap/status update or docs refactor.

### 2026-02-19 - Keep roadmap execution-focused
- Context: Roadmap had strong detail but weak immediate readability for current execution.
- Lesson: Add a short "Now / Next / Later" snapshot and avoid duplicating completed items in multiple places.
- Action: Added `Execution Snapshot (Now, Next, Later)` and removed redundant historical completion bullets from `ROADMAP.md`.
- Reuse Trigger: Any roadmap or planning doc update with long historical sections.

### 2026-02-19 - Establish explicit quality gates
- Context: Needed durable standards for verification, cleanup, and docs sync.
- Lesson: Quality improves when completion criteria are written and mandatory.
- Action: Added enforceable workflow rules to `AGENTS.md`.
- Reuse Trigger: Any task that changes behavior, API, config, or operational commands.

## Template For New Lessons
### YYYY-MM-DD - <Short title>
- Context:
- Mistake or risk:
- Root cause:
- Prevention check:
- Scope (where this applies):
- Status: Active | Superseded by <ID/date>
