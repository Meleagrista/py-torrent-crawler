import json
import logging
import time
import urllib.parse
from typing import Set, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from time import sleep

from rich.spinner import Spinner
from rich.text import Text

from src.constants import TORRENT_BASE_URL, MOVIE_STORE_FILE
from src.core.cli import console
from src.schemas.movie_schema import Movie
from src.utils.requests import requests

logger = logging.getLogger(__name__)


class SearchEngine:
    def __init__(self):
        self._movie_search_url = TORRENT_BASE_URL + "/sort-category-search/{query}/Movies/seeders/desc/1/"

        self._movie_store = {}
        self._movie_id_store = {}

        self._torrent_id_store = {}

        self._load_movies()

    @property
    def movies(self) -> list[Movie]:
        return list(self._movie_store.values())

    def get(self, idx: int, from_torrents: bool = False) -> Optional[Movie]:
        if from_torrents:
            return self._torrent_id_store.get(idx, None)
        else:
            return self._movie_id_store.get(idx, None)

    # noinspection PyUnresolvedReferences
    def search(self, query: str, force: bool = False, language: str = None, torrents: int = None) -> list['Movie']:
        movies = set()

        with Live(console=console, transient=True) as live:
            live.update(Spinner(name='dots', text="Fetching movie links...", style='green'))
            urls = self._get_movie_links(query)
            live.update(Text("Movie links fetched successfully!", style='green'))
            sleep(2)

        with (Progress(
                TextColumn("{task.description}"),
                SpinnerColumn(),
                BarColumn(complete_style="green"),
                TextColumn("{task.completed}/{task.total}", style="progress.completed"),
                TimeElapsedColumn(),
                console=console,
                transient=True
        ) as progress):
            task = progress.add_task("Processing", total=len(urls))
            for url in urls:
                try:
                    stored_movie: Movie = self._movie_store.get(url, None)

                    if stored_movie and not force:
                        movie = stored_movie
                    else:
                        movie = Movie.from_url(url, language=language, torrents=torrents)
                        movie.id = stored_movie.id if stored_movie else movie.id

                    if movie:
                        movies.add(movie)
                    else:
                        logger.warning(f"Movie skipped for `{url}`")
                except Exception as e:
                    logger.error(f"Error fetching movie from URL {url}: {e}")
                progress.update(task, advance=1)

        self._store_movies(list(movies))

        return list(movies)

    def _load_movies(self):
        if not MOVIE_STORE_FILE.exists():
            logger.warning(f"Movie store file {MOVIE_STORE_FILE} does not exist. Creating a new one.")
            with MOVIE_STORE_FILE.open("w", encoding="utf-8") as f:
                json.dump([], f)

        with MOVIE_STORE_FILE.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                movies = [Movie.model_validate(movie_data) for movie_data in data]
                self._store_movies(movies, save=False)
            except (json.JSONDecodeError, ValidationError) as e:
                logger.error(f"Failed to load movie store: {e}")

        for movie in self._movie_store.values():
            for torrent in movie.torrents:
                if torrent.id in self._torrent_id_store:
                    logger.warning(f"Duplicate torrent ID for movies {movie.title} and {self._torrent_id_store[torrent.id]}.")
                else:
                    self._torrent_id_store[torrent.id] = torrent

    def _save_movies(self):
        if not MOVIE_STORE_FILE.exists():
            logger.error(f"Movie store file {MOVIE_STORE_FILE} cannot be found.")
            with MOVIE_STORE_FILE.open("w", encoding="utf-8") as f:
                json.dump([], f)

        with MOVIE_STORE_FILE.open("w", encoding="utf-8") as f:
            json.dump([m.model_dump(mode="json") for m in self._movie_store.values()], f, indent=2)

    def _store_movies(self, movies: list[Movie], save: bool = True):
        for movie in movies:
            self._movie_store[str(movie.url)] = movie
            self._movie_id_store[movie.id] = movie

        if save:
            self._save_movies()

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