#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it from https://docs.astral.sh/uv/getting-started/installation/"
  exit 1
fi

extras=("dev" "exec")
for extra in "$@"; do
  extras+=("$extra")
done

args=()
for extra in "${extras[@]}"; do
  args+=(--extra "$extra")
done

echo "Syncing project environment with uv..."
uv sync "${args[@]}"

if [[ ! -f .env && -f .env.example ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo
echo "Bootstrap completed."
echo "Run commands with:"
echo "  uv run python -m mvp_agent.cli --help"
echo
echo "If you plan to use Codex auth provider:"
echo "  codex login"
