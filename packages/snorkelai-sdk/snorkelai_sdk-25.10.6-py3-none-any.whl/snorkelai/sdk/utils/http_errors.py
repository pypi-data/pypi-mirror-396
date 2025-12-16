from typing import List, TypedDict, Union

from requests.exceptions import HTTPError


class ValidationError(TypedDict):
    loc: List[Union[str, int]]
    msg: str
    type: str


def _parse_validation_errors(details: List[ValidationError]) -> str:
    messages = [entry["msg"] for entry in details if "msg" in entry]
    return "; ".join(messages) if messages else ""


def parse_http_error_detail(
    error: HTTPError, default_detail: str = "Server error occurred"
) -> str:
    if error.response is None:
        return default_detail

    try:
        payload = error.response.json()
    except (ValueError, AttributeError):
        return default_detail

    if not isinstance(payload, dict):
        return default_detail

    detail = payload.get("detail")

    if isinstance(detail, str) and detail:
        return detail

    if isinstance(detail, list):
        parsed = _parse_validation_errors(detail)
        if parsed:
            return parsed

    return default_detail
