"""Helper utilities for structured output with Pydantic models."""

import json
import re
import uuid
from typing import Any, Dict, Type
from textwrap import dedent

from pydantic import BaseModel, ValidationError


def create_schema_system_message(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Create a system message that instructs the LLM to return structured output.

    Args:
        model: The Pydantic model class to generate schema from

    Returns:
        Dictionary representing a system message for in_memory_messages

    Example:
        ```python
        from pydantic import BaseModel

        class UserInfo(BaseModel):
            name: str
            age: int

        message = create_schema_system_message(UserInfo)
        # Use in in_memory_messages parameter
        ```
    """
    schema = model.model_json_schema()

    message_content = dedent(f"""As a genius expert, your task is to understand the content and provide the parsed objects in json that match the following json_schema:

    {json.dumps(schema, indent=2, ensure_ascii=False)}

    Make sure to return an instance of the JSON, not the schema itself""")

    return {
        "id": str(uuid.uuid4()),
        "message": message_content,
        "role": "system",
        "toolRequests": [],
        "toolResponses": [],
    }


def remove_start_md_json(response_msg: str) -> str:
    """
    Checks the message for the listed start patterns and removes them if present.

    Args:
        response_msg: The response message to check.

    Returns:
        The response message without the start marker (if one was present).
    """
    start_pattern = re.compile(
        r"^(```json\n|`json\n|```\n|`\n|```json|`json|```|`|json|json\n)"
    )
    match = start_pattern.match(response_msg)
    if match:
        response_msg = response_msg[match.end() :]

    return response_msg


def remove_end_md_json(response_msg: str) -> str:
    """
    Checks the message for the listed end patterns and removes them if present.

    Args:
        response_msg: The response message to check.

    Returns:
        The response message without the end marker (if one was present).
    """
    end_pattern = re.compile(r"(\n```|\n`|```|`)$")
    match = end_pattern.search(response_msg)
    if match:
        response_msg = response_msg[: match.start()]

    return response_msg


def extract_json_from_string(response_msg: str) -> str:
    """
    Attempts to extract JSON (object or array) from within a larger string, not specific to markdown.

    Args:
        response_msg: The response message to check.

    Returns:
        The extracted JSON string if found, otherwise the original string.
    """
    json_pattern = re.compile(r"\{.*\}|\[.*\]", re.DOTALL)
    match = json_pattern.search(response_msg)
    if match:
        return match.group(0)

    return response_msg


def remove_markdown_json(response_msg: str) -> str:
    """
    Checks if the response message is in JSON format and removes Markdown formatting if present.

    Args:
        response_msg: The response message to check.

    Returns:
        The response message without Markdown formatting if present, or an error message.
    """
    response_msg = remove_start_md_json(response_msg)
    response_msg = remove_end_md_json(response_msg)

    # Validate if the remaining response message is valid JSON. If it's still not valid
    # after removing the markdown notation, try to extract JSON from within the string.
    try:
        json.loads(response_msg)
        return response_msg
    except json.JSONDecodeError:
        response_msg = extract_json_from_string(response_msg)
        try:
            json.loads(response_msg)
            return response_msg
        except json.JSONDecodeError:
            return f"Invalid JSON response: {response_msg}"


def parse_response_to_model(response_text: str, model: Type[BaseModel]) -> BaseModel:
    """
    Parse a response string to a Pydantic model instance.

    This function cleans markdown formatting from JSON responses and validates
    the parsed data against the provided Pydantic model.

    Args:
        response_text: The raw response text from the LLM
        model: The Pydantic model class to parse into

    Returns:
        An instance of the Pydantic model

    Raises:
        ValidationError: If the response doesn't match the model schema
        ValueError: If the response is not valid JSON

    Example:
        ```python
        from pydantic import BaseModel

        class UserInfo(BaseModel):
            name: str
            age: int

        response = '```json\\n{"name": "John", "age": 30}\\n```'
        user = parse_response_to_model(response, UserInfo)
        print(user.name)  # "John"
        ```
    """
    # Clean markdown formatting
    cleaned_json = remove_markdown_json(response_text)

    # Check for error message
    if cleaned_json.startswith("Invalid JSON response:"):
        raise ValueError(cleaned_json)

    # Parse JSON
    try:
        data = json.loads(cleaned_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}") from e

    # Validate against Pydantic model
    try:
        return model.model_validate(data)
    except ValidationError as e:
        raise ValidationError(f"Response does not match schema: {e}") from e
