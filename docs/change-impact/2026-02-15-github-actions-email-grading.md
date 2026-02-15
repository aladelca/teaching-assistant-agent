# Change Impact Template

## Request Summary
- Request: Add a GitHub Actions workflow to run email-driven grading on schedule/manual trigger using repository secrets for IMAP/SMTP and optional LLM body parsing.
- Owner: Adrian / teaching-assistant-agent
- Date: 2026-02-15

## Scope
- In scope:
  - New workflow file under `.github/workflows/`.
  - Scheduled + manual trigger.
  - Runtime setup (`uv`, Python).
  - Invocation of `mvp_agent.email_cli`.
  - Optional artifact upload for outputs.
- Out of scope:
  - Secret provisioning itself (done in GitHub settings by repo admin).
  - Changes to core grading logic.
  - Infra beyond GitHub-hosted runners.

## Affected Components
- Files/modules:
  - `.github/workflows/email-grading.yml` (new)
  - `README.md` (short section for Actions setup)
- External dependencies:
  - GitHub Actions runners
  - `astral-sh/setup-uv`, `actions/setup-python`, `actions/upload-artifact`
- Data/API/schema touchpoints:
  - IMAP/SMTP endpoints via secrets
  - LLM endpoint via secrets (optional)

## Impact Analysis
- Functional impact:
  - Enables unattended periodic inbox processing and grading via CI runner.
- Backward compatibility:
  - No breaking changes to existing CLI or package behavior.
- Security impact:
  - Uses GitHub Secrets for credentials.
  - No secrets printed in logs.
- Performance impact:
  - Job runtime bounded by `timeout-minutes`; no local performance impact.
- Operational impact:
  - Requires correct secret setup and mail provider app-password policies.

## Risk Assessment
- Risk level: Medium
- Main risks:
  - Misconfigured SMTP/IMAP secrets.
  - Overlapping scheduled runs.
  - Runner limits for heavy submission volumes.
- Mitigations:
  - Add `concurrency` key to avoid overlap.
  - Keep timeout bounded and schedule reasonable.
  - Upload outputs as artifacts for observability.

## Test Plan
- Unit tests:
  - N/A (workflow-only change).
- Integration tests:
  - Manual `workflow_dispatch` run in GitHub Actions.
- Regression tests:
  - Existing CI remains unchanged.
- Manual verification:
  - Trigger workflow with test email and validate reply + artifacts.

## Rollback Plan
- Revert strategy:
  - Revert workflow commit.
- Data recovery notes:
  - No persistent schema/data changes.

## Sign-off
- Ready for implementation: Yes
