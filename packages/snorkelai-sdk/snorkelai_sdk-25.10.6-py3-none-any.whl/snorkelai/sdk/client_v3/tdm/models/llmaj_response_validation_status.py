import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class LLMAJResponseValidationStatus(StrEnum):
    EMPTY_RESPONSE = "empty_response"
    INFERENCE_FAILURE = "inference_failure"
    INVALID_JSON = "invalid_json"
    INVALID_SCORE = "invalid_score"
    MISSING_RATIONALE = "missing_rationale"
    MISSING_SCORE = "missing_score"
    SUCCESS = "success"
    UNKNOWN_ERROR = "unknown_error"
