import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class Splits(StrEnum):
    DEV = "dev"
    TEST = "test"
    TRAIN = "train"
    VALID = "valid"
