#!/usr/bin/env bash
set -euo pipefail

echo ""
echo " ============================================================"
echo "  AI Resume Builder v2 — Development Server"
echo " ============================================================"
echo ""

# ── Check Python ────────────────────────────────────────────────────────────
command -v python3 >/dev/null 2>&1 || { echo "[ERROR] python3 not found. Install Python 3.11+"; exit 1; }

# ── Backend env ─────────────────────────────────────────────────────────────
if [ ! -f backend/.env ]; then
    echo "[INFO] Copying backend/.env.example → backend/.env"
    cp backend/.env.example backend/.env
    echo "[WARN] Edit backend/.env and add your API keys!"
fi

# ── Backend virtualenv ───────────────────────────────────────────────────────
if [ ! -d backend/.venv ]; then
    echo "[INFO] Creating Python virtual environment..."
    python3 -m venv backend/.venv
fi
source backend/.venv/bin/activate

# ── Install backend deps ─────────────────────────────────────────────────────
echo "[INFO] Installing backend dependencies..."
pip install -q -r backend/requirements.txt

# ── Check Node ───────────────────────────────────────────────────────────────
command -v node >/dev/null 2>&1 || { echo "[ERROR] Node.js not found. Install Node.js 20+"; exit 1; }

# ── Install frontend deps ────────────────────────────────────────────────────
if [ ! -d frontend/node_modules ]; then
    echo "[INFO] Installing frontend dependencies..."
    (cd frontend && npm install)
fi

echo ""
echo " [INFO] Starting backend  → http://localhost:8000"
echo " [INFO] Starting frontend → http://localhost:5173"
echo ""
echo " Docs: http://localhost:8000/docs"
echo " App:  http://localhost:5173"
echo ""

# ── Start both servers ────────────────────────────────────────────────────────
(cd backend && uvicorn app.main:app --reload --port 8000) &
BACKEND_PID=$!

(cd frontend && npm run dev) &
FRONTEND_PID=$!

echo "[INFO] Backend PID: $BACKEND_PID | Frontend PID: $FRONTEND_PID"
echo "[INFO] Press Ctrl+C to stop both servers."

# ── Graceful shutdown ────────────────────────────────────────────────────────
trap "echo ''; echo '[INFO] Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait
