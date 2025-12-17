"""
Production Django settings for uni_bot project.
"""


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.UNIBOT_INSTRUCTOR_WIDGET_DISPLAYING_MODE = settings.ENV_TOKENS.get(
        "UNIBOT_INSTRUCTOR_WIDGET_DISPLAYING_MODE",
        "custom_widget_in_separate_tab",
    )

    settings.UNIBOT_BASE_URL = settings.ENV_TOKENS.get(
        "UNIBOT_BASE_URL", "https://example.com"
    )
    settings.UNIBOT_API_KEY = settings.ENV_TOKENS.get(
        "UNIBOT_API_KEY", "extremely_strong_key"
    )
    settings.UNIBOT_TA_SETTINGS_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_TA_SETTINGS_ENDPOINT",
        "api/plugin/settings/{course_id}",
    )
    settings.UNIBOT_TA_SETTINGS_AVATAR_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_TA_SETTINGS_AVATAR_ENDPOINT",
        "api/plugin/settings/{course_id}/avatar",
    )
    settings.UNIBOT_COURSE_CONTEXTS_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_COURSE_CONTEXTS_ENDPOINT",
        "api/plugin/courses/{course_id}/context",
    )
    settings.UNIBOT_COURSE_CONTEXT_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_COURSE_CONTEXT_ENDPOINT",
        "api/plugin/courses/{course_id}/context/{section_id}",
    )
    settings.UNIBOT_RESTRICTED_QUESTIONS_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_RESTRICTED_QUESTIONS_ENDPOINT",
        "api/plugin/courses/{course_id}/question",
    )
    settings.UNIBOT_RESTRICTED_QUESTIONS_RESTRICT_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_RESTRICTED_QUESTIONS_RESTRICT_ENDPOINT",
        "api/plugin/courses/{course_id}/question/restrict",
    )
    settings.UNIBOT_RESTRICTED_QUESTION_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_RESTRICTED_QUESTION_ENDPOINT",
        "api/plugin/courses/{course_id}/question/{question_uuid}",
    )
    settings.UNIBOT_STATUS_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_STATUS_ENDPOINT",
        "api/plugin/course/{course_id}",
    )
    settings.UNIBOT_MODELS_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_MODELS_ENDPOINT",
        "api/plugin/course/{course_id}/model",
    )
    settings.UNIBOT_MODEL_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_MODEL_ENDPOINT",
        "api/plugin/course/{course_id}/model/{model_uuid}",
    )
    settings.UNIBOT_COURSE_SIGNAL_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_COURSE_SIGNAL_ENDPOINT",
        "api/plugin/signal/course/{course_id}",
    )
    settings.UNIBOT_ADDITIONAL_CONTENT_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_ADDITIONAL_CONTENT_ENDPOINT",
        "api/plugin/{course_id}/context/additional",
    )
    settings.UNIBOT_ADDITIONAL_CONTENT_ITEM_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_ADDITIONAL_CONTENT_ITEM_ENDPOINT",
        "api/plugin/context/additional/{item_uuid}",
    )
    settings.UNIBOT_GLOBAL_SETTINGS_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_GLOBAL_SETTINGS_ENDPOINT", "api/plugin/admin/settings"
    )
    settings.UNIBOT_RESET_COURSE_WIDGET_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_RESET_COURSE_WIDGET_ENDPOINT",
        "api/plugin/course/{course_id}/reset-widget",
    )
    settings.UNIBOT_WIDGET_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_WIDGET_ENDPOINT",
        "api/widget",
    )
    settings.UNIBOT_LOADER_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_LOADER_ENDPOINT",
        "api/widget/loader",
    )
    settings.UNIBOT_STATIC_ENDPOINT = settings.ENV_TOKENS.get(
        "UNIBOT_STATIC_ENDPOINT", "widget"
    )
