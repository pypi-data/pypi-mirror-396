"""Module-specific configuration classes for rc_cli."""

from __future__ import annotations

import os
import tempfile

from rc_cli.common_lib.config_base import BaseConfig


class DownloadConfig(BaseConfig):
    """Configuration for download operations."""

    HOME_DIR = os.path.expanduser("~")
    FILE_DIR = os.path.join(HOME_DIR, "Downloads", "BrandApp")

    BASE_URL = os.environ.get(
        "DOWNLOAD_BASE_URL",
        "http://cloud.example.com/remote.php/dav/files/user/apps",
    )

    AUTH_USERNAME = os.environ.get("RC_DOWNLOAD_USERNAME", "mThor_cloud")
    AUTH_PASSWORD = os.environ.get("RC_DOWNLOAD_PASSWORD", "NextCloud123")

    TIMEOUT_TOTAL = 600.0
    TIMEOUT_CONNECT = 60.0

    CHUNK_SIZE = 8192
    MAX_CONCURRENT_DOWNLOADS = 5
    PROGRESS_UPDATE_INTERVAL = 0.1

    SUFFIX = "coverage"

    @classmethod
    def get_app_types(cls) -> dict:
        """Get APP_TYPES with company name from environment."""
        company_name = os.environ.get("COMPANY_NAME", "company").lower()
        return {
            "aqa": [
                f"web-aqa-xmn-{company_name}-inhouse-debug.apk",
                "WEB-AQA-XMN-Glip-Inhouse.ipa",
                "WEB-AQA-XMN-Glip.zip",
            ],
            "up": [
                f"xmn-up-{company_name}-inhouse-debug.apk",
                "XMN-UP-Glip-Inhouse.ipa",
                "XMN-UP-Glip.zip",
            ],
            "df": [
                f"web-aqa-xmn-{company_name}-inhouse-debug-23.4.10.1.apk",
                "WEB-AQA-XMN-Glip-23.4.10.1-Inhouse.ipa",
                "WEB-AQA-XMN-Glip-23.4.10.1.zip",
                f"xmn-up-{company_name}-inhouse-debug-23.4.10.1.apk",
                "XMN-UP-Glip-23.4.10.1-Inhouse.ipa",
                "XMN-UP-Glip-23.4.10.1.zip",
            ],
        }

    APP_TYPES = property(lambda self: self.get_app_types())


class SPConfig(BaseConfig):
    """Configuration for Service Parameter operations."""

    GITLAB_BASE_URL = os.environ.get("SP_GITLAB_BASE_URL", "https://git.example.com/api/v4")
    GITLAB_PROJECT_ID = os.environ.get("SP_GITLAB_PROJECT_ID", "24890")
    GITLAB_FILE_PATH = "assembly.json"
    GITLAB_BRANCH = "master"

    INTAPI_BASE_URL = os.environ.get("SP_INTAPI_BASE_URL", "")
    INTAPI_AUTH_HEADER = os.environ.get("SP_INTAPI_AUTH_HEADER", "")
    INTAPI_BRAND_ID = os.environ.get("SP_INTAPI_BRAND_ID", "1210")

    ENV_API_ENDPOINTS = {
        "webaqaxmn": os.environ.get("SP_INTAPI_BASE_URL_WEBAQAXMN", os.environ.get("SP_INTAPI_BASE_URL", "")),
        "xmn-up": os.environ.get("SP_INTAPI_BASE_URL_XMN_UP", ""),
        "glpdevxmn": os.environ.get("SP_INTAPI_BASE_URL_GLPDEVXMN", ""),
    }

    DEFAULT_TIMEOUT = 30.0
    CACHE_TTL = 300

    MAX_DESCRIPTION_LENGTH = 80
    SEARCH_RESULTS_LIMIT = 20

    @classmethod
    def get_intapi_base_url(cls, env_name: str = "webaqaxmn") -> str:
        url = cls.ENV_API_ENDPOINTS.get(env_name, cls.INTAPI_BASE_URL)
        if not url:
            raise ValueError(
                f"API endpoint not configured for environment '{env_name}'. "
                f"Please set SP_INTAPI_BASE_URL_{env_name.upper().replace('-', '_')} in .env file"
            )
        return url


class FFSConfig(BaseConfig):
    """Configuration for Feature Flag Service operations."""

    DEFAULT_BASE_URL = os.environ.get(
        "FFS_BASE_URL",
        "http://aws16-c01-ffs01.ffs.svc.c01.eks02.k8s.aws16.lab.nordigy.ru:8080",
    )
    DEFAULT_TIMEOUT = float(os.environ.get("FFS_TIMEOUT", "30.0"))
    CACHE_TTL = 300

    MAX_SEARCH_RESULTS = 100
    MAX_DESCRIPTION_LENGTH = 80


class DeviceSpyConfig(BaseConfig):
    """Configuration for Device Spy operations."""

    BASE_URL = os.environ.get("DS_BASE_URL", "https://device-spy.example.com")
    HOSTS_ENDPOINT = f"{BASE_URL}/api/v1/hosts"
    ALL_DEVICES_ENDPOINT = f"{BASE_URL}/api/v1/hosts/get_all_devices"
    DEVICE_ASSETS_ENDPOINT = f"{BASE_URL}/api/v1/device_assets/"

    DISPLAY_WIDTH = 60


class AccountPoolConfig(BaseConfig):
    """Configuration for Account Pool operations."""

    BASE_URL = os.environ.get("AP_BASE_URL", "https://account-pool.example.com")

    DEFAULT_ENV = "webaqaxmn"
    DEFAULT_BRAND = "1210"

    CACHE_FILE = os.path.join(tempfile.gettempdir(), "account_pool_cache.json")


