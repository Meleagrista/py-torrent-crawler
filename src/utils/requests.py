import logging
import requests as py_requests
import urllib3

from src.constants import CHROME_BINARY

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

ERROR_INDICATORS = [
        "bad search request",
        "bad category",
        "access denied",
        "error 403",
        "you don't have permission",
        "page not found",
        "not available",
        "invalid request",
        "no results found"
    ]

class RobustFetcher:

    def __init__(self):
        self.session = py_requests.Session()

        # Read from env or use fallback path
        chrome_binary = CHROME_BINARY

        options = Options()
        options.binary_location = chrome_binary
        options.page_load_strategy = 'eager'
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")  # This is the critical one

        # Setup ChromeDriver
        service = Service(ChromeDriverManager(driver_version="135.0.7049.84").install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(4)

    def fetch_url(self, url):
        logger.debug(f"Fetching URL: {url}")
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            logger.debug("Fetched successfully with requests.")
            return str(response.text)
        except Exception as e:
            # TODO: Find the exact Exception type.
            logger.warning(f"Requests failed for {url}. Falling back to Selenium.")
            try:
                self.driver.get(url)
                logger.debug("Fetched successfully with Selenium.")
                # TODO: Add a check for the HTML content to ensure it's loaded.
                return str(self.driver.page_source)
            except Exception as se:
                logger.error(f"Selenium also failed for {url}: {se}")
                return None

requests = RobustFetcher()