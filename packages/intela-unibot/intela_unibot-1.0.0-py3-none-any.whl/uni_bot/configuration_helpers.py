"""
Provides helper functions for interaction with the plugin configuration.
"""

from typing import Any, Union
from urllib.parse import urljoin

import requests
from django.apps import apps
from django.conf import settings

_Sentinel = type("_Sentinel", (), {})

_sentinel = _Sentinel()


def get_value(value_name: str, default: Any = None) -> Any:
    """
    Provides the value from the plugin configuration.
    """
    # pylint: disable=invalid-name
    UniBotSettingsConfiguration = apps.get_model(
        "uni_bot", "UniBotSettingsConfiguration"
    )  # Dynamic import to avoid circular imports
    current_config = UniBotSettingsConfiguration.current()

    if current_config.enabled:
        return current_config.config_values.get(value_name, default)

    return default


def get_unibot_base_url(default: Union[str, _Sentinel] = _sentinel) -> str:
    """
    Provides the Uni Bot base URL.
    """
    default_value = default if default is not _sentinel else settings.UNIBOT_BASE_URL
    return get_value("UNIBOT_BASE_URL", default_value)


def include_file_content_during_data_collection(
    default: Union[str, _Sentinel] = _sentinel,
) -> bool:
    """
    Decides whether to include file content during data collection.
    """
    default_value = (
        default
        if default is not _sentinel
        else settings.FEATURES["INCLUDE_FILE_CONTENT_DURING_DATA_COLLECTION"]
    )
    return get_value("INCLUDE_FILE_CONTENT_DURING_DATA_COLLECTION", default_value)


def get_api_headers():
    """Generate headers for API requests."""
    api_key = get_value("UNIBOT_API_KEY", "")
    return {"accept": "application/json", "X-API-KEY": api_key}


def fetch_unibot_data(
    endpoint: str = settings.UNIBOT_GLOBAL_SETTINGS_ENDPOINT, param: str = None
):
    """Fetch data from the UniBot API."""
    base_url = get_unibot_base_url()
    api_url = urljoin(base_url, endpoint)
    try:
        response = requests.get(api_url, headers=get_api_headers(), timeout=30)
        response.raise_for_status()
        data = response.json()
        if param:
            return {param: data.get(param)}
        return data
    except (requests.RequestException, ValueError):
        return {}
