# Release Ownership

## Maintainer of Record
- Owner: Adrian Alarcon

## Responsibilities
- Approve release scope and target version.
- Ensure CI is green for the release commit.
- Validate package artifacts (`sdist` and wheel).
- Approve and push release tags (`vMAJOR.MINOR.PATCH`).
- Ensure secrets used in release workflows are valid and scoped.

## Release Approval Rule
- At least one maintainer approval is required before pushing a release tag.
- Emergency hotfix releases must be documented in the release notes.
