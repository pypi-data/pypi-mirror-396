import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class WorkspaceScopedFeature(StrEnum):
    CUSTOM_METRICS = "custom_metrics"
    CUSTOM_OPERATORS = "custom_operators"
    EXTERNAL_LLMS = "external_llms"
    FINETUNING = "finetuning"
