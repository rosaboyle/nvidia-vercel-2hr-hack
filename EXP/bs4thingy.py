from bs4 import BeautifulSoup, Comment  # type: ignore
from typing import List
import re


def extract_text_from_html(html_content: str) -> str:
    """
    Extract clean text content from HTML while handling various edge cases.

    Args:
        html_content (str): Raw HTML content

    Returns:
        str: Cleaned text content with preserved formatting
    """
    # Create BeautifulSoup object with 'lxml' parser (or 'html.parser' as fallback)
    try:
        soup: BeautifulSoup = BeautifulSoup(html_content, "lxml")
    except Exception as e:
        print(f"Error creating BeautifulSoup object: {e}")
        soup = BeautifulSoup(html_content, "html.parser")

    # Remove scripts, styles, and comments
    for element in soup(["script", "style", "head", "[document]"]):
        element.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Get text while preserving some structure
    lines: List[str] = []
    for element in soup.descendants:
        # Handle text nodes
        if isinstance(element, str) and not isinstance(element, Comment):
            text: str = element.strip()
            if text:
                # Replace multiple spaces with single space
                text = re.sub(r"\s+", " ", text)
                lines.append(text)

        # Add line breaks for block-level elements
        elif element.name in [
            "br",
            "p",
            "div",
            "li",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        ]:
            if lines and lines[-1] != "\n":
                lines.append("\n")

    # Join lines and clean up extra whitespace
    text = " ".join(lines)

    # Clean up whitespace
    text = re.sub(
        r"\n\s*\n", "\n\n", text
    )  # Convert multiple newlines to double newlines
    text = re.sub(r" +", " ", text)  # Remove multiple spaces
    text = text.strip()  # Remove leading/trailing whitespace

    return text


# Example usage:
if __name__ == "__main__":
    sample_html: str = """
    <html>
        <head>
            <title>Sample Page</title>
            <style>
                body { color: black; }
            </style>
        </head>
        <body>
            <h1>Main Title</h1>
            <div>
                <p>First paragraph with <strong>bold</strong> text.</p>
                <p>Second paragraph with <a href="#">link</a>.</p>
                <script>console.log('test');</script>
                <!-- Comment that should be removed -->
            </div>
        </body>
    </html>
    """

    print(extract_text_from_html(sample_html))
