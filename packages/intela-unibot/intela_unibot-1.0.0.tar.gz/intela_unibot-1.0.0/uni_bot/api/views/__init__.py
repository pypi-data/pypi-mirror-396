"""
Unibot API views.
"""
from uni_bot.api.views.additional_content import AdditionalContentViewSet
from uni_bot.api.views.bot_status import BotStatusView
from uni_bot.api.views.course_context import CourseContextViewSet
from uni_bot.api.views.course_users import CourseUsersView, UserCourseLocationView
from uni_bot.api.views.course_widget_control import CourseWidgetControlViewSet
from uni_bot.api.views.learning_models import ModelsViewSet
from uni_bot.api.views.restricted_questions import RestrictedQuestionViewSet
from uni_bot.api.views.teacher_assistant_settings import (
    TeacherAssistantSettingsView,
    TeacherAssistantSettingsAvatarView,
)


from uni_bot.api.views.widget import WidgetView, WidgetLoaderView, WidgetStaticView

__all__ = [
    'AdditionalContentViewSet',
    'BotStatusView',
    'CourseContextViewSet',
    'CourseUsersView',
    'UserCourseLocationView',
    'CourseWidgetControlViewSet',
    'ModelsViewSet',
    'RestrictedQuestionViewSet',
    'TeacherAssistantSettingsView',
    'TeacherAssistantSettingsAvatarView',
    'WidgetView',
    'WidgetLoaderView',
    'WidgetStaticView',
]
