import hashlib
import logging

from typing import List, Dict, Any
from pydantic import field_validator, Field, BaseModel, HttpUrl
from rich.table import Table
from rich.text import Text

from src.core.cli import console
from src.schemas.movie_schema import DASH_HEAD

logger = logging.getLogger(__name__)

class Object(BaseModel):
    id: int = Field(..., description="The unique identifier of this instance.")
    url: HttpUrl = Field(..., description="Origin URL of this instance.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata of this instance.")

    @staticmethod
    def generate_id(title: str, url: str) -> int:
        title = title.strip().lower()
        url = url.strip().lower()

        unique_str = f"{title}|{url}"
        hash_digest = hashlib.sha256(unique_str.encode('utf-8')).hexdigest()

        # Remove letters and get digits only
        numeric_id = int(re.sub(r'\D', '', hash_digest)) % (10 ** 10)
        return numeric_id

def get_li_span_text(soup, label: str) -> str | None:
    try:
        return soup.find('strong', string=label).find_next('span').text.strip()
    except AttributeError:
        return None


import re

from enum import Enum
from pydantic import BaseModel


class DateUnit(str, Enum):
    YEAR = "year"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"

    @classmethod
    def from_string(cls, string: str) -> 'DateUnit':
        unit = string.lower().strip()
        if unit.endswith('s'):
            unit = unit[:-1]
        try:
            return cls(unit)
        except ValueError:
            raise ValueError(f"Invalid date unit: '{unit}'")

    def __str__(self):
        return self.value.lower()


class Date(BaseModel):
    value: int
    unit: DateUnit

    @classmethod
    def from_string(cls, string: str) -> 'Date':
        if "decade" in string:
            match = re.search(r"(\d+)\s*decade", string)
            if match:
                value = int(match.group(1)) * 10
                return cls(value=value, unit=DateUnit.YEAR)
            else:
                raise ValueError(f"Could not parse the decade format: '{string}'")

        match = re.search(r"(\d+)\s*(year|month|week|day|hour|minute)s?\s*(ago)?", string, re.IGNORECASE)

        if not match:
            raise ValueError(f"Could not parse the date from string: '{string}'")

        value = int(match.group(1))
        unit = DateUnit.from_string(match.group(2))

        return cls(value=value, unit=unit)

    def __str__(self):
        return f"{self.value} {str(self.unit)}{'' if self.value > 1 else 's'} ago"


class SizeUnit(str, Enum):
    GB = "GB"
    MB = "MB"
    KB = "KB"

    @classmethod
    def from_string(cls, string: str) -> 'SizeUnit':
        unit = string.strip().upper()
        if unit.endswith('S'):
            unit = unit[:-1]
        try:
            return cls(unit)
        except ValueError:
            raise ValueError(f"Invalid size unit: '{unit}'")

    def __str__(self):
        return self.value.upper()


class Size(BaseModel):
    value: float
    unit: SizeUnit

    @classmethod
    def from_string(cls, string: str) -> 'Size':
        match = re.search(r"(\d+(?:\.\d+)?)\s*(GB|MB|KB)s?", string, re.IGNORECASE)

        if not match:
            raise ValueError(f"Could not parse the size from string: '{string}'")

        value = float(match.group(1))
        unit = SizeUnit.from_string(match.group(2))

        return cls(value=value, unit=unit)

    def __str__(self):
        return f"{self.value:.2f} {str(self.unit)}"


from bs4 import BeautifulSoup


class Comment(BaseModel):
    user: str = Field(..., description="The username of the person who posted the comment.")
    message: str = Field(..., description="The content of the comment.")
    date: Date = Field(..., description="The date and time when the comment was posted.")

    @classmethod
    def from_html(cls, html: str | BeautifulSoup) -> list['Comment']:
        if isinstance(html, str):
            soup = BeautifulSoup(html, 'html.parser')
        else:
            soup = html

        comments = []
        comments_section = soup.find('div', {'role': 'tabpanel', 'id': 'comments'})
        comment_details = comments_section.find_all('div', class_='comment-detail')

        for detail in comment_details:
            user_name = detail.find('a', class_='user').text.strip()
            message = detail.find('p').text.strip()
            date_text = detail.find('span', {'class': 'flaticon-time'}).find_next('span').text.strip()
            date = Date.from_string(date_text)
            comment = Comment(user=user_name, message=message, date=date)
            comments.append(comment)

        return comments


from urllib.parse import urlparse

from src.constants import TORRENT_SUPPORTED_LANGUAGES
from src.utils.requests import requests

