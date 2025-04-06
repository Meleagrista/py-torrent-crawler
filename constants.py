import os

TORRENT_BASE_URL = os.getenv('TORRENT_BASE_URL', 'https://1337x.to')

NUMBER_OF_LINKS = int(os.getenv('NUMBER_OF_LINKS', 5))
LANGUAGES = os.getenv('LANGUAGES', 'English, Spanish').replace(' ', '').split(',')
