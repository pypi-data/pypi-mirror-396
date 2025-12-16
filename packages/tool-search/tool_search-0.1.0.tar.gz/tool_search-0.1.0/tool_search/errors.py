"""Error codes and error response builders for tool_search.

Aligns with Anthropic's official tool_search_tool specification.
See: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool
"""

from typing import Any


class ToolSearchErrorCode:
    """Standard error codes from Anthropic spec."""

    TOO_MANY_REQUESTS = "too_many_requests"
    INVALID_PATTERN = "invalid_pattern"
    PATTERN_TOO_LONG = "pattern_too_long"
    UNAVAILABLE = "unavailable"
    # Custom codes for our implementation
    QUERY_REQUIRED = "query_required"
    NOT_INDEXED = "not_indexed"


# Maximum query length per Anthropic spec
MAX_QUERY_LENGTH = 200


def build_error_response(
    tool_use_id: str,
    error_code: str,
    message: str | None = None,
) -> dict[str, Any]:
    """Build an error response in Anthropic's format.

    Args:
        tool_use_id: The tool_use_id from the request
        error_code: One of ToolSearchErrorCode values
        message: Optional human-readable message

    Returns:
        Error response dict matching Anthropic spec
    """
    content: dict[str, Any] = {
        "type": "tool_search_tool_result_error",
        "error_code": error_code,
    }

    if message:
        content["message"] = message

    return {
        "type": "tool_search_tool_result",
        "tool_use_id": tool_use_id,
        "content": content,
    }


def validate_query(query: str) -> str | None:
    """Validate a search query.

    Args:
        query: The search query string

    Returns:
        Error code if invalid, None if valid
    """
    if not query or not query.strip():
        return ToolSearchErrorCode.QUERY_REQUIRED

    if len(query) > MAX_QUERY_LENGTH:
        return ToolSearchErrorCode.PATTERN_TOO_LONG

    return None
