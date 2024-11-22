import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# current file directory
current_dir = os.path.dirname(os.path.abspath(__file__))

from prompts import prompt_to_extract_toxins
from text_2_entity import parse_input
from pydantic_models import ToxinList

def extract_toxins(text: str) -> ToxinList:
    return parse_input(
        system_content=prompt_to_extract_toxins,
        user_content=text,
        response_format=ToxinList,
        model="gpt-4o-2024-08-06"
    )

if __name__ == "__main__":
    print(extract_toxins(""))

