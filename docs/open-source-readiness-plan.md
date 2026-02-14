# Open-Source Readiness Plan

## Goal
Prepare this repository to be maintained as an open-source project while keeping operational usage internal and secure.

## Phase 1: Repository Baseline
Status: Initial Implementation Completed

Objectives:
- Ensure the repository is clean and reproducible.
- Define release ownership and versioning policy.

Tasks:
- Remove build artifacts and generated metadata from versioned files.
- Confirm release versioning strategy (`vMAJOR.MINOR.PATCH`).
- Document who can approve releases.

Deliverables:
- Clean working tree and stable local build process.
- Short release ownership note in docs.

## Phase 2: Legal and Packaging Metadata (MIT)
Status: Initial Implementation Completed

Objectives:
- Make legal usage explicit.
- Improve package metadata quality for distribution.

Tasks:
- Add an MIT `LICENSE`.
- Complete `pyproject.toml` metadata (`authors`, `license`, `classifiers`, `keywords`).
- Add packaging tools (`build`, `twine`) to development dependencies.

Deliverables:
- MIT-licensed repository.
- Package metadata suitable for public/internal distribution.

## Phase 3: Secrets and Configuration Hygiene
Status: Initial Implementation Completed

Objectives:
- Standardize local configuration without leaking credentials.
- Define a clear secret handling model for GitHub.

Tasks:
- Add `.env.example` with required environment variables.
- Harden `.gitignore` for `.env*`, build outputs, and packaging artifacts.
- Add secret-handling guidance (`SECURITY.md` + README pointers).

Deliverables:
- Safe configuration baseline for contributors.
- GitHub Secrets model documented.

## Phase 4: Continuous Integration
Status: Initial Implementation Completed

Objectives:
- Enforce quality checks automatically.
- Validate distribution artifacts in CI.

Tasks:
- Add CI workflow for lint, tests, build, and `twine check`.
- Run matrix tests for supported Python versions.
- Upload built artifacts to workflow outputs.

Deliverables:
- Green CI on pull requests and default branch pushes.

## Phase 5: Release Automation
Status: Initial Implementation Completed

Objectives:
- Make releases reproducible and low-friction.
- Support internal/public publication options.

Tasks:
- Add tag-based release workflow (`v*` tags).
- Build and attach `sdist`/wheel artifacts to GitHub Releases.
- Optionally publish to package index when a token is configured.

Deliverables:
- Automated, auditable release pipeline.

## Phase 6: Operational Security Hardening
Status: Initial Implementation Completed

Objectives:
- Reduce risk for internal operators.
- Keep behavior explicit for local-only tools.

Tasks:
- Add optional token protection for review UI.
- Document secure usage for notebook execution and browser automation.
- Keep local defaults safe (`localhost`, no credential persistence by default).

Deliverables:
- Reduced accidental exposure risk in internal deployments.

## Phase 7: Community and Maintenance Docs
Status: Initial Implementation Completed

Objectives:
- Define contribution and vulnerability-reporting expectations.

Tasks:
- Add `CONTRIBUTING.md`.
- Add `SECURITY.md`.
- Add a short release checklist.

Deliverables:
- Clear contributor and maintainer workflow.

## Phase 8: Final Validation
Status: In Progress

Objectives:
- Confirm the repository is release-ready end to end.

Tasks:
- Run lint, tests, and package build from a clean environment.
- Validate CLI smoke tests in mock mode.
- Validate CI and release workflows in GitHub.

Deliverables:
- Open-source-ready baseline with MIT licensing and secret-safe automation.
