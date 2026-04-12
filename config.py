"""
Centralized configuration for DB-Architect.
Loads settings from environment variables (supports .env files via python-dotenv).
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent / ".env")

# --- API Configuration ---
API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = os.environ.get("MODEL", "gpt-4o-mini")

if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
    print(
        "\n[ERROR] No valid API key found.\n"
        "       Set OPENAI_API_KEY in a .env file or as an environment variable.\n"
        "       See .env.example for reference.\n"
    )
    sys.exit(1)

# --- Pipeline Settings ---
MAX_REFLECTION_RETRIES = int(os.environ.get("MAX_REFLECTION_RETRIES", "5"))
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
