import logging
import re

from typing import List
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from pydantic import BaseModel, field_validator, Field

from src.constants import LANGUAGES
from src.schemas.date_schema import Date
from src.schemas.page_schema import Page
from src.schemas.size_schema import Size
from src.utils.requests import fecther

logger = logging.getLogger(__name__)


def get_li_span_text(soup, label: str) -> str | None:
    try:
        return soup.find('strong', string=label).find_next('span').text.strip()
    except AttributeError:
        return None


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


class Torrent(Page):
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
        response = fecther.fetch_url(url)
        if not response:
            raise ValueError("Failed to fetch the URL.")

        soup = BeautifulSoup(response, 'html.parser')

        # Extract language, category, subcategory, etc.
        language = get_li_span_text(soup, 'Language')
        if language not in LANGUAGES:
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
