# Operational Security Notes

## Notebook Execution
- Prefer `--exec-mode docker` for untrusted notebooks.
- Keep Docker network isolated (`--docker-network none` unless strictly needed).
- Set bounded resources (`--docker-cpus`, `--docker-memory`, `--execution-timeout`).
- Store execution outputs in controlled folders and avoid public sharing.

## Review UI
- Default host is localhost (`127.0.0.1`).
- Set `REVIEW_UI_TOKEN` in internal environments.
- Do not expose the review UI directly to the public internet.

## Browser Assist
- Do not hardcode credentials in step JSON files.
- Avoid reusing `storage_state.json` across users.
- Treat uploaded CSVs and feedback files as potentially sensitive.

## Secrets in GitHub Actions
- Use repository/environment secrets, never plaintext in workflows.
- Limit secret scope to the minimum environments/jobs required.
- Rotate secrets periodically and after staff changes.
