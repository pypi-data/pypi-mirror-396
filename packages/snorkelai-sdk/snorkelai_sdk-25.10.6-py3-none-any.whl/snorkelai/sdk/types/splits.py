import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class Splits(StrEnum):
    train = "train"
    dev = "dev"
    valid = "valid"
    test = "test"


SCALE_SPLITS = [Splits.dev.value, Splits.test.value, Splits.valid.value]
