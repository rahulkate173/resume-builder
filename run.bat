@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM  run.bat  –  Start the AI Resume Builder (Windows)
REM  Usage:  run.bat
REM ─────────────────────────────────────────────────────────────────────────────

setlocal EnableDelayedExpansion

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║        AI Resume Builder – Startup           ║
echo  ╚══════════════════════════════════════════════╝
echo.

REM ── 1. Check .env exists ─────────────────────────────────────────────────────
if not exist ".env" (
    echo [ERROR] .env file not found. Copy .env.example to .env and fill in your keys.
    pause
    exit /b 1
)
echo [OK] .env found.

REM ── 2. Activate virtual environment ──────────────────────────────────────────
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [OK] Virtual environment activated.
) else (
    echo [WARN] .venv not found. Creating virtual environment with uv...
    uv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv. Make sure 'uv' is installed.
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
    echo [OK] Virtual environment created and activated.
)

REM ── 3. Install / sync dependencies ───────────────────────────────────────────
echo [INFO] Syncing dependencies from requirements.txt...
uv pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Dependency installation failed. Check requirements.txt.
    pause
    exit /b 1
)
echo [OK] Dependencies ready.

REM ── 4. Launch Streamlit ───────────────────────────────────────────────────────
echo.
echo [INFO] Starting Streamlit app on http://localhost:8501 ...
echo [INFO] Press Ctrl+C to stop.
echo.
streamlit run app.py

endlocal
