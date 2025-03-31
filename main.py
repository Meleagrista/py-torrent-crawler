import urllib.parse
import requests

from bs4 import BeautifulSoup


def search_movies(query):
    # Format the query to be used in the URL (encode spaces as %20)
    query = urllib.parse.quote_plus(query)

    # Initialize variables
    page_number = 1
    movie_titles = []

    while True:
        # Construct the URL to search for movies
        url = f"https://1337x.to/sort-category-search/{query}/Movies/seeders/desc/{page_number}/"

        # Make a GET request to fetch the page content
        response = requests.get(url)
        if response.status_code != 200:
            print("Error fetching the webpage.")
            return []

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if "Bad search request" exists in the HTML (indicating no results)
        if "Bad search request" in soup.text or "Bad Category" in soup.text:
            print("No more results or invalid search.")
            break

        # Find all <a> elements that contain movie links
        movie_links = soup.find_all('a', href=True)

        # Extract movie names from the links
        for link in movie_links:
            # Check if the link contains a movie URL pattern
            if "/torrent/" in link['href']:
                movie_titles.append(link.get_text())

            # Stop if we have reached 10 movies
            if len(movie_titles) >= 10:
                print("Found 10 movies, stopping the search.")
                break

        # If 10 movies have been found, break the loop
        if len(movie_titles) >= 10:
            break

        # Increment the page number to search the next page
        page_number += 1

    # Return the list of movie titles
    return movie_titles


def display_results(results):
    """Displays the search results."""
    for idx, movie in enumerate(results, start=1):
        print(f"{idx}. {movie}")


def main():
    while True:
        # Prompt user for a search query
        query = input("Enter a movie name to search (or type 'exit' to quit): ")

        # Allow user to exit the program
        if query.lower() == 'exit':
            print("Goodbye!")
            break

        print(f"\nSearching for movies: {query}\n")
        results = search_movies(query)  # Implement this function

        if results:
            display_results(results)
        else:
            print("No results found.\n")


if __name__ == "__main__":
    main()