class Torrent(Object):
    id: int = Field(..., description="The unique identifier for the torrent.")
    title: str = Field(..., description="The title of the torrent.")
    category: str = Field(..., description="The category of the torrent.")
    language: str = Field(..., description="The language of the torrent content.")
    date: Date = Field(..., description="The date when the torrent was uploaded")
    size: Size = Field(..., description="The size of the torrent files")
    comments: List[Comment] = Field(default_factory=list, description="A list of comments for the torrent")
    seeders: int = Field(..., description="The number of seeders for this torrent")
    magnet_link: str = Field(..., description="The magnet link for the torrent")
    torrent_links: List[str] = Field(default_factory=list, description="List of torrent file links")

    @classmethod
    @field_validator('magnet_link', mode='after')
    def validate_magnet_link(cls, v):
        magnet_regex = r'^magnet:\?xt=urn:btih:[a-fA-F0-9]{40,64}.*'
        if not re.match(magnet_regex, v):
            raise ValueError(f"Invalid magnet link: {v}")
        return v

    @classmethod
    @field_validator('torrent_links', mode='after')
    def validate_torrent_links(cls, v):
        if not v:
            raise ValueError("No .torrent links provided.")
        for link in v:
            parsed = urlparse(link)
            if parsed.scheme not in ('http', 'https'):
                raise ValueError(f"Invalid torrent link (bad scheme): {link}")
            if not parsed.path.endswith('.torrent') and 'torrent' not in parsed.path:
                raise ValueError(f"Invalid torrent link format: {link}")
        return v

    @classmethod
    def from_url(cls, url: str) -> 'Torrent':
        response = requests.fetch_url(url)
        if not response:
            raise ValueError("Failed to fetch the URL.")

        soup = BeautifulSoup(response, 'html.parser')

        title_tag = soup.find('div', class_='box-info-heading').find('h1')
        title = title_tag.get_text(strip=True) if title_tag else None

        language = get_li_span_text(soup, 'Language')
        if language not in TORRENT_SUPPORTED_LANGUAGES:
            logger.warning(f"Language '{language}' not supported.")
            return None

        category = get_li_span_text(soup, 'Category')
        subcategory = get_li_span_text(soup, 'Type')
        date_text = get_li_span_text(soup, 'Date uploaded')
        date = Date.from_string(date_text) if date_text else None
        size_text = get_li_span_text(soup, 'Total size')
        size = Size.from_string(size_text) if size_text else None

        try:
            tags = [li.find('a').text for li in soup.find('ul', class_='category-name').find_all('li')]
        except AttributeError:
            tags = []

        comments = Comment.from_html(soup)
        uploader = get_li_span_text(soup, 'Uploaded By')
        downloads_text = get_li_span_text(soup, 'Downloads')
        downloads = int(downloads_text.replace(',', '')) if downloads_text else 0
        seeders_text = get_li_span_text(soup, 'Seeders')
        seeders = int(seeders_text.replace(',', '')) if seeders_text else 0
        magnet_link_tag = next((a for a in soup.find_all('a', href=True) if 'Magnet Download' in a.get_text(strip=True)), None)
        magnet_link = magnet_link_tag['href'] if magnet_link_tag else None
        dropdown = soup.find('ul', class_='dropdown-menu')
        torrent_links = []
        if dropdown:
            for a_tag in dropdown.find_all('a', href=True):
                href = a_tag['href']
                if href.endswith('.torrent') or 'torrent.php?' in href or 'btcache.me' in href:
                    torrent_links.append(href)

        if not magnet_link or not torrent_links:
            raise ValueError("No magnet link or torrent file links found.")

        return Torrent(
            id=Object.generate_id(title, url),
            title=title,
            url=url,
            metadata={'downloads': downloads, 'uploader': uploader, 'tags': tags, 'type': subcategory},
            category=category,
            language=language,
            date=date,
            size=size,
            comments=comments,
            seeders=seeders,
            magnet_link=magnet_link,
            torrent_links=torrent_links
        )

    @classmethod
    def print_details(cls, torrents):
        table = Table(
            header_style=None,
            box=DASH_HEAD,
            expand=True,
            width=console.width,
            padding=(0, 2),
            pad_edge=False,
            show_edge=False,
        )

        table.add_column("ID", min_width=8)
        table.add_column("Title")
        table.add_column("Seeders", justify="right")
        table.add_column("Size", justify="right")
        table.add_column("Language")
        table.add_column("Date", justify="right")

        for torrent in torrents:
            table = torrent.add_row(table)

        console.print(table)

    def add_row(self, table: Table) -> Table:
        id_content = Text(str(self.id).strip())
        title_content = Text(self.title)
        seeders_content = Text(str(self.seeders))
        size_content = Text(str(self.size))
        language_content = Text(self.language)
        date_content = Text(str(self.date))

        table.add_row(id_content, title_content, seeders_content, size_content, language_content, date_content)

        return table