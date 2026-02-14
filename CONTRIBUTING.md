# Contributing

## Scope
This project is open source and primarily used for internal academic operations.
External contributions are welcome when they align with repository goals.

## Development Setup
```bash
uv sync --extra dev --extra exec
```

## Quality Checks
Run these commands before opening a pull request:
```bash
uv run ruff check .
uv run pytest -q
uv run python -m build
```

## Pull Requests
- Keep PRs focused and small.
- Include tests when behavior changes.
- Update docs when CLI flags, outputs, or security assumptions change.
- Follow the behavior guidelines in `CODE_OF_CONDUCT.md`.

## Commit and Release Notes
- Use descriptive commit messages.
- For user-facing changes, add a short note in `README.md` or `docs/`.

## Security
Do not commit secrets or student-sensitive data.
See `SECURITY.md` for reporting and secret handling.
