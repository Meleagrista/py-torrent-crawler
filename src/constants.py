import os
from pathlib import Path

SRC_ROOT = Path(__file__).parent.parent

default_download_path = SRC_ROOT / 'devops/bind'
TORRENT_DOWNLOAD_PATH = Path(os.getenv('TORRENT_DOWNLOAD_PATH', default_download_path))

# Create the directory if it doesn't exist
TORRENT_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)

default_torrent_base_url = 'https://1337x.to'
TORRENT_BASE_URL = os.getenv('TORRENT_BASE_URL', default_torrent_base_url)

default_number_of_links = 5
NUMBER_OF_LINKS = int(os.getenv('NUMBER_OF_LINKS', default_number_of_links))

default_languages = 'English, Spanish'
LANGUAGES = os.getenv('LANGUAGES', default_languages).replace(' ', '').split(',')

default_chrome_binary_path = '/usr/bin/chromium'
CHROME_BINARY = os.environ.get("CHROME_BINARY", default_chrome_binary_path)
