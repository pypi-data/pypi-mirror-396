import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class ResourceType(StrEnum):
    APPLICATION = "application"
    DATASET = "dataset"
    DATA_CONNECTOR = "data_connector"
    DATA_CONNECTOR_CONFIG_AMAZON_S3 = "data_connector_config_amazon_s3"
    DATA_CONNECTOR_CONFIG_DATABRICKS_SQL = "data_connector_config_databricks_sql"
    DATA_CONNECTOR_CONFIG_GOOGLE_BIGQUERY = "data_connector_config_google_bigquery"
    DATA_CONNECTOR_CONFIG_GOOGLE_CLOUD_STORAGE = (
        "data_connector_config_google_cloud_storage"
    )
    DATA_CONNECTOR_CONFIG_SNORKEL_INTERNAL_STORAGE = (
        "data_connector_config_snorkel_internal_storage"
    )
    DATA_CONNECTOR_CONFIG_SNOWFLAKE = "data_connector_config_snowflake"
    DATA_CONNECTOR_CONFIG_SQLDB = "data_connector_config_sqldb"
    LOGS = "logs"
    NODE = "node"
    STATIC_ASSET_UPLOAD_METHOD = "static_asset_upload_method"
    SYSTEM_SCOPED_FEATURE = "system_scoped_feature"
    WORKSPACE_SCOPED_FEATURE = "workspace_scoped_feature"
