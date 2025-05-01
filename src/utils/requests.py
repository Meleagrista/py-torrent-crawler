import logging
import time

import requests as py_requests
import urllib3

from src.constants import CHROME_BINARY, SELENIUM_LOAD_STRATEGY

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
        options.page_load_strategy = SELENIUM_LOAD_STRATEGY
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

    def fetch_url(self, url, max_retries=3, backoff_factor=3):
        logger.debug(f"Fetching URL: {url}")

        # First try using requests
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            logger.debug("Fetched successfully with requests.")
            return str(response.text)
        except Exception as e:
            logger.debug(f"Requests failed because of a {e.__class__.__name__} exception: {e}")
            logger.warning(f"Requests failed for {url}. Falling back to Selenium.")

            # Retry loop for Selenium
            for attempt in range(max_retries):
                try:
                    self.driver.get(url)

                    page_source = self.driver.page_source

                    # Common error message patterns
                    error_indicators = [
                        "access denied"
                    ]

                    if any(error.lower() in page_source.lower() for error in error_indicators):
                        logger.warning(f"Selenium fetched the page, but it may have been blocked or denied")
                        raise Exception("Page blocked or denied")

                    if page_source:
                        logger.debug("Selenium fetch returned a non-empty page source.")
                        return str(page_source)
                except Exception as se:
                    logger.debug(f"Selenium requests failed because of a {e.__class__.__name__} exception")
                    logger.debug(f"Selenium attempt {attempt + 1} failed: {se}")
                    if attempt < max_retries - 1:
                        sleep_time = backoff_factor ** attempt
                        logger.debug(f"Retrying after {sleep_time} seconds...")
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"Selenium failed after {max_retries} attempts for {url}: {se}")
                        return None

requests = RobustFetcher()