import re
from typing import List


def extract_urls(text: str) -> List[str]:
    """
    Extract valid URLs from a given text string.

    Args:
        text (str): Input text containing potential URLs

    Returns:
        List[str]: List of extracted valid URLs

    Example:
        >>> text = "Visit https://example.com and http://github.com"
        >>> extract_urls(text)
        ['https://example.com', 'http://github.com']
    """
    url_pattern = r"""
        https?://                                           # http:// or https://
        (?:                                                 # Domain part
            (?:                                             # Hostname
                (?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+ # Subdomains and domain
                [a-zA-Z]{2,}                                # TLD
            |                                               # OR
                \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}         # IPv4
            )
        )
        (?:                                                 # Path part
            /                                               # Starting slash
            [\w\-.~!$&'()*+,;=:@%/]*                      # Valid URL characters
        )*                                                  # Zero or more path parts
        (?:\?[\w\-.~!$&'()*+,;=:@%/?]*)?                  # Optional query parameters
        (?:\#[\w\-.~!$&'()*+,;=:@%/?]*)?                  # Optional fragment
    """

    return re.findall(url_pattern, text, re.VERBOSE)


def main() -> None:
    # Example usage
    text: str = """
    Here are some example URLs:
    https://www.example.com
    Check out http://github.com/repository
    Visit our docs at https://docs.example.com/guide?version=1.0
    For local development: http://localhost:8080/test
    Some invalid ones: ftp://invalid.com, just.example.com
    """

    urls: List[str] = extract_urls(text)
    for url in urls:
        print(url)


if __name__ == "__main__":
    main()
