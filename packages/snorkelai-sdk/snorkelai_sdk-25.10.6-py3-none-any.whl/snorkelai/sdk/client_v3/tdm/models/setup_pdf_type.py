import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class SetupPDFType(StrEnum):
    NATIVE_PDF = "Native PDF"
    SCANNED_PDF_NEED_TO_RUN_OCR = "Scanned PDF, need to run OCR"
    SCANNED_PDF_NO_NEED_TO_RUN_OCR = "Scanned PDF, no need to run OCR"
