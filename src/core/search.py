import logging
import time
import urllib.parse
from typing import Set, Optional

from bs4 import BeautifulSoup
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from time import sleep

from rich.spinner import Spinner
from rich.text import Text

from src.constants import TORRENT_BASE_URL
from src.core.cli import console
from src.schemas.movie_schema import Movie
from src.utils.requests import requests

logger = logging.getLogger(__name__)


class SearchEngine:
    def __init__(self):

        self._movie_search_url = TORRENT_BASE_URL + "/sort-category-search/{query}/Movies/seeders/desc/1/"
        self._movie_store = {}
        self._movie_id_store = {}

    @property
    def movies(self) -> list[Movie]:
        return list(self._movie_store.values())

    def get(self, idx: int) -> Optional[Movie]:
        return self._retrieve_movie(movie_id=idx)

    def search(self, query: str) -> list['Movie']:
        movies = set()

        with Live(console=console, transient=True) as live:
            live.update(Spinner(name='dots', text="Fetching movie links...", style='green'))
            urls = self._get_movie_links(query)
            live.update(Text("Movie links fetched successfully!", style='green'))
            sleep(2)

        with Progress(
                TextColumn("{task.description}"),
                SpinnerColumn(),
                BarColumn(complete_style="green"),
                TextColumn("{task.completed}/{task.total}", style="progress.completed"),
                TimeElapsedColumn(),
                console=console,
                transient=True
        ) as progress:
            task = progress.add_task("Processing movies", total=len(urls))
            for url in urls:
                try:
                    movie = self._retrieve_movie(url) or Movie.from_url(url)
                    movies.add(movie)
                except Exception as e:
                    logger.error(f"Error fetching movie from URL {url}: {e}")
                progress.update(task, advance=1)

        for movie in movies:
            self._store_movie(movie)

        return list(movies)

    def _store_movie(self, movie: Movie):
        self._movie_store[movie.url] = movie
        self._movie_id_store[movie.id] = movie

    def _retrieve_movie(self, movie_url: str = None, movie_id: int = None) -> Optional[Movie]:
        if movie_id and movie_url:
            raise ValueError("Both movie_url and movie_id cannot be provided at the same time.")
        if movie_url:
            return self._movie_store.get(movie_url, None)
        if movie_id:
            return self._movie_id_store.get(movie_id, None)
        raise ValueError("Either movie_url or movie_id must be provided.")

    def _get_movie_links(self, query: str) -> Set[str]:
        """
        Fetches direct movie page URLs from the search results.

        :param query: Search query.
        :return: Set of movie page URLs.
        """
        formatted_query = urllib.parse.quote_plus(query)
        search_url = self._movie_search_url.format(query=formatted_query)

        response = requests.fetch_url(search_url)
        if not response:
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