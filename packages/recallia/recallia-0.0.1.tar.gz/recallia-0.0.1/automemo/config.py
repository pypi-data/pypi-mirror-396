import os
from pathlib import Path

# Core paths
BASE_DIR = Path('data')
INBOX_DIR = BASE_DIR / 'inbox'
ARCHIVE_DIR = BASE_DIR / 'archive'
ERROR_DIR = BASE_DIR / 'errors'
DB_PATH = BASE_DIR / 'db.sqlite3'
LOG_DIR = BASE_DIR / 'logs'

# AI settings
ASR_DEVICE = 'cuda'
LLM_MODEL = 'qwen2.5:14b'  # Use 32b if memory allows
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')


def ensure_directories() -> None:
    """Create required directories and files if missing."""
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    ERROR_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.touch(exist_ok=True)
