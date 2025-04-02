from search import MovieSearch


# Function to display movies
def display_movies(movies):
    """Displays the search results."""
    if not movies:
        print("No results found.\n")
        return

    for idx, movie in enumerate(movies, start=1):
        print(f"[{idx}] {movie.title}")


# Main function
def main():
    movie_search = MovieSearch()

    while True:
        query = input("Enter a movie name to search (or type 'exit' to quit): ")

        if query.lower() == 'exit':
            print("Goodbye!")
            break

        movies = movie_search.search(query)

        display_movies(list(movies))
        print()


if __name__ == "__main__":
    main()
