#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  run.sh  –  Start the AI Resume Builder (Linux / macOS / WSL / Git Bash)
#  Usage:  bash run.sh
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

ok()   { echo -e "  ${GREEN}[OK]${RESET}   $*"; }
warn() { echo -e "  ${YELLOW}[WARN]${RESET} $*"; }
err()  { echo -e "  ${RED}[ERROR]${RESET} $*"; exit 1; }
info() { echo -e "  [INFO] $*"; }

echo ""
echo -e "${BOLD} ╔══════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD} ║        AI Resume Builder – Startup           ║${RESET}"
echo -e "${BOLD} ╚══════════════════════════════════════════════╝${RESET}"
echo ""

# ── 1. Check .env exists ─────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    err ".env file not found. Copy .env.example to .env and fill in your keys."
fi
ok ".env found."

# ── 2. Create / activate virtual environment ──────────────────────────────────
if [ ! -d ".venv" ]; then
    warn ".venv not found. Creating virtual environment with uv..."
    uv venv || err "Failed to create venv. Make sure 'uv' is installed: pip install uv"
    ok "Virtual environment created."
fi

# Activate (works in bash/zsh; for fish use: source .venv/bin/activate.fish)
# shellcheck disable=SC1091
source .venv/bin/activate
ok "Virtual environment activated."

# ── 3. Install / sync dependencies ───────────────────────────────────────────
info "Syncing dependencies from requirements.txt..."
uv pip install -r requirements.txt --quiet
ok "Dependencies ready."

# ── 4. Launch Streamlit ───────────────────────────────────────────────────────
echo ""
info "Starting Streamlit app on http://localhost:8501 ..."
info "Press Ctrl+C to stop."
echo ""

streamlit run app.py
