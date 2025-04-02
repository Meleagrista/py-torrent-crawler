from typing import Tuple

from pydantic import BaseModel

from enums.movies.genres import Genre
from schemas.torrent_schema import Torrent


class Movie(BaseModel):
    title: str
    genres: Tuple[Genre, ...]
    summary: str
    poster: str
    rating: float
    torrents: Tuple[Torrent, ...]

    def __eq__(self, other):
        if not isinstance(other, Movie):
            return False
        return self.title == other.title  # Compare only by title

    def __hash__(self):
        return hash(self.title)  # Hash using only title
