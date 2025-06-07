# Changelog
All notable changes to this project will be documented in this file.

## [unreleased] - 2025-05-05

### Updated
- **2025-05-05**:
  - Update `README.md` with new repository name.
  - Update movie schema output for edge case.

## [v1.0.0] – 2025-05-05

### Added
- **2025-04-20**:
  - Add Docker image for Windows support.
  - Add mechanism to download movies outside the Docker image.
  - Add improved console output appearance.
  - Add improved download progress bar.
  - Add Command Line Interface (CLI).

- **2025-04-21**:
  - Add updated `help` command.

- **2025-04-30**:
  - Add new `summary` and `torrents` commands.
  - Add title field to torrent file schema.

- **2025-05-01**:
  - Add retry mechanism for failed requests while using Selenium.
  - Add persistence system for movie store.
  - Add logger class to manage logging.
  - Add command history feature added to the CLI.
  - Add year field added to movie schema.
  - Add ID field added to torrent schema.
  - Add `search` and `download` commands keyword to filter torrents by language.

- **2025-05-03**:
  - Add `history` command keyword for filtering by title or year.

- **2025-05-05**:
  - Add `README.md` documentation.
  - Add `LICENSE.txt`.

### Updated
- **2025-04-21**:
  - Update terminal output formatting through `rich` library.

- **2025-04-30**:
  - Update movie schema output through `rich` library.

- **2025-05-01**:
  - Update CLI output through `rich` library.
  
### Fixed
- **2025-04-20**:
  - Fix HTML parser to extract titles.
  - Fix Genre enum conversion.

- **2025-04-30**:
  - Fix format errors and removed debugging lines.
  - Fix issues with the `--language` keyword in the `search` command.