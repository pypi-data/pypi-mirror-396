"""
App configuration for uni_bot.
"""

from django.apps import AppConfig

# pylint: disable=import-error
from openedx.core.djangoapps.plugins.constants import (
    ProjectType, SettingsType, PluginURLs, PluginSettings
)

from uni_bot.constants import EXTENSIONS_APP_NAME


class UniBotPluginConfig(AppConfig):
    """
    Uni Bot Plugin configuration.
    """
    name = EXTENSIONS_APP_NAME
    verbose_name = 'Uni Bot Plugin'

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
            ProjectType.CMS: {
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

    def ready(self):
        """
        Implicitly connect signal handlers decorated with @receiver.
        """
        from uni_bot import handlers  # pylint: disable=import-outside-toplevel, unused-import
