import hashlib
import re
from enum import Enum
from typing import List
from pydantic import Field

from src.schemas.torrent_schema import Torrent, Object


class MediaType(str, Enum):
    MOVIE = "movie"


class Media(Object):
    id: int = Field(..., description="The unique identifier of this piece of media.")
    media: MediaType = Field(..., description="Type of media.")
    torrents: List['Torrent'] = Field(..., description="A list of the loaded torrents for this piece of media.")
    torrents_count: int = Field(..., description="The total number of torrents available for this piece of media.")

    @staticmethod
    def generate_id(title: str, url: str) -> int:
        title = title.strip().lower()
        url = url.strip().lower()

        unique_str = f"{title}|{url}"
        hash_digest = hashlib.sha256(unique_str.encode('utf-8')).hexdigest()

        # Remove letters and get digits only
        numeric_id = int(re.sub(r'\D', '', hash_digest)) % (10 ** 10)
        return numeric_id