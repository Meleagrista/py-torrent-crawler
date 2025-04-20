import logging
import time
import urllib.parse

from typing import Set
from bs4 import BeautifulSoup

from src.constants import TORRENT_BASE_URL
from src.schemas.movie_schema import Movie
from src.utils.requests_utils import requests

logger = logging.getLogger(__name__)


class MovieSearch:
    ERROR_INDICATORS = [
        "bad search request",
        "bad category",
        "access denied",
        "error 403",
        "you don't have permission",
        "page not found",
        "not available",
        "invalid request",
        "no results found"
    ]

    def __init__(self):
        self._search_url = TORRENT_BASE_URL + "/sort-category-search/{query}/Movies/seeders/desc/1/"

    def search(self, query: str) -> Set['Movie']:
        """
        Searches for movies based on the given query.

        :param query: Movie name or keyword to search for.
        :return: A set of Movie objects.
        """
        urls = self._get_movie_links(query)
        movies = set()

        for url in urls:
            try:
                movie = Movie.from_url(url)
                movies.add(movie)
            except Exception as e:
                logger.error(f"Error fetching movie from URL {url}: {e}")
                continue
        return movies

    def _get_movie_links(self, query: str) -> Set[str]:
        """
        Fetches direct movie page URLs from the search results.

        :param query: Search query.
        :return: Set of movie page URLs.
        """
        formatted_query = urllib.parse.quote_plus(query)
        search_url = self._search_url.format(query=formatted_query)

        response = requests.fetch_url(search_url)
        if not response:
            return set()

        if any(err in response for err in self.ERROR_INDICATORS) or len(response) < 100:
            logger.error("Search failed or returned an invalid page.")
            return set()

        soup = BeautifulSoup(response, 'html.parser')

        # Extract links to torrents
        torrent_links = {
            TORRENT_BASE_URL + link["href"]
            for link in soup.select('a[href^="/torrent/"]')
        }

        # Fetch movie links from each torrent page
        movie_links = set()

        # Use copy to safely modify the set during iteration
        while torrent_links:
            url = torrent_links.pop()
            start_time = time.perf_counter()
            response = requests.fetch_url(url)

            if not response:
                continue

            soup = BeautifulSoup(response, 'html.parser')
            movie_link = soup.select_one('a[href^="/movie/"]')
            logger.debug(f"Fetched {url} in {(time.perf_counter() - start_time):.2f} seconds")

            if movie_link:
                movie_url = TORRENT_BASE_URL + movie_link["href"]
                movie_response = requests.fetch_url(movie_url)

                if not movie_response:
                    continue

                movie_soup = BeautifulSoup(movie_response, 'html.parser')
                movie_torrent_links = {
                    TORRENT_BASE_URL + link["href"]
                    for link in movie_soup.select('a[href^="/torrent/"]')
                }

                movie_links.add(movie_url)
                torrent_links -= movie_torrent_links

        return movie_links