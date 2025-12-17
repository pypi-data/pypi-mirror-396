"""
Common Django settings for uni_bot project.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

from path import Path

from openedx.core.lib.derived import Derived  # pylint: disable=import-error

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'secret-key'


# Application definition

INSTALLED_APPS = []

ROOT_URLCONF = 'uni_bot.urls'


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_TZ = True


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.STATICFILES_DIRS.insert(0, Path(__file__).parent.parent + '/frontend-app/dist/')

    settings.UNIBOT_INSTRUCTOR_WIDGET_DISPLAYING_MODE = 'custom_widget_in_separate_tab'

    settings.DEFAULT_PROXY_REQUEST_TIMEOUT_SECONDS = 5

    settings.UNIBOT_BASE_URL = 'https://example.com'
    settings.UNIBOT_API_KEY = 'extremely_strong_key'
    settings.UNIBOT_TA_SETTINGS_ENDPOINT = 'api/plugin/settings/{course_id}'
    settings.UNIBOT_TA_SETTINGS_AVATAR_ENDPOINT = 'api/plugin/settings/{course_id}/avatar'
    settings.UNIBOT_COURSE_CONTEXTS_ENDPOINT = 'api/plugin/courses/{course_id}/context'
    settings.UNIBOT_COURSE_CONTEXT_ENDPOINT = 'api/plugin/courses/{course_id}/context/{section_id}'
    settings.UNIBOT_RESTRICTED_QUESTIONS_ENDPOINT = 'api/plugin/courses/{course_id}/question'
    settings.UNIBOT_RESTRICTED_QUESTIONS_RESTRICT_ENDPOINT = 'api/plugin/courses/{course_id}/question/restrict'
    settings.UNIBOT_RESTRICTED_QUESTION_ENDPOINT = 'api/plugin/courses/{course_id}/question/{question_uuid}'
    settings.UNIBOT_STATUS_ENDPOINT = 'api/plugin/course/{course_id}'
    settings.UNIBOT_MODELS_ENDPOINT = 'api/plugin/course/{course_id}/model'
    settings.UNIBOT_MODEL_ENDPOINT = 'api/plugin/course/{course_id}/model/{model_uuid}'
    settings.UNIBOT_COURSE_SIGNAL_ENDPOINT = 'api/plugin/signal/course/{course_id}'
    settings.UNIBOT_ADDITIONAL_CONTENT_ENDPOINT = 'api/plugin/{course_id}/context/additional'
    settings.UNIBOT_ADDITIONAL_CONTENT_ITEM_ENDPOINT = 'api/plugin/context/additional/{item_uuid}'
    settings.UNIBOT_GLOBAL_SETTINGS_ENDPOINT = 'api/plugin/admin/settings'
    settings.UNIBOT_RESET_COURSE_WIDGET_ENDPOINT = 'api/plugin/course/{course_id}/reset-widget'
    settings.UNIBOT_WIDGET_ENDPOINT = 'api/widget'
    settings.UNIBOT_LOADER_ENDPOINT = 'api/widget/loader'
    settings.UNIBOT_STATIC_ENDPOINT = 'widget'
    settings.UNIBOT_INSTRUCTOR_WIDGET_SCRIPT = '<script>console.log("Unibot script example");</script>'

    settings.FEATURES['INCLUDE_FILE_CONTENT_DURING_DATA_COLLECTION'] = True

    add_current_app_templates_to_templates_dirs_settings(settings)


def add_current_app_templates_to_templates_dirs_settings(settings):
    """
    Adds the current app templates directory to the templates directories setting.
    """
    app_templates = Path(__file__).parent.parent / 'templates'
    settings.MAKO_TEMPLATE_DIRS_BASE.insert(0, app_templates)
    for template in settings.TEMPLATES:
        template_dirs = template['DIRS']
        if not (callable(template_dirs) or isinstance(template_dirs, Derived)):
            template['DIRS'].insert(0, app_templates)
