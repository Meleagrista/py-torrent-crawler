import asyncio

from typing import Optional

from src.constants import TORRENT_DOWNLOAD_PATH
from src.core.cli import CLI, console
from src.core.download import TorrentDownloaderWrapper
from src.core.search import SearchEngine
from src.schemas.movie_schema import Movie

cli = CLI()
search_engine = SearchEngine()

@cli.command(
    "search",
    arguments=[("title", "Title of the movie to search for")],
    help_text="Scrapes the page for the given movie title."
)
def search(movie_title):
    movies = list(search_engine.search(movie_title))

    if not movies:
        console.print("[red]No results found.[/red]")
    else:
        Movie.print_header()
        for movie in movies:
            movie.print_row()

@cli.command(
    "download",
    arguments=[("id", "ID of the movie to download")],
    help_text="Downloads the movie with the given ID."
)
def download(movie_id):
    movie = search_engine.get(int(movie_id))

    if not movie:
        console.print("[red]No movie found with that ID.[/red]")
    else:
        torrent_file = TorrentDownloaderWrapper(movie.torrents[0].magnet_link, str(TORRENT_DOWNLOAD_PATH))
        asyncio.run(torrent_file.start_download())

@cli.command(
    "history",
    keyword_args={
        '-n': ('number', 'Number of movies to display', 'number'),
        '-s': ('sort', 'Sort movies by title', None),
        '--sort': ('sort', 'Sort movies by title', None),
    },
    help_text="Displays the movie search history."
)
def history(number: Optional[int] = None, sort: bool = False):
    if not isinstance(sort, bool):
        console.print("[red]Invalid sort option.[/red]")
        return

    movies = search_engine.movies
    movies.sort(key=lambda x: x.title) if sort else movies
    number = int(number) if number is not None else len(movies)

    if not movies:
        console.print("[red]No results found.[/red]")
    else:
        Movie.print_header()
        for movie in movies[:number]:
            movie.print_row()

if __name__ == "__main__":
    cli.start()