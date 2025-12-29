#!/bin/bash

echo ""
echo "========================================"
echo "  JobTrack - AI Job Application Tracker"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo ""
    echo "Install Python:"
    echo "  Mac: brew install python3"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo ""
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[SETUP] First time setup - creating .env file..."
    echo ""
    read -p "Enter your Anthropic API key: " APIKEY
    echo "ANTHROPIC_API_KEY=$APIKEY" > .env
    echo ""
    echo "[OK] API key saved!"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "[SETUP] Installing dependencies (this may take a minute)..."
pip install -q -r requirements.txt

# Create uploads directory
mkdir -p uploads/resumes

echo ""
echo "========================================"
echo "  Starting JobTrack..."
echo "========================================"
echo ""
echo "  Open your browser to: http://localhost:8000"
echo ""
echo "  Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Start the server
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000