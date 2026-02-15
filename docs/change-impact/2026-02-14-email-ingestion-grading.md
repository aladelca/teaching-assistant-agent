# Change Impact Template

## Request Summary
- Request: Add support so an operator can send an email with student submission attachments, trigger grading, and receive a reply email with gradebook CSV attached.
- Owner: Adrian / teaching-assistant-agent
- Date: 2026-02-14

## Scope
- In scope:
  - IMAP inbox polling for unseen messages.
  - Attachment extraction (zip and direct notebook files).
  - Batch grading execution using existing `run_batch` pipeline.
  - SMTP reply with `gradebook_summary.csv` attachment.
  - New CLI entrypoint and README usage section.
  - Unit tests for parsing, extraction, and reply composition.
- Out of scope:
  - Hosting/deployment daemonization.
  - OAuth-based Gmail API integration.
  - Rich anti-spam/abuse filtering.
  - Full mailbox workflow automation in external tools.

## Affected Components
- Files/modules:
  - `mvp_agent/email_inbox.py` (new)
  - `mvp_agent/email_cli.py` (new)
  - `pyproject.toml` (new script entrypoint)
  - `README.md` (new section)
  - `tests/test_email_inbox.py` (new)
- External dependencies:
  - Python stdlib only (`imaplib`, `smtplib`, `email`, `zipfile`, etc.).
- Data/API/schema touchpoints:
  - IMAP server for read operations.
  - SMTP server for outbound replies.
  - Existing `run_batch` input/output directories.

## Impact Analysis
- Functional impact:
  - Enables email-driven grading loop from inbound attachment to outbound CSV response.
- Backward compatibility:
  - No breaking change to existing CLIs or APIs.
- Security impact:
  - Introduces credential handling for IMAP/SMTP; mitigated by env vars and no logging of secrets.
  - Attachment extraction confined to controlled temp/output paths.
- Performance impact:
  - Minimal overhead; grading time remains dominant cost.
- Operational impact:
  - Requires mail credentials and periodic execution (`cron`, systemd timer, or manual run).

## Risk Assessment
- Risk level: Medium
- Main risks:
  - Malformed/large attachments.
  - Incorrect MIME parsing in real-world emails.
  - SMTP send failures and transient network errors.
- Mitigations:
  - Defensive parsing, file type checks, and extraction safeguards.
  - Explicit status/error reporting in reply body.
  - Exceptions surfaced per-message without crashing full run.

## Test Plan
- Unit tests:
  - Subject-to-assignment parsing.
  - Safe attachment extraction and zip handling.
  - Reply message composition with CSV attachment.
- Integration tests:
  - CLI dry-run path with mocked mail clients.
- Regression tests:
  - Existing test suite (`pytest`) must stay green.
- Manual verification:
  - Send sample email with zip of notebooks and validate CSV reply.

## Rollback Plan
- Revert strategy:
  - Revert branch/commit introducing email modules and script entrypoint.
- Data recovery notes:
  - Generated output directories are additive and can be removed safely.

## Sign-off
- Ready for implementation: Yes
