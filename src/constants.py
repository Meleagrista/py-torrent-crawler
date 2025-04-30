import os
from pathlib import Path

# ─────────────────────────────────────────────
# PATH CONFIGURATION
# ─────────────────────────────────────────────

SRC_ROOT = Path(__file__).parent.parent

# Download path
TORRENT_DOWNLOAD_PATH = Path.home() / 'downloads'

# Cache directory for history and store files
CACHE_DIR = Path.home() / '.cache' / 'storage'

# ─────────────────────────────────────────────
# FILESYSTEM INITIALIZATION
# ─────────────────────────────────────────────

TORRENT_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────
# FILES
# ─────────────────────────────────────────────

LOG_FILE = CACHE_DIR / '.logs'
HISTORY_FILE = CACHE_DIR / '.history'
MOVIE_STORE_FILE = CACHE_DIR / 'movie_store.json'

# ─────────────────────────────────────────────
# DEFAULTS & ENVIRONMENT CONFIGURATION
# ─────────────────────────────────────────────

# Base URL for torrent scraping
TORRENT_BASE_URL = os.environ.get('TORRENT_BASE_URL', 'https://1337x.to')

# Search depth (how many pages to crawl)
TORRENT_SEARCH_DEPTH = int(os.environ.get('SEARCH_DEPTH', 2))

# Supported languages
default_languages = 'English, Spanish'
TORRENT_SUPPORTED_LANGUAGES = os.environ.get('SUPPORTED_LANGUAGES', default_languages).replace(' ', '').split(',')

# Chrome binary path (for headless browsing if used)
CHROME_BINARY = os.environ.get("CHROME_BINARY", '/usr/bin/chromium')

# Terminal display settings
TERMINAL_WIDTH = int(os.environ.get("TERMINAL_WIDTH", 140))





