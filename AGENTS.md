# AI Hub Agent Operating Rules

## Purpose
This file defines mandatory execution standards for work in AI Hub.
The goals are quality, completeness, and clear communication.

## Mandatory Quality Workflow
Before marking any task complete, execute all steps below.

1. Adversarial second pass
- Run a deliberate challenge pass that tries to disprove the solution.
- Identify at least 3 realistic failure modes (edge cases, regressions, or missed requirements).
- Verify each failure mode with concrete checks or reasoning.
- If subagents are available, run an independent reviewer path; otherwise perform an explicit adversarial self-review.

2. Verification before completion
- Do not claim success without fresh evidence from appropriate validation (tests, lint, build, or task-specific checks).
- Report verification outcomes in the final update.
- If full verification cannot run, state what was run, what was blocked, and residual risk.

3. Code hygiene
- Remove dead code, unused imports, stale conditionals, and obsolete comments in touched files.
- Keep cleanup scoped to task-affected files unless broader cleanup is explicitly requested.
- Avoid unrelated refactors during feature or bug-fix work.

4. Documentation sync and cleanup
- For any behavior, API, configuration, or operational change, update documentation in the same task.
- Remove or revise outdated documentation touched by the change.
- Ensure examples and commands remain accurate after code changes.

5. Completion gate
- A task is complete only when code, verification, and documentation are aligned.
- Do not mark complete with known critical defects.

## Required Skills for This Project
When relevant to the request, prioritize these skills:

- `verification-before-completion`
- `subagent-driven-development`
- `dispatching-parallel-agents`
- `requesting-code-review`
- `test-driven-development`
- `doc-coauthoring`
- `dead-code-detector`

## Continuous Improvement Rule
At the end of meaningful tasks, propose 0 to 2 concrete improvements to rules or workflow when recurring friction is observed.

Improvement proposals must be:
- specific and testable,
- low overhead by default,
- scoped to AI Hub needs.

If no useful improvement is identified, do not force one.

## Memory Rule
- Use `Memory.md` as the durable record of recurring mistakes and prevention checks.
- Before substantial work, scan relevant sections of `Memory.md` and apply applicable guardrails.
- After substantial work, add or update entries only when a reusable lesson is discovered.
- Prefer marking old entries as superseded instead of deleting history.

## Communication Standard
- Be concise and direct.
- Explicitly call out assumptions, risks, and blockers.
- Include exact file references for substantial code explanations.
