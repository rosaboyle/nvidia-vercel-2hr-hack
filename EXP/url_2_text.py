# File: EXP/url_to_text.py

from typing import Optional, Dict
from bs4thingy import extract_text_from_html
from extractor_api import fetch_webpage
import dotenv

dotenv.load_dotenv()

def url_to_text(
    url: str,
    scraper_api_key: Optional[str] = None,
    custom_headers: Optional[Dict[str, str]] = None,
    use_proxy: bool = True,
    timeout: int = 30
) -> str:
    """
    Convert a webpage URL directly to cleaned text content.
    
    Args:
        url (str): The URL of the webpage to extract text from
        scraper_api_key (Optional[str]): ScraperAPI key. If None, uses default from fetch_webpage
        custom_headers (Optional[Dict[str, str]]): Custom headers for the request
        use_proxy (bool): Whether to use ScraperAPI proxy
        timeout (int): Request timeout in seconds
        
    Returns:
        str: Cleaned text content from the webpage
        
    Raises:
        ScrapingError: If fetching the webpage fails
        Exception: If text extraction fails
    """
    try:
        # Fetch HTML content
        html_content = fetch_webpage(
            target_url=url,
            custom_headers=custom_headers,
            proxy=use_proxy,
            timeout=timeout
        )
        
        # Extract and clean text
        text_content = extract_text_from_html(html_content)
        
        return text_content
        
    except Exception as e:
        raise Exception(f"Failed to process URL {url}: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Example URLs to test
    test_urls = [
        "https://www.epa.gov/chemicals-under-tsca/\
epa-finalizes-solvent-14-dioxane-tsca-risk-evaluation",
    ]
    
    for url in test_urls:
        try:
            print(f"\nProcessing {url}...")
            print("-" * 50)
            text = url_to_text(
                url=url,
                custom_headers={"Accept-Language": "en-US,en;q=0.9"},
                use_proxy=True  # Set to False for direct requests
            )
            print(text)
            # print(f"Extracted text:\n{text[:500]}...")  # Print first 500 chars
            # print("-" * 50)
        except Exception as e:
            print(f"Error processing {url}: {e}")