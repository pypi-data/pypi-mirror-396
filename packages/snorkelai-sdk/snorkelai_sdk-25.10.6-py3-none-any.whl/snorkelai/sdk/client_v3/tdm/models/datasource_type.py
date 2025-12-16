import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class DatasourceType(StrEnum):
    AMAZON_S3 = "amazon_s3"
    AZURE = "azure"
    DATABRICKS = "databricks"
    GOOGLE_BIG_QUERY = "google_big_query"
    GOOGLE_CLOUD_STORAGE = "google_cloud_storage"
    LOCAL_FILE = "local_file"
    PUBLIC_URL = "public_url"
    SNORKEL_DATA = "snorkel_data"
    SNOWFLAKE = "snowflake"
    SQL_DB = "sql_db"
