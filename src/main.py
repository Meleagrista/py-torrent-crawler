from src.utils.logger import setup_logging
setup_logging()

import asyncio

from typing import Optional, Literal

from src.constants import TORRENT_DOWNLOAD_PATH, TORRENT_SUPPORTED_LANGUAGES
from src.core.cli import CLI, console
from src.core.download import TorrentDownloaderWrapper
from src.core.search import SearchEngine
from src.schemas.movie_schema import Movie

cli = CLI()
search_engine = SearchEngine()

def get_movie_or_warn(movie_id: int):
    movie = search_engine.get(movie_id)
    if not movie:
        console.print("[red]No movie found with that ID.[/red]")
        return None
    return movie

@cli.command(
    "search",
    arguments=[("title", "Title of the movie to search for")],
    keyword_args={
        '--refresh':  ('refresh',  'Overwrite stored movies if possible',            None     ),
        '-l':         ('language', 'Language to search in the torrent files',       'text'    ),
        '--language': ('language', 'Language to search in the torrent files',       'text'    ),
        '-n':         ('files',    'Minimum number of torrents to explore',         'number'  ),
        '--files':    ('files',    'Minimum number of torrents files to explore',   'number'  ),
        },
    help_text="Scrapes the page for the given movie title."
)
def search(movie_title: str, refresh: bool = False, language: str = None, files: int = None):
    if not isinstance(refresh, bool):
        console.print("[red]Invalid option.[/red]")
        return

    if language and language.capitalize() not in TORRENT_SUPPORTED_LANGUAGES:
        console.print("[red]Invalid language option.[/red] The supported languages are: {}".format(", ".join(TORRENT_SUPPORTED_LANGUAGES)))
        return

    if files and not isinstance(files, int):
        files = int(files)
        if files < 0:
            console.print("[red]Invalid number of files.[/red] Must be a positive number.")
            return

    movies = search_engine.search(movie_title, force=refresh, language=language, torrents=files)
    if not movies:
        console.print("[red]No results found.[/red]")
    else:
        Movie.print_details(movies)

@cli.command(
    "download",
    arguments=[("id", "ID of the movie to download")],
    keyword_args={'--torrent': ('torrent', 'Use a torrent ID instead', None)},
    help_text="Downloads the movie with the given ID."
)
def download(idx: int, torrent: bool = False):
    if not isinstance(torrent, bool):
        console.print("[red]Invalid option.[/red]")
        return

    magnet_link = None
    if not torrent:
        movie = get_movie_or_warn(int(idx))
        if movie:
            magnet_link = movie.torrents[0].magnet_link
    else:
        torrent = search_engine.get(int(idx), from_torrents=True)
        if not torrent:
            console.print("[red]No torrent found with that ID.[/red]")
        else:
            magnet_link = torrent.magnet_link

    if magnet_link:
        downloader = TorrentDownloaderWrapper(magnet_link, str(TORRENT_DOWNLOAD_PATH))
        asyncio.run(downloader.start_download())

@cli.command(
    "summary",
    arguments=[("id", "ID of the movie to showcase")],
    help_text="Prints the summary of the movie with the given ID."
)
def summary(movie_id):
    movie = get_movie_or_warn(int(movie_id))
    if movie:
        movie.print_summary()

@cli.command(
    "torrents",
    arguments=[("id", "ID of the movie to showcase its torrent files")],
    help_text="List the torrent files of the movie with the given ID."
)
def torrents(movie_id):
    movie = get_movie_or_warn(int(movie_id))
    if movie:
        movie.print_torrents()

@cli.command(
    "history",
    keyword_args={
        '-n':       ('number',  'Number of movies to display',                          'number'    ),
        '-s':       ('sort',    'Sort movies by attribute (title, year or rating).',    'option'    ),
        '--sort':   ('sort',    'Sort movies by attribute (title, year or rating).',    'option'    ),
        '-t':       ('title',   'Filter movies by title',                               'text'      ),
        '--title':  ('title',   'Filter movies by title',                               'text'      ),
    },
    help_text="Displays the movie search history."
)
def history(
    number: int = 10,
    sort: Literal['title', 'year', 'rating'] = None,
    title: Optional[str] = None
):
    if sort and sort not in ['title', 'year', 'rating']:
        console.print("[red]Invalid sort option.[/red] The supported options are: [green]title[/green], [green]year[/green], [green]rating[/green].")
        return

    if isinstance(number, int):
        number = int(number)

    if number < 0:
        console.print("[red]Invalid number of movies.[/red] Must be a positive number.")
        return

    movies = search_engine.movies

    # Filter by search text
    if title:
        title_lower = title.lower()
        movies = [movie for movie in movies if title_lower in movie.title.lower()]

    # Apply sorting
    if sort == 'year':
        movies.sort(key=lambda x: x.year, reverse=True)
    elif sort == 'rating':
        movies.sort(key=lambda x: x.rating, reverse=True)
    elif sort == 'title':
        movies.sort(key=lambda x: x.title)

    # Adjust number
    if number > len(movies):
        number = len(movies)

    if not movies:
        console.print("[red]No results found.[/red]")
    else:
        Movie.print_details(movies[:number])

if __name__ == "__main__":
    cli.start()