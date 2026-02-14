#!/usr/bin/env bash
set -euo pipefail

PACKAGE_NAME="${MVP_AGENT_PACKAGE_NAME:-mvp-agent-correccion}"
REPO_URL="${MVP_AGENT_REPO_URL:-https://github.com/aladelca/teaching-assistant-agent.git}"
EXTRAS="${MVP_AGENT_EXTRAS:-exec}"
INSTALL_CODEX="${MVP_AGENT_INSTALL_CODEX:-0}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv was not found. Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is still not available in PATH."
  echo "Add \$HOME/.local/bin to PATH and run this installer again."
  exit 1
fi

if [[ -n "$EXTRAS" ]]; then
  PACKAGE_SPEC="${PACKAGE_NAME}[${EXTRAS}] @ git+${REPO_URL}"
else
  PACKAGE_SPEC="${PACKAGE_NAME} @ git+${REPO_URL}"
fi

echo "Installing ${PACKAGE_SPEC}..."
uv tool install "$PACKAGE_SPEC"

echo
echo "Installation completed."
echo "If the commands are not found, run: uv tool update-shell"
echo "Then open a new terminal."
echo
echo "Quick check:"
echo "  mvp-agent --help"
echo "  mvp-agent-batch --help"

if [[ "$INSTALL_CODEX" == "1" ]]; then
  if command -v npm >/dev/null 2>&1; then
    echo
    echo "Installing Codex CLI..."
    npm i -g @openai/codex
    echo "Run: codex login"
  else
    echo
    echo "Skipping Codex CLI install because npm is not available."
    echo "Install Node.js and then run: npm i -g @openai/codex && codex login"
  fi
fi
