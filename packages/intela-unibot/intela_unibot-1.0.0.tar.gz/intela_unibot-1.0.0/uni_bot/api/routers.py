"""
Unibot API Routers.
"""
from django.conf import settings
from rest_framework.routers import DefaultRouter

from uni_bot.constants import UUID_PATTERN


class UsageKeyLookupRouter(DefaultRouter):
    """
    Route endpoints with usage key lookup regex.
    """

    include_format_suffixes = False

    def get_lookup_regex(self, *args, **kwargs) -> str:  # pylint: disable=unused-argument
        return settings.USAGE_KEY_PATTERN


class UuidLookupRouter(DefaultRouter):
    """
    Route endpoints with UUID lookup regex.
    """

    include_format_suffixes = False

    def get_lookup_regex(self, *args, **kwargs) -> str:  # pylint: disable=unused-argument
        return UUID_PATTERN
