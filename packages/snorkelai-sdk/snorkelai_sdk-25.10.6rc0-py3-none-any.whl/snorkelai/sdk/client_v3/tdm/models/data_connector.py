import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class DataConnector(StrEnum):
    AMAZONS3 = "AmazonS3"
    CLOUDSTORAGE = "CloudStorage"
    DATABRICKSSQL = "DatabricksSQL"
    FILEUPLOAD = "FileUpload"
    GOOGLEBIGQUERY = "GoogleBigQuery"
    GOOGLECLOUDSTORAGE = "GoogleCloudStorage"
    SNORKELINTERNALSTORAGE = "SnorkelInternalStorage"
    SNOWFLAKE = "Snowflake"
    SQLDB = "SQLDB"
