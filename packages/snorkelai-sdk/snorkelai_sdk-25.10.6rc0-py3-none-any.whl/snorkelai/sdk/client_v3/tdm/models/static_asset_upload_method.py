import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class StaticAssetUploadMethod(StrEnum):
    LOCAL = "local"
    REMOTE_GCS = "remote_gcs"
    REMOTE_S3 = "remote_s3"
