"""
Contains a unibot tab.
"""
from django.utils.translation import gettext_noop

# pylint: disable=import-error
from lms.djangoapps.courseware.access import has_access
from xmodule.tabs import CourseTab

from uni_bot.constants import EXTENSIONS_APP_NAME
from uni_bot.enums import UnibotInstructorWidgetDisplayingMode
from uni_bot.utils import is_enabled_instructor_widget_displaying_mode_in


class UniBotDashboardTab(CourseTab):  # pylint: disable=too-few-public-methods
    """
    Provide information for tab.
    """

    name = 'unibot'
    type = 'unibot'
    title = gettext_noop('AI Assistant')
    view_name = f'{EXTENSIONS_APP_NAME}:unibot_tab'
    is_dynamic = True

    @classmethod
    def is_enabled(cls, course, user=None):
        """
        Check whether the tab is enabled.

        Enable the tab only to instructors and staff members if the tab
        rendering is allowed by the instructor widget displaying mode.
        """
        is_allowed_by_plugin_mode = is_enabled_instructor_widget_displaying_mode_in(
            UnibotInstructorWidgetDisplayingMode.get_widget_in_separate_tab_modes()
        )
        return (
            is_allowed_by_plugin_mode
            and user
            and user.is_authenticated
            and has_access(user, 'staff', course, course.id)
        )
