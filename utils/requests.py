import logging
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
logger.propagate = False


class RobustFetcher:
    # Pre-initialize session
    session = requests.Session()

    # Set up Selenium options
    options = Options()
    options.page_load_strategy = 'eager'
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")

    # Initialize Selenium driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(2)

    @classmethod
    def fetch_url(cls, url):
        logger.debug(f"Fetching URL: {url}")
        try:
            response = cls.session.get(url, timeout=10)
            response.raise_for_status()
            logger.debug("Fetched successfully with requests.")
            return str(response.text)
        except Exception as e:
            logger.warning(f"Requests failed for {url}: {e}. Falling back to Selenium.")
            try:
                cls.driver.get(url)
                logger.debug("Fetched successfully with Selenium.")
                return str(cls.driver.page_source)
            except Exception as se:
                logger.error(f"Selenium also failed for {url}: {se}")
                return None
