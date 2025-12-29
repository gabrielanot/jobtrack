@echo off
title JobTrack - Starting...

echo.
echo  ========================================
echo    JobTrack - AI Job Application Tracker
echo  ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Check if .env file exists
if not exist ".env" (
    echo [SETUP] First time setup - creating .env file...
    echo.
    set /p APIKEY="Enter your Anthropic API key: "
    echo ANTHROPIC_API_KEY=%APIKEY%> .env
    echo.
    echo [OK] API key saved!
    echo.
)

:: Check if virtual environment exists
if not exist ".venv" (
    echo [SETUP] Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install dependencies
echo [SETUP] Installing dependencies (this may take a minute)...
pip install -q -r requirements.txt

:: Create uploads directory
if not exist "uploads\resumes" mkdir uploads\resumes

echo.
echo  ========================================
echo    Starting JobTrack...
echo  ========================================
echo.
echo  Open your browser to: http://localhost:8000
echo.
echo  Press Ctrl+C to stop the server
echo  ========================================
echo.

:: Start the server
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

pause
