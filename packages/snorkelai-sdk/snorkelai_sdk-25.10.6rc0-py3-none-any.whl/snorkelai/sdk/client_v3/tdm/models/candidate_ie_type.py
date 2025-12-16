import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class CandidateIEType(StrEnum):
    CURRENCY = "Currency"
    CUSTOM_ENTITY = "Custom entity"
    DATE = "Date"
    EMAIL_ADDRESS = "Email address"
