import os
from pathlib import Path

default_download_path = Path.home() / 'Downloads'
TORRENT_DOWNLOAD_PATH = Path(os.getenv('TORRENT_DOWNLOAD_PATH', default_download_path))

default_torrent_base_url = 'https://1337x.to'
TORRENT_BASE_URL = os.getenv('TORRENT_BASE_URL', default_torrent_base_url)

default_number_of_links = 5
NUMBER_OF_LINKS = int(os.getenv('NUMBER_OF_LINKS', default_number_of_links))

default_languages = 'English, Spanish'
LANGUAGES = os.getenv('LANGUAGES', default_languages).replace(' ', '').split(',')
