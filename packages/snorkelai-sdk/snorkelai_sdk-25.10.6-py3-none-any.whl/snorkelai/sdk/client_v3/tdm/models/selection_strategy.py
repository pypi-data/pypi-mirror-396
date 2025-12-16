import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class SelectionStrategy(StrEnum):
    MODEL_CONFIDENCE = "model_confidence"
    MODEL_ENTROPY = "model_entropy"
    RANDOM = "random"
