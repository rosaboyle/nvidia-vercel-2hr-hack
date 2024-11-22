import asyncio
from pydantic import BaseModel
from typing import List
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from text_2_entity import parse_input, parse_input_async, get_openai_text_response, open_ai_sequence_response, ChatMessageUser, get_openai_text_response_async

# Test models
class UserInfo(BaseModel):
    name: str
    age: int
    interests: List[str]

class TestResponse(BaseModel):
    message: str
    status: str

# Test cases
def test_parse_input():
    system_content = "You are a helpful assistant that provides user information."
    user_content = "Generate information about a random user."
    
    result = parse_input(
        system_content=system_content,
        user_content=user_content,
        response_format=UserInfo,
        model="gpt-4o-2024-08-06"
    )
    
    assert isinstance(result, UserInfo)
    assert isinstance(result.name, str)
    assert isinstance(result.age, int)
    assert isinstance(result.interests, list)

async def test_parse_input_async():
    system_content = "You are a helpful assistant that provides user information."
    user_content = "Generate information about a random user."
    
    result = await parse_input_async(
        system_content=system_content,
        user_content=user_content,
        response_format=UserInfo,
        model="gpt-4o-2024-08-06"
    )
    
    assert isinstance(result, UserInfo)
    assert isinstance(result.name, str)
    assert isinstance(result.age, int)
    assert isinstance(result.interests, list)

def test_get_openai_text_response():
    system_prompt = "You are a helpful assistant."
    user_prompt = "Say hello!"
    
    result = get_openai_text_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model="gpt-4o"
    )
    
    assert isinstance(result, str)
    assert len(result) > 0

def test_open_ai_sequence_response():
    # Test with single message
    single_message = ChatMessageUser(
        content="Hello!",
        role="user"
    )
    
    message_list = [single_message.model_dump()]
    
    result_single = open_ai_sequence_response(
        messages=message_list,
        model="gpt-4o"
    )
    
    assert isinstance(result_single, list)
    assert len(result_single) == 2  # Original message + response
    # assert all(isinstance(msg, ChatMessageUser) for msg in result_single)
    
    # Test with multiple messages
    multiple_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ]
    
    result_multiple = open_ai_sequence_response(
        messages=multiple_messages,
        model="gpt-4o"
    )
    
    assert isinstance(result_multiple, list)
    assert len(result_multiple) == 3  # Original messages + response

async def test_get_openai_text_response_async():
    system_prompt = "You are a helpful assistant."
    user_prompt = "Say hello!"
    
    result = await get_openai_text_response_async(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model="gpt-4o"
    )
    
    assert isinstance(result, str)
    assert len(result) > 0

# Run async tests
if __name__ == "__main__":
    # Run synchronous tests
    test_parse_input()
    test_get_openai_text_response()
    test_open_ai_sequence_response()
    
    # Run async tests
    asyncio.run(test_parse_input_async())
    asyncio.run(test_get_openai_text_response_async())
    
    print("All tests completed successfully!")