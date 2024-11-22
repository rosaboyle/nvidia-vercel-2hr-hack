import os
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# current file directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
# import url_to_tex
from url_2_text import url_to_text  # noqa: E402

# import prompts
from prompts import prompt_to_extract_toxins  # noqa: E402
from text_2_entity import parse_input  # noqa: E402
from pydantic_models import ToxinList, ToxinListResponse  # noqa: E402
from extract_urls import extract_urls  # noqa: E402

app = FastAPI(
    title="Toxin Parser API",
    description="API for extracting toxin information from URLs and text content",
    version="1.0.0",
)


class TextInput(BaseModel):
    """Request model for text input"""

    text: str


class UrlInput(BaseModel):
    """Request model for URL input"""

    url: HttpUrl


class TextUrlResponse(BaseModel):
    """Response model for text and URLs"""

    urls: List[HttpUrl]
    text: str


@app.post("/extract/urls", response_model=ToxinListResponse)
async def combined_url_and_text(input_data: TextInput) -> ToxinListResponse:
    """
    Extract URLs from a given text.
    """
    urls = extract_urls(input_data.text)
    original_text = input_data.text
    all_toxins: list[ToxinList.Toxin] = []
    for url in urls:
        original_text = original_text.replace(url, "")
        text = url_to_text(url)
        toxins = extract_toxins(text)
        all_toxins.extend(toxins.toxins)

    if original_text:
        toxins_from_original_text = extract_toxins(original_text)
        all_toxins.extend(toxins_from_original_text.toxins)

    return ToxinListResponse(toxins=all_toxins, urls=urls)


@app.post("/parse/url", response_model=ToxinListResponse)
async def parse_from_url(input_data: UrlInput) -> ToxinListResponse:
    """
    Parse toxin information from a given URL.

    Args:
        input_data (UrlInput): Input containing the URL to process

    Returns:
        ToxinListResponse: Extracted toxin information and source URL

    Raises:
        HTTPException: If URL processing or parsing fails
    """
    try:
        # Convert URL to text
        text = url_to_text(str(input_data.url))

        # Extract toxins from text
        toxins_result = extract_toxins(text)

        return ToxinListResponse(
            toxins=toxins_result.toxins, urls=[str(input_data.url)]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")


@app.post("/parse/text", response_model=ToxinList)
async def parse_from_text(input_data: TextInput) -> ToxinList:
    """
    Parse toxin information from provided text.

    Args:
        input_data (TextInput): Input containing the text to process

    Returns:
        ToxinList: Extracted toxin information

    Raises:
        HTTPException: If text parsing fails
    """
    try:
        return extract_toxins(input_data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")


def extract_toxins(text: str) -> ToxinList:
    """
    Extract toxin information from text using the parsing model.

    Args:
        text (str): Input text to process

    Returns:
        ToxinList: Extracted toxin information
    """
    return parse_input(
        system_content=prompt_to_extract_toxins,
        user_content=text,
        response_format=ToxinList,
        model="gpt-4o",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
    print("Server is running on port 8000")
