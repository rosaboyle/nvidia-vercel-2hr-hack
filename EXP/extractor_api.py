from typing import Optional, Dict
import requests  # type: ignore
from requests.adapters import HTTPAdapter  # type: ignore
from requests.packages.urllib3.util.retry import Retry  # type: ignore
import logging
from urllib.parse import quote_plus
import os

SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")


class ScrapingError(Exception):
    """Custom exception for scraping errors"""

    pass


def fetch_webpage(
    target_url: str,
    scraper_api_key: str | None = SCRAPER_API_KEY,
    timeout: int = 30,
    proxy: bool = True,
    retry_attempts: int = 3,
    custom_headers: Optional[Dict[str, str]] = None,
) -> str:
    """
    Fetch webpage content using ScraperAPI as a proxy service.

    Args:
        target_url (str): The URL to scrape
        scraper_api_key (str): Your ScraperAPI key
        timeout (int): Request timeout in seconds
        proxy (bool): Whether to use ScraperAPI proxy (if False, makes direct request)
        retry_attempts (int): Number of retry attempts for failed requests
        custom_headers (Optional[Dict[str, str]]): Custom headers to send with the request

    Returns:
        str: HTML content of the webpage

    Raises:
        ScrapingError: If the scraping fails after all retries
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Setup retry strategy
    retry_strategy = Retry(
        total=retry_attempts,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    # Create session with retry strategy
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Default headers
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Combine custom headers with default headers
    headers = {**default_headers, **(custom_headers or {})}

    try:
        if proxy:
            # Use ScraperAPI
            encoded_url = quote_plus(target_url)
            scraper_url = (
                f"http://api.scraperapi.com?api_key={scraper_api_key}&url={encoded_url}"
            )
            logger.info(f"Making request through ScraperAPI to: {target_url}")
            response = session.get(scraper_url, timeout=timeout, headers=headers)
        else:
            # Direct request without proxy
            logger.info(f"Making direct request to: {target_url}")
            response = session.get(target_url, timeout=timeout, headers=headers)

        # Raise an exception for bad status codes
        response.raise_for_status()
        if isinstance(response.text, bytes):
            return response.text.decode("utf-8")
        if not isinstance(response.text, str):
            raise ScrapingError(f"Unexpected response type: {type(response.text)}")
        return response.text

    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to fetch {target_url}: {str(e)}"
        logger.error(error_msg)
        raise ScrapingError(error_msg) from e


# Example usage
if __name__ == "__main__":
    # Example 1: Using ScraperAPI proxy
    try:
        html_content = fetch_webpage(
            target_url="http://httpbin.org/ip",
            custom_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        print("Content with proxy:", html_content)
    except ScrapingError as e:
        print(f"Scraping failed: {e}")

    # Example 2: Direct request without proxy
    try:
        html_content = fetch_webpage(target_url="http://httpbin.org/ip", proxy=False)
        print("\nContent without proxy:", html_content)
    except ScrapingError as e:
        print(f"Scraping failed: {e}")
