import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class DatasetViewTypes(StrEnum):
    RANKING_LLM_RESPONSES_VIEW = "ranking_llm_responses_view"
    SINGLE_LLM_RESPONSE_VIEW = "single_llm_response_view"
