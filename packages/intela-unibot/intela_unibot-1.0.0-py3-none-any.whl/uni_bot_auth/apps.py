"""
App configuration for uni_bot_auth.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# pylint: disable=import-error
from openedx.core.djangoapps.plugins.constants import (
    ProjectType, SettingsType, PluginURLs, PluginSettings
)

from uni_bot_auth.constants import EXTENSIONS_APP_NAME


class UniBotAuthAppConfig(AppConfig):
    """
    Uni Bot Auth application configuration.
    """

    name = EXTENSIONS_APP_NAME
    verbose_name = _('Uni Bot Authentication application')

    # Class attribute that configures and enables this app as a Plugin App.
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: EXTENSIONS_APP_NAME,
                PluginURLs.REGEX: '',
                PluginURLs.RELATIVE_PATH: 'urls',
            },
        },

        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                SettingsType.COMMON: {
                    PluginSettings.RELATIVE_PATH: 'settings.common',
                },
                SettingsType.TEST: {
                    PluginSettings.RELATIVE_PATH: 'settings.test',
                },
                SettingsType.PRODUCTION: {
                    PluginSettings.RELATIVE_PATH: 'settings.production',
                },
            },
        }
    }
