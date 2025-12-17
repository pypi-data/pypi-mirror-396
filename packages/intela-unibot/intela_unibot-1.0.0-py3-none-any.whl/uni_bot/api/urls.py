"""
Unibot API URL Configurations.
"""
from django.urls import include, path, re_path

from openedx.core.constants import COURSE_ID_PATTERN  # pylint: disable=import-error

from uni_bot.api import routers, views

usage_key_lookup_router = routers.UsageKeyLookupRouter()
usage_key_lookup_router.register(
    rf'course_context/{COURSE_ID_PATTERN}',
    views.CourseContextViewSet,
    basename='course_context',
)
usage_key_lookup_router.register(
    rf'course_widget_control/{COURSE_ID_PATTERN}',
    views.CourseWidgetControlViewSet,
    basename='course_widget_control',
)

uuid_lookup_router = routers.UuidLookupRouter()
uuid_lookup_router.register(
    rf'restricted_question/{COURSE_ID_PATTERN}',
    views.RestrictedQuestionViewSet,
    basename='restricted_question',
)
uuid_lookup_router.register(
    rf'additional_content/{COURSE_ID_PATTERN}',
    views.AdditionalContentViewSet,
    basename='additional_content',
)
uuid_lookup_router.register(
    rf'models/{COURSE_ID_PATTERN}',
    views.ModelsViewSet,
    basename='models',
)


urlpatterns = [
    path('', include([*usage_key_lookup_router.urls, *uuid_lookup_router.urls])),
    path('widget/', views.WidgetView.as_view(), name='widget'),
    path('widget/loader/', views.WidgetLoaderView.as_view(), name='widget_loader'),
    re_path(r'^widget/static/(?P<filename>[\w.-]+)$', views.WidgetStaticView.as_view(), name='widget_static'),
    path('user_course_location/', views.UserCourseLocationView.as_view(), name='user_course_location'),
    re_path(
        rf'ta_settings/{COURSE_ID_PATTERN}/avatar/',
        views.TeacherAssistantSettingsAvatarView.as_view(),
        name='ta_settings_avatar',
    ),
    re_path(rf'ta_settings/{COURSE_ID_PATTERN}/', views.TeacherAssistantSettingsView.as_view(), name='ta_settings'),
    re_path(rf'course_users/{COURSE_ID_PATTERN}/', views.CourseUsersView.as_view(), name='course_users'),
    re_path(rf'bot_status/{COURSE_ID_PATTERN}/', views.BotStatusView.as_view(), name='bot_status'),
]
