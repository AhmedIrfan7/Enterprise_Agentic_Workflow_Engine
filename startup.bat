@echo off
setlocal EnableDelayedExpansion

echo.
echo  ============================================================
echo   Enterprise Agentic Workflow Engine - Windows Startup
echo  ============================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

REM ── Backend env ──────────────────────────────────────────────────────────────
if not exist "%BACKEND_DIR%\.env" (
    echo [WARN] backend\.env not found. Copying from .env.example...
    copy "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env" >nul
    echo [WARN] Set OPENAI_API_KEY in backend\.env before running agents.
    echo.
)

REM ── Python venv ──────────────────────────────────────────────────────────────
set "VENV_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
    echo [INFO] Creating Python virtual environment...
    python -m venv "%BACKEND_DIR%\.venv"
    if errorlevel 1 (
        echo [ERROR] Failed to create venv. Is Python 3.11+ installed?
        pause & exit /b 1
    )
)

echo [INFO] Installing backend dependencies...
"%BACKEND_DIR%\.venv\Scripts\pip.exe" install -q -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 (
    echo [ERROR] pip install failed. Check backend\requirements.txt.
    pause & exit /b 1
)

REM ── Start backend ────────────────────────────────────────────────────────────
echo [INFO] Starting FastAPI backend on http://localhost:8000 ...
start "EAWE Backend" cmd /k "cd /d %BACKEND_DIR% && .venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000"

REM ── npm install ──────────────────────────────────────────────────────────────
if not exist "%FRONTEND_DIR%\node_modules" (
    echo [INFO] Installing frontend npm packages ^(first run^)...
    cd /d "%FRONTEND_DIR%"
    npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed. Is Node.js 18+ installed?
        pause & exit /b 1
    )
)

REM ── Start frontend ───────────────────────────────────────────────────────────
echo [INFO] Starting React frontend on http://localhost:3000 ...
start "EAWE Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm start"

echo.
echo  ============================================================
echo   Both services are starting in separate windows.
echo   Frontend : http://localhost:3000
echo   API Docs : http://localhost:8000/api/docs
echo  ============================================================
echo.
pause
