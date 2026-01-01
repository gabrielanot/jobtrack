@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ==========================================
echo     JobTrack - AI Job Application Tracker
echo ==========================================
echo.

:: Check if .env file exists and has a VALID API key
set "HAS_KEY=0"
if exist .env (
    for /f "tokens=1,* delims==" %%a in (.env) do (
        if "%%a"=="ANTHROPIC_API_KEY" (
            set "KEY_VALUE=%%b"
            if defined KEY_VALUE (
                echo %%b | findstr /B "sk-ant" >nul 2>&1
                if !errorlevel! equ 0 (
                    set "HAS_KEY=1"
                    echo [OK] Found valid API key in .env
                )
            )
        )
    )
)

:: If no valid API key, prompt the user
if "!HAS_KEY!"=="0" (
    echo.
    echo ============================================
    echo   FIRST TIME SETUP - API Key Required
    echo ============================================
    echo.
    echo To use AI features, you need an Anthropic API key.
    echo.
    echo 1. Go to: https://console.anthropic.com/settings/keys
    echo 2. Sign in or create an account
    echo 3. Create a new API key
    echo 4. Copy it - starts with sk-ant-api03-...
    echo.
    echo ============================================
    echo.
    set /p "API_KEY=Paste your API key here: "
    
    if defined API_KEY (
        :: Validate key format
        echo !API_KEY! | findstr /B "sk-ant" >nul 2>&1
        if !errorlevel! equ 0 (
            :: Create .env file
            echo ANTHROPIC_API_KEY=!API_KEY!> .env
            echo.
            echo [OK] API key saved successfully!
            echo.
        ) else (
            echo.
            echo [WARNING] Key doesn't look valid - should start with sk-ant
            echo           Saving anyway - you can edit .env later if needed.
            echo ANTHROPIC_API_KEY=!API_KEY!> .env
            echo.
        )
    ) else (
        echo.
        echo [SKIP] No API key entered.
        echo        AI features will not work until you add one.
        echo        Edit the .env file to add: ANTHROPIC_API_KEY=your-key
        echo.
        pause
    )
)

:: Check if Python is installed
echo.
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