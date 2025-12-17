"""
Production Django settings for uni_bot_auth project.
"""


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.UNIBOT_JWT_SECRET_KEY = settings.ENV_TOKENS.get('UNIBOT_JWT_SECRET_KEY', 'strong_secret_key')
