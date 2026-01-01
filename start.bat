@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo.
echo ==========================================
echo     JobTrack - AI Job Application Tracker
echo ==========================================
echo.

:: Check if this is first run (no .env or no mode set)
set "NEED_SETUP=0"
if not exist .env (
    set "NEED_SETUP=1"
) else (
    findstr /C:"JOBTRACK_AI_MODE=" .env >nul 2>&1
    if !errorlevel! neq 0 (
        set "NEED_SETUP=1"
    )
)

:: First time setup
if "!NEED_SETUP!"=="1" (
    echo ============================================
    echo   FIRST TIME SETUP
    echo ============================================
    echo.
    echo Choose your AI mode:
    echo.
    echo   [1] FREE - Basic keyword matching
    echo       No setup required, works offline
    echo       Good for: Quick ATS score estimates
    echo.
    echo   [2] FREE + OLLAMA - Local AI ^(Recommended^)
    echo       Requires: Ollama installed ^(free^)
    echo       Good for: Full AI features, 100%% free
    echo.
    echo   [3] CLAUDE API - Best quality ^(Paid^)
    echo       Requires: Anthropic API key
    echo       Good for: Best results, ~$0.01/analysis
    echo.
    echo ============================================
    echo.
    
    set /p "MODE_CHOICE=Enter choice (1, 2, or 3): "
    
    if "!MODE_CHOICE!"=="1" (
        echo JOBTRACK_AI_MODE=free> .env
        echo.
        echo [OK] Free mode selected - basic keyword matching
        echo.
    ) else if "!MODE_CHOICE!"=="2" (
        echo JOBTRACK_AI_MODE=ollama> .env
        echo.
        echo [OK] Ollama mode selected
        echo.
        echo --------------------------------------------
        echo To use Ollama:
        echo   1. Download from: https://ollama.ai
        echo   2. Install and run Ollama
        echo   3. Open a terminal and run: ollama pull llama3.2
        echo   4. Keep Ollama running in background
        echo --------------------------------------------
        echo.
        pause
    ) else if "!MODE_CHOICE!"=="3" (
        echo.
        echo You need an Anthropic API key.
        echo Get one at: https://console.anthropic.com/settings/keys
        echo.
        set /p "API_KEY=Paste your API key (starts with sk-ant-): "
        
        if defined API_KEY (
            echo JOBTRACK_AI_MODE=claude> .env
            echo ANTHROPIC_API_KEY=!API_KEY!>> .env
            echo.
            echo [OK] Claude mode configured!
            echo.
        ) else (
            echo.
            echo [WARNING] No API key entered, falling back to free mode
            echo JOBTRACK_AI_MODE=free> .env
            echo.
        )
    ) else (
        echo.
        echo [INFO] Invalid choice, using free mode
        echo JOBTRACK_AI_MODE=free> .env
        echo.
    )
)

:: Show current mode
echo.
for /f "tokens=1,* delims==" %%a in ('findstr /C:"JOBTRACK_AI_MODE=" .env 2^>nul') do (
    echo Current AI Mode: %%b
)
echo.

:: Check if Python is installed
echo [CHECK] Looking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
python --version
echo [OK] Python found!

:: Install dependencies if needed
if not exist ".deps_installed" (
    echo.
    echo [SETUP] Installing dependencies - this may take a minute...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install dependencies.
        echo.
        pause
        exit /b 1
    )
    echo. > .deps_installed
    echo.
    echo [OK] Dependencies installed!
)

echo.
echo ==========================================
echo     Starting JobTrack...
echo ==========================================
echo.
echo Open your browser to: http://localhost:8000
echo.
echo To stop: Close this window or press Ctrl+C
echo.
echo To change AI mode: Delete .env and restart
echo ==========================================
echo.

:: Start the server
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

:: If we get here, the server stopped or crashed
echo.
echo ==========================================
echo Server stopped or encountered an error.
echo ==========================================
echo.
pause