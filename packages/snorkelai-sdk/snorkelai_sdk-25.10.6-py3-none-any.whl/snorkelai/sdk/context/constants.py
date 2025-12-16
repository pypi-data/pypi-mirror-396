import re

BASE_URL_ENV_VAR = "SNORKEL_PLATFORM_BASE_URL"
API_KEY_ENV_VAR = "SNORKEL_PLATFORM_API_KEY"
API_KEY_FILE_ENV_VAR = "SNORKEL_PLATFORM_API_KEY_FILE"
DEFAULT_WORKSPACE_NAME = "default"
DEFAULT_WORKSPACE_UID = 1

html_link_re = re.compile(r"""<(a|A)\s+(?:[^>]*?\s+)?(href|HREF)=["'](?P<url>[^"']+)""")
plain_link_re = re.compile(r"""(?P<url>http[s]?://[-a-zA-Z0-9@:%_+.~#?&/=]+)""")
workspace_pattern = re.compile(r"workspace-\d+/")
VENDOR_PRODUCT_NAME = "SnorkelAI_SnorkelPlatform"
BASE_ARTIFACT_CACHE_DIR = "/var/lib/snorkel"
CONTAINER_VOLUME_DATA_PATH_TEST_OVERRIDE_ENV_VAR = (
    "CONTAINER_VOLUME_DATA_PATH_TEST_OVERRIDE"
)
