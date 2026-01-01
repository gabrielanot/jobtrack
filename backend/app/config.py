"""
JobTrack Configuration

AI_MODE options:
- "claude"  : Uses Claude API (best quality, requires API key & payment)
- "ollama"  : Uses Ollama local AI (free, requires Ollama installed)
- "free"    : Uses keyword matching only (free, no setup, basic features)
"""

import os
from pathlib import Path

# Load from environment variable, or default to "free"
AI_MODE = os.getenv("JOBTRACK_AI_MODE", "free").lower()

# Valid modes
VALID_MODES = ["claude", "ollama", "free"]

if AI_MODE not in VALID_MODES:
    print(f"⚠ Invalid AI_MODE '{AI_MODE}', defaulting to 'free'")
    AI_MODE = "free"

# Ollama settings
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

def get_mode_description():
    """Return a description of the current mode"""
    descriptions = {
        "claude": "Claude API (best quality, paid)",
        "ollama": f"Ollama local AI ({OLLAMA_MODEL}, free)",
        "free": "Keyword matching (basic, free, no setup)"
    }
    return descriptions.get(AI_MODE, "Unknown")