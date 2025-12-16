import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class PromptTemplateOrigin(StrEnum):
    CRITERIA_TEMPLATE = "CRITERIA_TEMPLATE"
    PROMPT_DEVELOPMENT = "PROMPT_DEVELOPMENT"
