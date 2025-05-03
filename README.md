# py-ev01-api
Dedicated space for codebase and documentation of my personal project - an API wrapper for ev01 streaming service.

## Roadmap
- [X] Add Docker image for Windows usage.
- [X] Add mechanism to download movie outside image.
- [X] Update search function to be more user-friendly (add a loading bar).
- [X] Update console output appearance.
- [X] Update download bar.
- [X] Update GUI controls to a command line interface.
- [X] Add new GUI commands.

### 2025-04-20
- [X] Add a retry mechanism for failed requests.
- [X] Update HTML parser to extract title from different container.
- [X] Update Genre enum for better readability.

### 2025-04-21
- [X] Update `help` command to show more information.
- [X] Add a command history feature.
- [X] Update CLI to use `rich` library.

### 2025-04-27
- [X] Update movie data, parse year from name.
- [X] Make a simple persistence system for the searched movies.

### 2025-04-31
- [X] Add a command to load more torrent files (choose number or language).
- [X] Add a keyword to load torrent files from a specific language with `/search`.
- [X] Add a keyword to use history with queries or years.

### Future improvements
- [ ] Add the files data available in the torrent file to find if the movie has subtitles.