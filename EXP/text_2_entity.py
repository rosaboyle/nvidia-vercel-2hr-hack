# Parser function
from pydantic import BaseModel

from openai import OpenAI, AsyncOpenAI
import os
from typing import Type, TypeVar

import sys
# Define a generic type variable
T = TypeVar("T", bound=BaseModel)

OPENAI_KEY = os.environ["OPENAI_API_KEY"]

def parse_input(
    system_content: str,
    user_content: str,
    response_format: Type[T],
    model: str = "gpt-4o-2024-08-06",
    client: OpenAI | None = None,
) -> T:
    """
    Generates a response from OpenAI based on the given inputs and model.

    Args:
        model (str): The OpenAI model to use for the completion.
        system_content (str): Content for the system role.
        user_content (str): Content for the user query.
        response_format (Type[T]): The class type of the response
          format (a Pydantic model).

    Returns:
        T: Parsed response from the completion in the type specified by response_format.
    """
    if client is None:
        client = OpenAI(api_key=OPENAI_KEY)

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        response_format=response_format,
    )

    if completion.choices[0].message.parsed is None:
        raise ValueError("Failed to parse response.")

    return completion.choices[0].message.parsed


async def parse_input_async(
    system_content: str,
    user_content: str,
    response_format: Type[T],
    model: str = "gpt-4o-2024-08-06",
    async_client: AsyncOpenAI | None = None,
) -> T:
    """
    Generates a response from OpenAI based on the given inputs and model.

    Args:
        model (str): The OpenAI model to use for the completion.
        system_content (str): Content for the system role.
        user_content (str): Content for the user query.
        response_format (Type[T]): The class type of the
          response format (a Pydantic model).

    Returns:
        T: Parsed response from the completion in the type specified by response_format.
    """
    if async_client is None:
        async_client = AsyncOpenAI(api_key=OPENAI_KEY)

    completion = await async_client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        response_format=response_format,
    )

    if completion.choices[0].message.parsed is None:
        raise ValueError("Failed to parse response.")

    return completion.choices[0].message.parsed


def get_openai_text_response(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o",
    client: OpenAI | None = None,
) -> str:
    """
    Generates a text response using OpenAI's chat completions API.

    Args:
        system_prompt (str): The system prompt for the conversation.
        user_prompt (str): The user prompt for the conversation.
        model (str, optional): The model to use for generating the response.
        Defaults to "gpt-4o".
        client (OpenAI | None, optional): The OpenAI client instance.
        If None, a new client will be created. Defaults to None.

    Returns:
        str: The generated text response.

    Raises:
        ValueError: If the response fails to generate.
    """

    if client is None:
        client = OpenAI(api_key=OPENAI_KEY)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    if not response.choices[0].message.content:
        raise ValueError("Failed to generate response.")

    return response.choices[0].message.content


from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionFunctionMessageParam,
)

from typing import Iterable


class ChatMessageUser(BaseModel):
    content: str
    """The contents of the user message."""

    role: str
    """The role of the messages author, in this case `user`."""


def open_ai_sequence_response(
    messages: (
        ChatMessageUser
        | Iterable[
            ChatCompletionSystemMessageParam
            | ChatCompletionUserMessageParam
            | ChatCompletionAssistantMessageParam
        ]
    ),
    model: str = "gpt-4o",
    client: OpenAI | None = None,
) -> list[ChatMessageUser]:
    """
    Generates a text response using OpenAI's chat completions API.

    Args:
        system_prompt (str): The system prompt for the conversation.
        user_prompt (str): The user prompt for the conversation.
        model (str, optional): The model to use for generating the response.
        Defaults to "gpt-4o".
        client (OpenAI | None, optional): The OpenAI client instance.
        If None, a new client will be created. Defaults to None.

    Returns:
        str: The generated text response.

    Raises:
        ValueError: If the response fails to generate.
    """

    if client is None:
        client = OpenAI()

    response = client.chat.completions.create(model=model, messages=messages)

    if not response.choices[0].message.content:
        raise ValueError("Failed to generate response.")

    return [
        *messages,
        ChatMessageUser(content=response.choices[0].message.content, role="assistant"),
    ]


async def get_openai_text_response_async(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o",
    async_client: AsyncOpenAI | None = None,
) -> str:
    """
    Retrieves a text response from the OpenAI chat model asynchronously.

    Args:
        system_prompt (str): The system prompt for the chat model.
        user_prompt (str): The user prompt for the chat model.
        model (str, optional): The name of the chat model to use. Defaults to "gpt-4o".
        async_client (AsyncOpenAI | None, optional): The async client for OpenAI.
            Defaults to None.

    Returns:
        str: The generated text response from the chat model.

    Raises:
        ValueError: If the response fails to generate.
    """
    if async_client is None:
        async_client = AsyncOpenAI()
    response = await async_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    if not response.choices[0].message.content:
        raise ValueError("Failed to generate response.")

    return response.choices[0].message.content
