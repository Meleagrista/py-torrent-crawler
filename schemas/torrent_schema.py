import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel

from constants import LANGUAGES
from schemas.date_schema import Date
from schemas.size_schema import Size
from utils.requests import RobustFetcher

logger = logging.getLogger(__name__)


def extract_date(text: str) -> datetime:
    time_pattern = re.compile(r'(\d+)\s*(year|month|week|day|hour|minute)s?\s*ago', re.IGNORECASE)
    match = time_pattern.search(text)

    if match:
        # Extract the value and unit
        value = int(match.group(1))
        unit = match.group(2).lower()

        # Calculate the timedelta
        now = datetime.now()

        if unit == 'year':
            return now - relativedelta(years=value)
        elif unit == 'month':
            return now - relativedelta(months=value)
        elif unit == 'week':
            return now - relativedelta(weeks=value)
        elif unit == 'day':
            return now - relativedelta(days=value)
        elif unit == 'hour':
            return now - relativedelta(hours=value)
        elif unit == 'minute':
            return now - relativedelta(minutes=value)

    # Fallback if no match is found (return the current time if unable to parse)
    return datetime.now()


def extract_size(size_text: str) -> float:
    # Strip any whitespace
    size_text = size_text.strip().lower()

    # Check if the size is in GB, MB, or KB
    if 'gb' in size_text:
        # Extract the number and convert to float
        size = float(size_text.replace('gb', '').strip())
    elif 'mb' in size_text:
        # Convert MB to GB (1 MB = 1/1024 GB)
        size = float(size_text.replace('mb', '').strip()) / 1024
    elif 'kb' in size_text:
        # Convert KB to GB (1 KB = 1/1024/1024 GB)
        size = float(size_text.replace('kb', '').strip()) / (1024 * 1024)
    else:
        # Default to GB if unit is not recognized
        size = float(size_text)

    return size


def get_li_span_text(soup, label: str) -> str | None:
    try:
        return soup.find('strong', string=label).find_next('span').text.strip()
    except AttributeError:
        return None


class Comment(BaseModel):
    user: str
    message: str
    date: Date

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
            # Extract user name
            user_name = detail.find('a', class_='user').text.strip()

            # Extract message
            message = detail.find('p').text.strip()

            # Extract date
            date_text = detail.find('span', {'class': 'flaticon-time'}).find_next('span').text.strip()
            date = Date.from_string(date_text)

            # Create the Comment object
            comment = Comment(user=user_name, message=message, date=date)
            comments.append(comment)

        return comments


class Torrent(BaseModel):
    category: str
    subcategory: str
    language: str
    date: Date
    size: Size
    tags: list[str] = []
    comments: list[Comment] = []
    uploader: str
    downloads: int
    seeders: int
    metadata: dict = {}

    @classmethod
    def from_url(cls, url: str) -> 'Torrent':
        response = RobustFetcher.fetch_url(url)
        if not response:
            raise ValueError("Failed to fetch the URL.")

        soup = BeautifulSoup(response, 'html.parser')

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

        return Torrent(
            category=category,
            subcategory=subcategory,
            language=language,
            date=date,
            size=size,
            tags=tags,
            comments=comments,
            uploader=uploader,
            downloads=downloads,
            seeders=seeders,
            metadata={'url': url}
        )
