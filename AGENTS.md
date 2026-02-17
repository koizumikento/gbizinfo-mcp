# AGENTS.md

This repository standardizes Python workflows on `uv`.

## Core Policy
- Use `uv` for all Python package management and command execution.
- Do not use `pip`, `pipenv`, `poetry`, or `conda` commands in this repo.
- Prefer reproducible runs from lock state.

## Environment Setup
1. Install `uv` (if not installed).
2. Sync dependencies:
   - `uv sync`
3. If dependency groups are used, include required groups explicitly:
   - `uv sync --group dev`

## Running Commands
- Always run Python tools via `uv run`.
- Examples:
  - `uv run python -m <module>`
  - `uv run pytest`
  - `uv run ty check`
  - `uv run ruff check .`
  - `uv run ruff format .`

## Type Checking
- Use `ty` as the default type checker.
- Run type checks with:
  - `uv run ty check`

## Dependency Management
- Add runtime dependencies with:
  - `uv add <package>`
- Add development-only dependencies with:
  - `uv add --group dev <package>`
- Remove dependencies with:
  - `uv remove <package>`
- Keep lockfile updated after dependency changes.

## Lockfile and Reproducibility
- Commit `uv.lock` when dependencies change.
- In CI and local verification, prefer locked environment:
  - `uv sync --frozen`
- Use `uv lock --check` to ensure lock consistency when needed.

## Python Version
- Pin and align Python version across local and CI (for example via `.python-version`).
- When changing Python version, update related tooling/config together.

## Agent Execution Rules
- Before running tests or linters, ensure environment is synced (`uv sync`).
- Prefer deterministic commands suitable for CI.
- Keep changes minimal and avoid unrelated dependency upgrades.
