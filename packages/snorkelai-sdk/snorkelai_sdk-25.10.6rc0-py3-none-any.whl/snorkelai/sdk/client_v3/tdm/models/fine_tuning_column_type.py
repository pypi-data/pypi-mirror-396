import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class FineTuningColumnType(StrEnum):
    CONTEXT = "context"
    INSTRUCTION = "instruction"
    PROMPT_PREFIX = "prompt_prefix"
    RESPONSE = "response"
