# Change Impact

## Request Summary
- Request: Add batch grading capabilities for student submissions in folders keyed by `apellidos_nombres`, with rubric-based grading and consolidated CSV output.
- Owner: Adrian
- Date: 2026-02-14

## Scope
- Add batch CLI to scan a submissions root and grade each student folder.
- Reuse existing grading pipeline for each notebook.
- Support folder-name pattern filtering (`apellidos_nombres`).
- Generate consolidated summary CSV with score/status/feedback metadata.
- Expose CLI interaction entrypoint for operational use.
- Add tests for batch workflow and summary generation.
- Update README and packaging entrypoints.

## Risk
- Medium: introduces orchestration over many submissions; failures must be isolated per student.

## Backward Compatibility
- Backward compatible. Existing single-student CLI behavior remains unchanged.

## Security / Performance
- No new external network dependencies required in mock mode.
- Per-student isolation in batch run reduces blast radius for malformed submissions.

## Test Plan
- `python3 -m pytest -q`

## Rollback Plan
- Revert merge commit to remove batch orchestration and restore single-run-only operation.
