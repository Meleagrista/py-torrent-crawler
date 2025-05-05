<div align="center">
  <!--suppress CheckImageSize -->
  <img src=".assets/logo-02.png" alt="logo" width="200" height="auto" />
  <h1>Torrent Crawler</h1>
  <p>
    Streamlined torrent search and download for movies.
  </p>
  <p>
    <a href="https://github.com/Meleagrista/py-torrent-crawler/graphs/contributors">
      <img src="https://img.shields.io/github/contributors/Meleagrista/py-torrent-crawler" alt="contributors" />
    </a>
    <a href="">
      <img src="https://img.shields.io/github/last-commit/Meleagrista/py-torrent-crawler" alt="last update" />
    </a>
    <a href="https://github.com/Meleagrista/py-torrent-crawler/stargazers">
      <img src="https://img.shields.io/github/stars/Meleagrista/py-torrent-crawler" alt="stars" />
    </a>
    <a href="https://github.com/Meleagrista/py-torrent-crawler/network/members">
      <img src="https://img.shields.io/github/forks/Meleagrista/py-torrent-crawler" alt="forks" />
    </a>
    <a href="https://github.com/Meleagrista/py-torrent-crawler/issues/">
      <img src="https://img.shields.io/github/issues/Meleagrista/py-torrent-crawler" alt="open issues" />
    </a>
    <a href="https://github.com/Meleagrista/py-torrent-crawler/blob/master/LICENSE.txt">
      <img src="https://img.shields.io/github/license/Meleagrista/py-torrent-crawler" alt="license" />
    </a>
  </p>

  <h4>
    <a href="https://github.com/Meleagrista/py-torrent-crawler/blob/master/CHANGELOG.md">View changes</a>
    <span> · </span>
    <a href="https://github.com/Meleagrista/py-torrent-crawler/issues/">Request feature</a>
  </h4>
</div>


# Table of Contents
- [About the Project](#about-the-project)
  - [Build With](#build-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
    - [Docker](#docker)
    - [Make](#make)
    - [Poetry (Optional)](#poetry-optional)
  - [Installation](#installation)
- [Usage](#usage)
  - [Environment Variables](#environment-variables)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
  - [Contributors](#contributors)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

# About the Project
This project is a command-line search engine and crawler designed to automate searching for torrent files on 1337x.to. It lets you quickly find torrents for movies, TV shows, and other content by simply providing a search title, saving you time browsing unreliable streaming websites.

## Build With
[![Python][Python-badge]][Python-url]
[![Docker][Docker-badge]][Docker-url]
[![Poetry][Poetry-badge]][Poetry-url]

# Getting Started
Follow these steps to set up and run the project locally.

## Prerequisites
Before running this project, ensure you have the following tools installed:

### Docker
Docker is required to run the project in a containerized environment. It enables compatibility across platforms, including Windows.

- **On Ubuntu**, install Docker with the following commands:
  ```bash
  sudo apt update
  sudo apt install -y ca-certificates curl gnupg
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt update
  sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  ```
- **On Windows**, download and install Docker Desktop from the [official Docker website](https://www.docker.com/products/docker-desktop).

### Make
Make is used to simplify command execution through the provided `Makefile`. You can also run the commands manually if preferred.

- **On Linux**, install Make with:  
  ```bash
  sudo apt update
  sudo apt install -y make
  ```
- **On Windows**, you can use [GnuWin](http://gnuwin32.sourceforge.net/packages/make.htm), or run Make through [WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/).

### Poetry (Optional)
Poetry is used for dependency management if you choose to run the program locally outside of Docker. This is supported on **Linux systems only**.
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```
After installation, ensure Poetry is added to your `PATH`:
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```

> [!NOTE] 
> Poetry is not required when using Docker, as all dependencies are already included in the image.

## Installation
Follow these steps to set up the project on your local machine.

1. Clone the project.
  ```bash
  git clone https://github.com/Meleagrista/py-torrent-crawler.git
  ```
2. Go to the project directory.
  ```bash
  cd py-torrent-crawler
  ```
3. Make sure **Docker** is installed and the daemon is active.
4. Build the project using **Make**.
  ```bash
  make build
  ```

# Usage
To run the project using the **Docker** image, use the following command:
  ```bash
  make run
  ```
You can modify the parameters `DOWNLOAD_DIR` and `CACHE_DIR` in the `Makefile` to set the download and cache directories, respectively to your desired locations.
You can also change them at runtime by running the command with the following parameters:
  ```bash
  make run DOWNLOAD_DIR=/path/to/download CACHE_DIR=/path/to/cache
  ```

## Environment Variables
You can customize the behavior of the program by setting the following environment variables:

- **`TORRENT_FILES_PER_MOVIE`**  Specifies the default number of torrent files to download per movie.
- **`TORRENT_SUPPORTED_LANGUAGES`** Defines the languages that are supported for torrent file downloads.
- **`SELENIUM_LOAD_STRATEGY`** Configures the loading strategy for **Selenium**, which is only relevant if the source website is blocked on your network.  
  - The recommended option is `normal` or you can choose `eager` for faster loading times with increased risk of errors.
- **`TERMINAL_WIDTH`**  Sets the width of the terminal output. Adjust this value to match your terminal size for optimal display.

# Roadmap
- [ ] Add screenshots and a demo to documentation.
- [ ] Add subtitle search by extracting metadata from torrent files.
- [ ] Add alternative torrent sites for scrapping.
- [ ] Improve search functionality to support other media types.
  - [ ] Add support for TV shows and series.

# Contributing
If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Any contributions you make are **greatly appreciated**.

1. Fork the project
2. Create your feature branch.
  ```bash
  git checkout -b feature/AmazingFeature
  ``` 
3. Commit your changes.
  ```bash
  git commit -m 'Add some AmazingFeature'
  ``` 
4. Push to the branch.
  ```bash
  git push origin feature/AmazingFeature
  ``` 
5. Open a pull request

## Contributors
<a href="https://github.com/Meleagrista/py-torrent-crawler/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Meleagrista/py-torrent-crawler" alt="contrib.rocks image" />
</a>

# License
This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE.txt](./LICENSE.txt) file for full license details.

# Contact
Feel free to reach out if you have any questions or feedback.

Martín do Río Rico - [mdoriorico@gmail.com](mailto:mdoriorico@gmail.com)

# Acknowledgements
Special thanks to the following projects and resources that inspired or supported this project:

- [TorrentP](https://github.com/iw4p/torrentp) – A lightweight torrent download tool that served as inspiration.
- [libtorrent](https://www.libtorrent.org) – The powerful BitTorrent library.
- [Awesome Readme Template](https://github.com/Louis3797/awesome-readme-template) – A great starting point for crafting high-quality README files.
- [Best-README-Template](https://github.com/othneildrew/Best-README-Template) – Another excellent template resource for project documentation.
- [Shields.io](https://shields.io/) – For providing useful badges to enhance the README.
- [Choose an Open Source License](https://choosealicense.com/) - For helping to select the right license for this project.

[Python-badge]: https://img.shields.io/badge/python-%233776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org

[Docker-badge]: https://img.shields.io/badge/docker-%232496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com

[Poetry-badge]: https://img.shields.io/badge/poetry-%2360A5FA?style=for-the-badge&logo=poetry&logoColor=white
[Poetry-url]: https://python-poetry.org