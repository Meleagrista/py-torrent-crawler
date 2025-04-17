import asyncio

from torrentp import TorrentDownloader

from src.constants import TORRENT_DOWNLOAD_PATH
from src.schemas.movie_schema import Movie
from src.search import MovieSearch


def display(movies: list[Movie]):
    if not movies:
        print("No results found.\n")
        return

    for idx, movie in enumerate(movies, start=1):
        print(f"[{idx}] {movie.title}")


def download(movie: Movie):
    torrent_file = TorrentDownloader(movie.torrents[0].magnet_link, str(TORRENT_DOWNLOAD_PATH))
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

        selected_movie = None

        # Ask the user to select a movie
        while not selected_movie:
            try:
                selection = int(input("\nSelect a movie by number to download (or type 0 to cancel): "))
                if selection == 0:
                    print("Cancelled movie download.")
                    exit()
                if 1 <= selection <= len(movies):
                    selected_movie = movies[selection - 1]
                else:
                    print("Invalid selection. Please choose a valid number.")
            except Exception as e:
                print(f"Error: {e}. Please enter a valid number.")

        try:
            download(selected_movie)
        except Exception as e:
            print(f"Error downloading the movie: {e}")
            exit()


if __name__ == "__main__":
    main()