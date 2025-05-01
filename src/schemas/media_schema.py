from enum import Enum
from typing import List
from pydantic import Field

from src.schemas.torrent_schema import Torrent, Object


class MediaType(str, Enum):
    MOVIE = "movie"


class Media(Object):
    media: MediaType = Field(..., description="Type of media.")
    torrents: List['Torrent'] = Field(..., description="A list of the loaded torrents for this piece of media.")
    torrents_count: int = Field(..., description="The total number of torrents available for this piece of media.")