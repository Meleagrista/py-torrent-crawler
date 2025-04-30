from enum import Enum
from typing import Tuple, Optional

from bs4 import BeautifulSoup
from pydantic import Field
from rich.box import Box
from rich.table import Table
from rich.text import Text

from src.constants import TORRENT_BASE_URL, TORRENT_SEARCH_DEPTH
from src.core.cli import console
from src.schemas.media_schema import Media, MediaType
from src.schemas.torrent_schema import Torrent
from src.utils.requests import requests

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

class Genre(str, Enum):
    ACTION = "Action"
    ADVENTURE = "Adventure"
    ANIMATION = "Animation"
    BRITISH = "British"
    COMEDY = "Comedy"
    CRIME = "Crime"
    DISASTER = "Disaster"
    DOCUMENTARY = "Documentary"
    DRAMA = "Drama"
    EASTERN = "Eastern"
    EROTIC = "Erotic"
    FAMILY = "Family"
    FAN_FILM = "Fan Film"
    FANTASY = "Fantasy"
    FILM_NOIR = "Film Noir"
    FOREIGN = "Foreign"
    HISTORY = "History"
    HOLIDAY = "Holiday"
    HORROR = "Horror"
    INDIE = "Indie"
    KIDS = "Kids"
    MUSIC = "Music"
    MUSICAL = "Musical"
    MYSTERY = "Mystery"
    NEO_NOIR = "Neo-noir"
    ROAD_MOVIE = "Road Movie"
    ROMANCE = "Romance"
    SCIENCE_FICTION = "Science Fiction"
    SHORT = "Short"
    SPORT = "Sport"
    SPORTING_EVENT = "Sporting Event"
    SPORTS_FILM = "Sports Film"
    SUSPENSE = "Suspense"
    TV_MOVIE = "TV Movie"
    THRILLER = "Thriller"
    WAR = "War"
    WESTERN = "Western"


class Movie(Media):
    title: str = Field(..., description="The title of the movie.")
    genres: Tuple['Genre', ...] = Field(..., description="A tuple of genres associated with the movie.")
    summary: str = Field(..., description="A brief summary of the movie plot.")
    poster: str = Field(..., description="The URL or path to the movie poster image.")
    rating: float = Field(..., ge=0.0, le=100.0, description="The rating of the movie.")

    def __eq__(self, other):
        if not isinstance(other, Movie):
            return False
        return self.title == other.title

    def __hash__(self):
        return hash(self.title)

    @classmethod
    def from_url(cls, url: str) -> 'Movie':
        response = requests.fetch_url(url)
        if not response:
            raise ValueError("Failed to fetch the URL.")

        soup = BeautifulSoup(response, 'html.parser')

        def get_text(selector: str) -> Optional[str]:
            el = soup.select_one(selector)
            return el.text.strip() if el else None

        title_raw = get_text(".featured-heading strong")
        if not title_raw:
            raise ValueError("No title found for URL.")
        title = title_raw.split("Download", 1)[-1].split("Torrents", 1)[0].strip()

        genres = tuple(Genre(g.text.strip()) for g in soup.select(".torrent-category span") if g.text.strip())
        summary = get_text(".torrent-detail-info p") or "No summary available."

        rating_style = soup.select_one(".rating .red")
        rating = float(rating_style["style"].split(":")[1].strip("%;")) if rating_style else 0.0

        image_el = soup.select_one(".torrent-image img")
        image_url = f"https:{image_el['src']}" if image_el else None

        torrent_rows = soup.select('tbody tr')
        torrent_data = []
        for row in torrent_rows:
            link = row.select_one('td.coll-1 a[href^="/torrent/"]')
            if link:
                torrent_url = TORRENT_BASE_URL + link["href"]
                seeds_text = row.select_one('td.coll-2.seeds')
                seeds = int(seeds_text.text.strip()) if seeds_text else 0
                torrent_data.append((torrent_url, seeds))

        sorted_links = [url for url, _ in sorted(torrent_data, key=lambda x: x[1], reverse=True)]
        torrents = [Torrent.from_url(link) for link in sorted_links[:TORRENT_SEARCH_DEPTH] if Torrent.from_url(link)]

        return cls(
            id=Media.generate_id(title, url),
            media=MediaType.MOVIE,
            url=url,
            metadata={'torrent_links': sorted_links},
            torrents=torrents,
            torrents_count=len(sorted_links),
            title=title,
            genres=genres,
            summary=summary,
            rating=rating,
            poster=image_url
        )

    @classmethod
    def print_details(cls, movies):
        table = Table(
            header_style=None,
            box=DASH_HEAD,
            expand=True,
            width=console.width,
            padding=(0, 2),
            pad_edge=False,
            show_edge=False,
        )

        table.add_column("ID")
        table.add_column("Title")
        table.add_column("Rating", justify="right")
        table.add_column("Languages")
        table.add_column("Genres")
        table.add_column("Torrents", justify="right")

        for movie in movies:
            table = movie.add_row(table)

        console.print(table)

    def add_row(self, table: Table) -> Table:
        languages_raw = list({torrent.language.capitalize() for torrent in self.torrents if torrent.language})

        id_content = Text(str(self.id).strip())
        title_content = Text(self.title)
        rating_content = Text(f"{self.rating:.1f}" if self.rating > 0.0 else "-")
        languages_content = Text(", ".join(languages_raw))
        genre_content = Text(", ".join(g.capitalize() for g in self.genres))
        torrents_content = Text(f"{len(self.torrents)}/{self.torrents_count}")

        table.add_row(id_content, title_content, rating_content, languages_content, genre_content, torrents_content)

        return table

    def print_summary(self):
        summary_content = Text(self.summary, style="italic")
        console.print(summary_content)

    def print_torrents(self):
        table = Table(
            header_style=None,
            box=DASH_HEAD,
            expand=True,
            width=console.width,
            padding=(0, 2),
            pad_edge=False,
            show_edge=False,
        )

        table.add_column("Category")
        table.add_column("Title")
        table.add_column("Seeders", justify="right")
        table.add_column("Size", justify="right")
        table.add_column("Language")
        table.add_column("Date")

        for torrent in self.torrents:
            table.add_row(
                str(torrent.category),
                str(torrent.title),
                str(torrent.seeders),
                str(torrent.size),
                str(torrent.language),
                str(torrent.date)
            )

        console.print(table)