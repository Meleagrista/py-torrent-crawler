from typing import Tuple, List
from bs4 import BeautifulSoup
from pydantic import Field
from enum import Enum

from src.constants import TORRENT_BASE_URL, NUMBER_OF_LINKS
from src.schemas.page_schema import Page
from src.schemas.torrent_schema import Torrent
from src.utils.requests import fecther


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


class Movie(Page):
    title: str = Field(..., description="The title of the movie.")
    genres: Tuple['Genre', ...] = Field(..., description="A tuple of genres associated with the movie.")
    summary: str = Field(..., description="A brief summary of the movie plot.")
    poster: str = Field(..., description="The URL or path to the movie poster image.")
    rating: float = Field(..., ge=0.0, le=100.0, description="The rating of the movie.")
    torrents: List['Torrent'] = Field(..., description="A tuple of torrents available for the movie.")

    def __eq__(self, other):
        if not isinstance(other, Movie):
            return False
        return self.title == other.title

    def __hash__(self):
        return hash(self.title)

    @classmethod
    def from_url(cls, url: str) -> 'Movie':
        response = fecther.fetch_url(url)
        if not response:
            raise ValueError("Failed to fetch the URL.")

        soup = BeautifulSoup(response, 'html.parser')

        title_element = soup.select_one(".torrent-detail-info h3 a")
        title = title_element.text.strip() if title_element else None
        if not title:
            raise ValueError("No title found for URL.")

        genres = tuple(Genre(g.text.strip()) for g in soup.select(".torrent-category span") if g.text.strip())
        summary_element = soup.select_one(".torrent-detail-info p")
        summary = summary_element.text.strip() if summary_element else "No summary available."

        rating_element = soup.select_one(".rating .red")
        rating = (
            float(rating_element["style"].split(":")[1].strip("%;")) / 100
            if rating_element else 0.0
        )

        image_element = soup.select_one(".torrent-image img")
        image_url = f"https:{image_element['src']}" if image_element else None

        torrents = []
        torrent_data = []
        for row in soup.select('tbody tr'):
            link = row.select_one('td.coll-1 a[href^="/torrent/"]')
            if not link:
                continue

            torrent_link = TORRENT_BASE_URL + link["href"]
            seeder_count = row.select_one('td.coll-2.seeds')
            seeders = int(seeder_count.text.strip()) if seeder_count else 0
            torrent_data.append((torrent_link, seeders))

        sorted_torrents = sorted(torrent_data, key=lambda x: x[1], reverse=True)
        sorted_torrent_links = [torrent[0] for torrent in sorted_torrents]

        for link in sorted_torrent_links:
            torrent = Torrent.from_url(link)
            if torrent:
                torrents.append(torrent)
            if len(torrents) >= NUMBER_OF_LINKS:
                break

        movie = Movie(
            url=url,
            metadata={'torrent_links': sorted_torrent_links},
            title=title,
            genres=genres,
            summary=summary,
            rating=rating,
            poster=image_url,
            torrents=torrents,
        )

        return movie
