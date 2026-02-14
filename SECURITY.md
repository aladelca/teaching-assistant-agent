# Security Policy

## Supported Usage
This repository is maintained for active development on the default branch.
Security fixes are applied to the latest release line.

## Reporting a Vulnerability
Please report vulnerabilities privately to project maintainers instead of opening a public issue.
Include:
- Affected component or command.
- Reproduction steps.
- Impact assessment.
- Suggested remediation (if available).

## Secret Management
- Never commit credentials to the repository.
- Use local environment variables or `.env` files excluded from git.
- In GitHub, store credentials in `Settings -> Secrets and variables -> Actions`.
- Prefer environment-scoped secrets for release pipelines.

Suggested secret names:
- `OPENAI_API_KEY`
- `LLM_API_KEY`
- `LLM_API_URL`
- `LLM_MODEL`
- `PYPI_API_TOKEN` (only if publishing to PyPI)

## Operational Notes
- `review_ui` is intended for local usage.
- Notebook execution can run untrusted code; use Docker isolation for safer operation.
- See `docs/operational-security.md` for recommended runtime controls.
