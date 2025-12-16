import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class AssetUploadType(StrEnum):
    ARROW = "arrow"
    ARROW_IPC = "arrow_ipc"
    CSV = "csv"
    DOC = "doc"
    DOCX = "docx"
    IMAGE = "image"
    JSON = "json"
    JSONP = "jsonp"
    JSONX = "jsonx"
    MP3 = "mp3"
    MP4 = "mp4"
    PARQUET = "parquet"
    PDF = "pdf"
    PPT = "ppt"
    PPTX = "pptx"
    WAV = "wav"
    XLS = "xls"
    XLSX = "xlsx"
