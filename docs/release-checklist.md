# Release Checklist

## Before Tagging
- Confirm `README.md`, `SECURITY.md`, and `CONTRIBUTING.md` are up to date.
- Run local checks:
  - `python -m ruff check .`
  - `python -m pytest -q`
  - `python -m build`
  - `python -m twine check dist/*`
- Verify no secrets are committed.
- Ensure `PYPI_API_TOKEN` is configured if publishing to PyPI.

## Create Release Tag
- Choose next semantic version (`vMAJOR.MINOR.PATCH`).
- Create and push tag:
  - `git tag vX.Y.Z`
  - `git push origin vX.Y.Z`

## After Workflow Completes
- Verify artifacts exist in the GitHub Release.
- Validate install from wheel in a clean environment.
- Announce changes to internal users with migration notes if needed.
