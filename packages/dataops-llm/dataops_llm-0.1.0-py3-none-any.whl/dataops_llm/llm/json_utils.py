"""JSON repair utilities for LLM responses."""

import json
import re
from typing import Optional


class JSONRepairError(Exception):
    """Raised when JSON cannot be repaired."""
    pass


def clean_json_response(raw_response: str) -> str:
    """Clean common JSON formatting issues from LLM responses.

    Handles:
    - Markdown code fences (```json ... ```)
    - Leading/trailing whitespace
    - Common truncation issues

    Args:
        raw_response: Raw LLM response

    Returns:
        Cleaned JSON string

    Raises:
        JSONRepairError: If JSON cannot be cleaned
    """
    # Strip markdown code fences
    cleaned = re.sub(r'```(?:json)?\s*(.*?)\s*```', r'\1', raw_response, flags=re.DOTALL)

    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()

    # Try to parse - if it works, we're done
    try:
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError as e:
        # Attempt basic repairs for truncation
        cleaned = _attempt_completion(cleaned)

        # Try again
        try:
            json.loads(cleaned)
            return cleaned
        except json.JSONDecodeError:
            raise JSONRepairError(
                f"Could not repair JSON. Error: {e}. "
                f"Content preview: {cleaned[:200]}..."
            )


def _attempt_completion(json_str: str) -> str:
    """Try to complete truncated JSON by closing braces/brackets.

    Args:
        json_str: Potentially truncated JSON string

    Returns:
        JSON string with missing closures added
    """
    # Count unclosed braces and brackets
    open_braces = json_str.count('{') - json_str.count('}')
    open_brackets = json_str.count('[') - json_str.count(']')

    # Add missing closures
    completed = json_str

    # If odd number of quotes, close the string
    if json_str.count('"') % 2 != 0:
        completed += '"'

    # Close braces
    completed += '}' * max(0, open_braces)

    # Close brackets
    completed += ']' * max(0, open_brackets)

    return completed
