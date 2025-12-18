import json
import os
import random
import re
import string
import tempfile
import time
import unicodedata

from hamcrest import (
    assert_that,
    equal_to,
    contains_string,
    greater_than,
    instance_of,
    is_not,
    none,
)

from codemie_sdk import CodeMieClient
from codemie_test_harness.tests import autotest_entity_prefix


class BaseUtils:
    def __init__(self, client: CodeMieClient):
        self.client = client


def get_random_name():
    """Generate a random name with lowercase letters and underscores only, and cannot begin with '_' or '-'."""
    characters = string.ascii_lowercase
    random_string = "".join(random.choice(characters) for _ in range(15))
    # Generate the remaining characters
    random_name = f"{autotest_entity_prefix}{random_string}"
    return random_name


def to_camel_case(input_string):
    # Remove non-letter characters
    cleaned = re.sub(r"[^a-zA-Z]", " ", input_string)
    # Split into words
    words = cleaned.split()
    # Convert to camelCase
    camel_case = words[0].capitalize() + "".join(
        word.capitalize() for word in words[1:]
    )
    return camel_case


def clean_json(json_str):
    try:
        # Attempt to parse the JSON string directly
        return json.loads(json_str)
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract embedded JSON from Markdown-like syntax
        pattern = re.compile(
            r'(\{(?:[^{}"]|"(?:[^"\\]|\\.)*")*\}|\[(?:[^\[\]"]|"(?:[^"\\]|\\.)*")*\])'
        )

        matcher = pattern.search(json_str)

        if matcher:
            unwrapped_json_str = matcher.group(1)
            # Replace non-breaking spaces with regular spaces and remove control characters
            unwrapped_json_str = unwrapped_json_str.replace("\u00a0", " ")
            unwrapped_json_str = "".join(
                c
                for c in unwrapped_json_str
                if not (unicodedata.category(c) == "Cc" and c not in "\r\n\t")
            )
            try:
                return json.loads(unwrapped_json_str)
            except json.JSONDecodeError as inner_exception:
                raise ValueError("Invalid JSON string") from inner_exception
        else:
            raise ValueError("No JSON found in the Markdown string")


def percent_of_relevant_titles(response):
    """
    Calculate the percentage of relevant titles in a response.
    Usage:
        percent = percent_of_relevant_titles(response)
    """
    json_to_parse = clean_json(response)
    search_terms = [
        "ai",
        "artificial intelligence",
        "machine learning",
        "natural language",
    ]
    percent = (
        sum(
            1
            for item in json_to_parse
            if any(term in item.get("title", "").lower() for term in search_terms)
        )
        * 10
    )
    return percent


