import logging
import urllib.parse

from typing import Set
from bs4 import BeautifulSoup

from enums.movies.genres import Genre
from schemas.movie_schema import Movie
from utils.requests import RobustFetcher

logger = logging.getLogger(__name__)

class MovieSearch:
    BASE_URL = "https://1337x.to"

    def __init__(self):
        self._search_url = self.BASE_URL + "/sort-category-search/{query}/Movies/seeders/desc/1/"

    def search(self, query: str) -> Set['Movie']:
        """
        Searches for movies based on the given query.

        :param query: Movie name or keyword to search for.
        :return: A set of Movie objects.
        """
        urls = self._get_movie_links(query)
        return self._get_movie_objects(urls)

    def _get_movie_links(self, query: str) -> Set[str]:
        """
        Fetches direct movie page URLs from the search results.

        :param query: Search query.
        :return: Set of movie page URLs.
        """
        formatted_query = urllib.parse.quote_plus(query)
        search_url = self._search_url.format(query=formatted_query)

        response = RobustFetcher.fetch_url(search_url)
        if not response:
            return set()

        soup = BeautifulSoup(response, 'html.parser')
        if "Bad search request" in soup.text or "Bad Category" in soup.text:
            logger.error("Invalid search or no results found.")
            return set()

        # Extract links to torrents
        torrent_links = {
            self.BASE_URL + link["href"]
            for link in soup.select('a[href^="/torrent/"]')
        }

        # Fetch movie links from each torrent page
        movie_links = set()
        for url in torrent_links:
            response = RobustFetcher.fetch_url(url)
            if not response:
                continue
            soup = BeautifulSoup(response, 'html.parser')

            movie_link = soup.select_one('a[href^="/movie/"]')
            if movie_link:
                movie_links.add(self.BASE_URL + movie_link["href"])

        return movie_links

    @staticmethod
    def _get_movie_objects(urls: Set[str]) -> Set['Movie']:
        """
        Extracts movie details from given URLs.

        :param urls: Set of movie page URLs.
        :return: Set of Movie objects.
        """
        movies = set()

        for url in urls:
            response = RobustFetcher.fetch_url(url)
            if not response:
                continue

            soup = BeautifulSoup(response, 'html.parser')

            # Extract title
            title_element = soup.select_one(".torrent-detail-info h3 a")
            title = title_element.text.strip() if title_element else None
            if not title:
                logger.warning(f"No title found for URL: {url}")
                continue

            # Extract genres
            genres = tuple(Genre(g.text.strip()) for g in soup.select(".torrent-category span") if g.text.strip())

            # Extract summary
            summary_element = soup.select_one(".torrent-detail-info p")
            summary = summary_element.text.strip() if summary_element else "No summary available."

            # Extract rating
            rating_element = soup.select_one(".rating .red")
            rating = (
                float(rating_element["style"].split(":")[1].strip("%;")) / 100
                if rating_element else 0.0
            )

            # Extract image
            image_element = soup.select_one(".torrent-image img")
            image_url = f"https:{image_element['src']}" if image_element else ""

            # Create Movie object
            movie = Movie(
                title=title,
                genres=genres,
                summary=summary,
                rating=rating,
                poster=image_url,
                torrents=tuple()
            )
            movies.add(movie)

        return movies
