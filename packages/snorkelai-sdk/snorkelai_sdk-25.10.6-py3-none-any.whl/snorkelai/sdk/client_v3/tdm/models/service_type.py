import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class ServiceType(StrEnum):
    AUTHORIZATION_API = "authorization-api"
    DB = "db"
    ENGINE = "engine"
    ENGINE_TINY = "engine-tiny"
    ENVOY_FRONT_PROXY = "envoy-front-proxy"
    FLIPPER_SERVER = "flipper-server"
    FLIPPER_WORKER = "flipper-worker"
    GRAFANA = "grafana"
    INFLUXDB = "influxdb"
    JUPYTERHUB = "jupyterhub"
    JUPYTERHUB_PROXY = "jupyterhub-proxy"
    NOTEBOOK = "notebook"
    PLATFORM_UI = "platform-ui"
    PROMPT_API = "prompt-api"
    RAY_HEAD = "ray-head"
    RAY_WORKER = "ray-worker"
    REDIS = "redis"
    STORAGE_API = "storage-api"
    TDM_API = "tdm-api"
    TELEGRAF = "telegraf"
