import logging
import os
from pathlib import Path

class TruncateFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', max_length=500):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.max_length = max_length

    def format(self, record):
        msg = super().format(record)
        if len(msg) > self.max_length:
            msg = msg[:self.max_length - 3] + ".."
        return msg

script_name = os.path.basename(__file__)

handler = logging.StreamHandler()
handler.setFormatter(TruncateFormatter(
    fmt=f"[%(levelname)s] <{script_name}> %(message)s", max_length=200
))

logging.basicConfig(
    level=logging.CRITICAL,
    handlers=[handler]
)

SRC_ROOT = Path(__file__).parent.parent

default_download_path = Path.home() / 'downloads'
TORRENT_DOWNLOAD_PATH = default_download_path

default_base_url = 'https://1337x.to'
TORRENT_BASE_URL = default_base_url

default_search_depth = 2
TORRENT_SEARCH_DEPTH = int(os.getenv('SEARCH_DEPTH', default_search_depth))

default_supported_languages = 'English, Spanish'
TORRENT_SUPPORTED_LANGUAGES = os.getenv('SUPPORTED_LANGUAGES', default_supported_languages).replace(' ', '').split(',')

# Create the directory if it doesn't exist
TORRENT_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)

default_chrome_binary_path = '/usr/bin/chromium'
CHROME_BINARY = os.environ.get("CHROME_BINARY", default_chrome_binary_path)

MOVIE_TABLE_FORMAT = {
    'id_width': 10,
    'title_width': 50,
    'rating_width': 6,
    'genres_width': 40,
    'torrents_width': 8,
    'margin': 2
}