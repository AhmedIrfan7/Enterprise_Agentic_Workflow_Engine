#!/usr/bin/env bash
set -euo pipefail

RESET="\033[0m"
BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"

log() { echo -e "${CYAN}[EAWE]${RESET} $*"; }
ok()  { echo -e "${GREEN}[EAWE]${RESET} $*"; }
warn(){ echo -e "${YELLOW}[EAWE]${RESET} $*"; }
err() { echo -e "${RED}[EAWE ERROR]${RESET} $*" >&2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# ── Backend ──────────────────────────────────────────────────────────────────
log "Starting ${BOLD}backend${RESET} (FastAPI + Uvicorn)…"

if [ ! -f "$BACKEND_DIR/.env" ]; then
  warn ".env not found in backend/. Copying from .env.example…"
  cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
  warn "⚠  Set OPENAI_API_KEY in backend/.env before running agents."
fi

VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
  log "Creating Python virtual environment…"
  python3 -m venv "$BACKEND_DIR/.venv"
fi

log "Installing backend dependencies…"
"$BACKEND_DIR/.venv/bin/pip" install -q -r "$BACKEND_DIR/requirements.txt"

cd "$BACKEND_DIR"
"$BACKEND_DIR/.venv/bin/uvicorn" app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
ok "Backend PID $BACKEND_PID → http://localhost:8000/api/docs"

# ── Frontend ─────────────────────────────────────────────────────────────────
log "Starting ${BOLD}frontend${RESET} (React + Webpack Dev Server)…"

cd "$FRONTEND_DIR"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  log "Installing frontend npm packages (first run — may take a minute)…"
  npm install --silent
fi

npm start &
FRONTEND_PID=$!
ok "Frontend PID $FRONTEND_PID → http://localhost:3000"

# ── Cleanup on exit ───────────────────────────────────────────────────────────
cleanup() {
  log "Shutting down…"
  kill "$BACKEND_PID" 2>/dev/null || true
  kill "$FRONTEND_PID" 2>/dev/null || true
  ok "All services stopped."
}
trap cleanup EXIT INT TERM

echo ""
ok "════════════════════════════════════════════════"
ok "  Enterprise Agentic Workflow Engine is running"
ok "  Frontend : http://localhost:3000"
ok "  API Docs : http://localhost:8000/api/docs"
ok "  Press Ctrl+C to stop both services."
ok "════════════════════════════════════════════════"
echo ""

wait
