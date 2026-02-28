# src/config.py
"""
Centralized configuration module.

Loads environment variables and provides configuration settings
for the application.
"""

# imports built-in modules
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_base_path() -> Path:
    """Get base path for both development and executable."""
    if getattr(sys, "frozen", False):
        # Running as executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent.parent


# Base directory
BASE_DIR: Path = get_base_path()

# Google Cloud configurations
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Gemini API configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "1"))
GEMINI_TOP_P = float(os.getenv("GEMINI_TOP_P", "0.95"))
GEMINI_TOP_K = int(os.getenv("GEMINI_TOP_K", "64"))
GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "8192"))

# Vertex AI configurations
VERTEX_AI_MODEL = os.getenv("VERTEX_AI_MODEL", "multimodalembedding@001")
VERTEX_AI_TOP_K = int(os.getenv("VERTEX_AI_TOP_K", "3"))

# File upload configurations
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
UPLOAD_TIMEOUT = int(os.getenv("UPLOAD_TIMEOUT", "180"))

# Directory configurations (relative to executable/script location)
DOCUMENTS_DIR: Path = BASE_DIR / "documents"
DB_DIR: Path = BASE_DIR / "db"
LOGS_DIR: Path = BASE_DIR / "logs"

# Create directories if they don't exist
DOCUMENTS_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


def validate_or_exit() -> None:
    """Validate required configurations."""
    if not GOOGLE_CLOUD_PROJECT:
        print("Error: GOOGLE_CLOUD_PROJECT not set in .env file")
        sys.exit(1)

    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set in .env file")
        sys.exit(1)
