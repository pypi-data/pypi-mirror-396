from pytest_texts_score.client import get_client
from pytest_texts_score.plugin import get_config
from pytest_texts_score.prompts import (
    get_system_answers_prompt,
    get_system_questions_prompt,
    get_user_answers_prompt,
    get_user_questions_prompt,
)
import pytest
from typing import Any
import json


def make_questions(base_text: str) -> str:
    """
    Generate questions from a given text using the LLM.

    This function sends the ``base_text`` to the configured Azure OpenAI model
    with a system prompt designed to elicit factual yes/no questions. It
    retrieves the global configuration and client instance to make the API call.

    :param base_text: The text from which to generate questions.
    :type base_text: str
    :return: A JSON string containing the generated questions. Returns an empty
             string if the model response content is empty.
    :rtype: str
    :raises openai.APIError: If the API call to the LLM fails.
    """
    config = get_config()
    client = get_client()
    response = client.chat.completions.create(
        model=config._llm_model,
        messages=[
            {
                "role": "system",
                "content": get_system_questions_prompt()
            },
            {
                "role": "user",
                "content": get_user_questions_prompt(base_text)
            },
        ],
        max_tokens=config._llm_max_tokens,
        temperature=0,
    )
    questions_text = response.choices[0].message.content
    return questions_text or ""


def evaluate_questions(answer_text: str,
                       questions_text: str) -> list[dict[str, Any]]:
    """
    Evaluate how well a text answers a list of questions using the LLM.

    This function sends the ``answer_text`` and a JSON string of
    ``questions_text`` to the configured Azure OpenAI model. The model is
    prompted to answer each question based on the text and provide a numeric
    score. The function parses the JSON response and returns the list of
    answers. It also handles and warns about responses that might include
    markdown ```json tags.

    :param answer_text: The text to use for answering the questions.
    :type answer_text: str
    :param questions_text: A JSON string representing the list of questions.
    :type questions_text: str
    :return: A list of dictionaries, where each dictionary contains a
             'question' and its corresponding 'answer' score.
    :rtype: list[dict[str, Any]]
    :raises ValueError: If the LLM response is not valid JSON or cannot be parsed.
    :raises openai.APIError: If the API call to the LLM fails.
    """
    config = get_config()
    client = get_client()
    response = client.chat.completions.create(
        model=config._llm_model,
        messages=[
            {
                "role": "system",
                "content": get_system_answers_prompt()
            },
            {
                "role": "user",
                "content": get_user_answers_prompt(answer_text, questions_text),
            },
        ],
        max_tokens=config._llm_max_tokens,
        temperature=0,
    )
    response_content = response.choices[0].message.content or ""

    # Some models, especially when instructed to return JSON, may wrap the output
    # in markdown code blocks (e.g., ```json ... ```). This block of code
    # robustly handles this by stripping the markers if they exist.
    if "```json" in response_content:
        pytest.warns(
            Exception(
                "Model is producing extra tags! The response will be parsed, but this may indicate model is not following instructions."
            ))
        # remove json tags
        response_content = response_content.split("```json")[1]
        response_content = response_content.split("```")[0]
    answers_list = []
    try:
        parsed = json.loads(response_content.strip())
        # The prompt asks for a specific structure: {"list": [...]}.
        # We safely extract the list, defaulting to an empty list if the key is missing.
        answers_list = parsed.get("list", [])
    except Exception as e:
        raise ValueError(f"Invalid JSON in evaluate_questions response: {e}")
    return answers_list
