import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class DataType(StrEnum):
    CONVERSATION = "conversation"
    HOCR = "hocr"
    HOCR_NO_OCR = "hocr_no_ocr"
    IMAGE = "image"
    PDF = "pdf"
    TEXT = "text"
    TIME_SERIES = "time_series"
    TRACE = "trace"
