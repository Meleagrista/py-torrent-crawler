import os
from pathlib import Path

from rich.box import Box

# ─────────────────────────────────────────────
# PATH CONFIGURATION
# ─────────────────────────────────────────────

SRC_ROOT = Path(__file__).parent.parent

# Download path
TORRENT_DOWNLOAD_PATH = Path.home() / 'downloads'

# Cache directory for history and store files
CACHE_DIR = Path.home() / '.cache' / 'storage'

# ─────────────────────────────────────────────
# FILE SYSTEM INITIALIZATION
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
TORRENT_BASE_URL = 'https://1337x.to'

# Search depth (how many pages to crawl)
default_search_depth = 2
TORRENT_SEARCH_DEPTH = int(os.environ.get('TORRENT_FILES_PER_MOVIE', default_search_depth))

# Supported languages
default_languages = 'English, Spanish'
TORRENT_SUPPORTED_LANGUAGES = os.environ.get('TORRENT_SUPPORTED_LANGUAGES', default_languages).replace(' ', '').split(',')
TORRENT_SUPPORTED_LANGUAGES = [lang.capitalize() for lang in TORRENT_SUPPORTED_LANGUAGES]

# Chrome binary path
CHROME_BINARY = '/usr/bin/chromium'

# Selenium load strategy
default_load_strategy = 'normal'
SELENIUM_LOAD_STRATEGY = os.environ.get("SELENIUM_LOAD_STRATEGY", default_load_strategy)

# Terminal display settings
default_terminal_width = 150
TERMINAL_WIDTH = int(os.environ.get("TERMINAL_WIDTH", default_terminal_width))

# ─────────────────────────────────────────────
# RICH TERMINAL SETTINGS
# ─────────────────────────────────────────────

DASH_HEAD: Box = Box(
    "    \n"
    "    \n"
    "----\n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
)




