# Contributing

## Scope

This repository is an internal MarketAcross project. Keep contributions focused, incremental, and directly tied to roadmap or bug-fix outcomes.

## Workflow

1. Read `AGENTS.md` and `Memory.md` before substantial work.
2. Make scoped changes only; avoid unrelated refactors.
3. Keep docs updated in the same task when behavior, API, or operations change.
4. Run verification before marking complete.

## Required Checks

Run relevant checks for touched areas.

Backend:

```bash
cd backend
python -m ruff check .
python -m ruff format --check .
python -m alembic upgrade head
python -m pytest --tb=short
```

Frontend:

```bash
cd frontend
npm ci --legacy-peer-deps
npm run lint
npm run test:run
npm run build
```

## Pull Request Notes

Include:

- What changed and why
- Verification run and outcomes
- Known blockers or residual risk
- Any documentation updated

## Documentation Rules

- Keep `ROADMAP.md` as source of truth for phase status/progress.
- Keep `CHANGELOG.md` updated under `Unreleased`.
- Ensure all markdown links resolve.

## Commit Style

Use clear, imperative commit messages, e.g.:

- `Add CI smoke workflow for main branch`
- `Fix migration enum duplication on fresh PostgreSQL`
- `Sync roadmap and architecture docs for Phase 8`
