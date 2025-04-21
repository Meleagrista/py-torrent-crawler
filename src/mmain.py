import logging
import os

from src.schemas.movie_schema import Movie


class TruncateFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', max_length=500):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.max_length = max_length

    def format(self, record):
        msg = super().format(record)
        if len(msg) > self.max_length:
            msg = msg[:self.max_length - 3] + "..."
        return msg

script_name = os.path.basename(__file__)

handler = logging.StreamHandler()
handler.setFormatter(TruncateFormatter(
    fmt=f"[%(levelname)s] <{script_name}> %(message)s", max_length=200
))

logging.basicConfig(
    level=logging.CRITICAL,
    handlers=[handler]
)

from src.core.search import SearchEngine
from src.core.cli import CLI, console

cli = CLI()
search_engine = SearchEngine()

@cli.command(
    "search",
    arguments=[("title", "Title of the movie to search for")],
    help_text="Scrapes the page for the given movie title."
)
def search(movie):
    movies = list(search_engine.search(movie))

    if not movies:
        console.print("[red]No results found.[/red]")
    else:
        Movie.print_header()
        for movie in movies:
            movie.print_row()

@cli.command(
    "history",
    help_text="Displays the movie search history."
)
def history():
    movies = search_engine.movies

    if not movies:
        console.print("[yellow]No movies found.[/yellow]")
    else:
        Movie.print_header()
        for movie in movies:
            movie.print_row()

if __name__ == "__main__":
    cli.start()