def wait_for_entity(get_entity_callable, entity_name, timeout=10, poll_interval=3):
    """
    Waits for an entity to be created or available with a timeout.
    :param entity_name: Entity name
    :param get_entity_callable: A callable that attempts to retrieve the entity.
                                Should raise NotFoundError if the entity is not found.
    :param timeout: The maximum time to wait for the entity (in seconds).
    :param poll_interval: The time between consecutive checks (in seconds).
    :return: The entity object if it is successfully retrieved.
    :raises TimeoutError: If the entity is not found within the timeout period.
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        entities = [
            raw
            for raw in get_entity_callable()
            if (hasattr(raw, "name") and entity_name == raw.name)
            or (hasattr(raw, "alias") and entity_name == raw.alias)
            or (hasattr(raw, "prompt") and entity_name == raw.prompt)
        ]

        if len(entities) > 0:
            return entities[0]
        time.sleep(poll_interval)

    # If timeout is reached and entity is not found, raise an error
    raise TimeoutError("Entity was not found within the timeout period.")


def assert_response(response, status_code, message=None):
    assert_that(response.status_code, equal_to(status_code))
    if message:
        error_details = json.loads(response.content)["error"].get("details", "")
        if isinstance(error_details, list):
            assert_that(error_details[0]["msg"], equal_to(message))
        elif error_details:
            assert_that(error_details, equal_to(message))
        else:
            assert_that(
                json.loads(response.content)["error"]["message"], equal_to(message)
            )


def assert_error_details(response, status_code, message):
    assert_that(
        response.status_code, equal_to(status_code), "Status code is not expected."
    )
    error_details = json.loads(response.content)["error"]["details"]
    assert_that(
        error_details, contains_string(message), "Error message is not expected."
    )


def credentials_to_dict(credentials):
    return {cred.key: cred.value for cred in credentials}


def assert_tool_triggered(tool_name, triggered_tools):
    """
    Assert that the expected tool(s) were triggered during assistant interaction.

    Args:
        tool_name: Either a single tool enum or a tuple of tool enums that should be triggered
        triggered_tools: List of tools that were actually triggered

    Raises:
        AssertionError: If any of the expected tools were not found in triggered_tools
                       (for tuples, ALL tools must be present)
    """
    # Handle both single tools and tuples of tools
    if isinstance(tool_name, tuple):
        tools_to_check = tool_name
    else:
        tools_to_check = (tool_name,)

    # Check each expected tool
    found_tools = []
    missing_tools = []

    for tool in tools_to_check:
        tool_value_lower = tool.value.lower()
        tool_value_with_spaces = tool.value.replace("_", " ").lower()

        # Check if this specific tool was triggered
        tool_found = False
        for triggered_tool in triggered_tools:
            if (
                triggered_tool.lower() == tool_value_lower
                or triggered_tool.lower() == tool_value_with_spaces
                or tool_value_with_spaces in triggered_tool.lower()
            ):
                found_tools.append(tool.value)
                tool_found = True
                break

        if not tool_found:
            missing_tools.append(tool.value)

    # Assert that ALL expected tools were found
    if missing_tools:
        expected_tools = [tool.value for tool in tools_to_check]

        if len(tools_to_check) == 1:
            assert False, (
                f"Tool validation failed:\n"
                f"Expected tool '{expected_tools[0]}' to be triggered\n"
                f"But it was not found in triggered tools: {triggered_tools}\n"
            )
        else:
            assert False, (
                f"Tool validation failed:\n"
                f"Expected ALL of these tools to be triggered: {expected_tools}\n"
                f"Missing tools: {missing_tools}\n"
                f"Found tools: {found_tools}\n"
                f"Actually triggered: {triggered_tools}\n"
            )


def extract_file_id_from_response(response):
    """
    Extract file ID from assistant response containing file URLs.

    Args:
        response: The assistant response text containing file URL

    Returns:
        str: The extracted file ID

    Raises:
        AssertionError: If no file URL is found in the response
    """
    file_url_pattern = r"sandbox:/v1/files/([A-Za-z0-9+/=]+)"
    file_url_match = re.search(file_url_pattern, response)

    assert_that(
        file_url_match,
        is_not(none()),
        f"No file URL found in response. Expected pattern 'sandbox:/v1/files/<file_id>' in: {response}",
    )

    return file_url_match.group(1)


def download_and_verify_file(client, file_id):
    """
    Download a file by its ID and verify it was successfully downloaded.

    Args:
        client: CodeMieClient instance
        file_id: The file identifier to download

    Returns:
        bytes: The downloaded file content

    Raises:
        AssertionError: If file download fails or content is invalid
    """
    file_content = client.files.get_file(file_id)

    assert_that(file_content, f"Downloaded file with ID '{file_id}' is empty")
    assert_that(len(file_content), greater_than(0), "Downloaded file has no content")
    assert_that(file_content, instance_of(bytes), "Downloaded content should be bytes")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    try:
        assert_that(os.path.exists(temp_file_path), "Temporary file was not created")
        assert_that(
            os.path.getsize(temp_file_path), greater_than(0), "Temporary file is empty"
        )
        assert_that(
            os.path.getsize(temp_file_path),
            equal_to(len(file_content)),
            "Saved file size does not match downloaded content size",
        )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return file_content
