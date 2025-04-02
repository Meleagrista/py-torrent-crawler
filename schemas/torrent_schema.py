from datetime import datetime
from pydantic import BaseModel

from enums.categories import Category
from enums.languages import Language


class Comment(BaseModel):
    user: str
    message: str
    year: int


class Torrent(BaseModel):
    category: Category
    language: Language
    date: datetime
    size: float
    uploader: str
    downloads: int
    seeders: int
    comments: list[Comment] = []
