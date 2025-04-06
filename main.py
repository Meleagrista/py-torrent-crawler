import asyncio

from torrentp import TorrentDownloader

from constants import TORRENT_DOWNLOAD_PATH
from schemas.movie_schema import Movie
from search import MovieSearch


def display(movies: list[Movie]):
    if not movies:
        print("No results found.\n")
        return

    for idx, movie in enumerate(movies, start=1):
        print(f"[{idx}] {movie.title}")


def download(movie: Movie):
    torrent_file = TorrentDownloader(movie.torrents[0].magnet_link, TORRENT_DOWNLOAD_PATH)
    asyncio.run(torrent_file.start_download())


def main():
    search_engine = MovieSearch()

    while True:
        query = input("Enter a movie name to search (or type 'exit' to quit): ")

        if query.lower() == 'exit':
            print("Goodbye!")
            break

        movies = list(search_engine.search(query))

        display(movies)

        # Ask the user to select a movie
        try:
            selection = int(input("\nSelect a movie by number to download (or type 0 to cancel): "))
            if selection == 0:
                print("Cancelled movie download.")
                continue
            if 1 <= selection <= len(movies):
                selected_movie = movies[selection - 1]
                download(selected_movie)
            else:
                print("Invalid selection. Please choose a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

        print()


if __name__ == "__main__":
    main()