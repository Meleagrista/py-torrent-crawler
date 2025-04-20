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

from src.core.search import MovieSearch
from src.core.cli import CLI

cli = CLI()
search_engine = MovieSearch()

@cli.command("search", arguments=["movie"], help_text="Scrapes the page for the given movie name.")
def search(movie):
    movies = list(search_engine.search(movie))

    if not movies:
        print("No results found.")
        return

    # Define column widths
    id_width = 12
    title_width = 50
    rating_width = 6
    genres_width = 40
    torrents_width = 8
    poster_width = 65

    Movie.print_header(
        id_width=id_width,
        title_width=title_width,
        rating_width=rating_width,
        genres_width=genres_width,
        torrents_width=torrents_width,
        poster_width=poster_width
    )

    for movie in movies:
        movie.print_row(
            id_width=id_width,
            title_width=title_width,
            rating_width=rating_width,
            genres_width=genres_width,
            torrents_width=torrents_width,
            poster_width=poster_width
        )

if __name__ == "__main__":
    cli.start()