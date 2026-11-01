@echo off
setlocal

echo.
echo  ============================================================
echo   AI Resume Builder v2 — Development Server
echo  ============================================================
echo.

:: ── Check Python ────────────────────────────────────────────────────────────
where python >nul 2>&1 || (echo [ERROR] Python not found. Install Python 3.11+ && exit /b 1)

:: ── Backend env ─────────────────────────────────────────────────────────────
if not exist backend\.env (
    echo [INFO] Copying backend\.env.example to backend\.env
    copy backend\.env.example backend\.env >nul
    echo [WARN] Edit backend\.env and add your API keys before first run!
)

:: ── Backend virtualenv ───────────────────────────────────────────────────────
if not exist backend\.venv (
    echo [INFO] Creating Python virtual environment...
    python -m venv backend\.venv
)
call backend\.venv\Scripts\activate.bat

:: ── Install backend deps ─────────────────────────────────────────────────────
echo [INFO] Installing backend dependencies...
pip install -q -r backend\requirements.txt

:: ── Check Node ───────────────────────────────────────────────────────────────
where node >nul 2>&1 || (echo [ERROR] Node.js not found. Install Node.js 20+ && exit /b 1)

:: ── Install frontend deps ────────────────────────────────────────────────────
if not exist frontend\node_modules (
    echo [INFO] Installing frontend dependencies...
    cd frontend && npm install && cd ..
)

echo.
echo  [INFO] Starting backend on http://localhost:8000
echo  [INFO] Starting frontend on http://localhost:5173
echo.
echo  Docs: http://localhost:8000/docs
echo  App:  http://localhost:5173
echo.

:: ── Start servers in parallel ────────────────────────────────────────────────
start "FastAPI Backend" cmd /k "cd backend && .venv\Scripts\python -m uvicorn app.main:app --reload --port 8000"
start "Vite Frontend"   cmd /k "cd frontend && npm run dev"

echo [INFO] Both servers started. Press any key to exit.
pause >nul
