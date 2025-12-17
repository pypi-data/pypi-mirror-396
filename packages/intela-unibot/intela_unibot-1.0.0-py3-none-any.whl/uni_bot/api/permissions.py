"""
Unibot API permissions.
"""
from opaque_keys.edx.keys import CourseKey
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

# pylint: disable=import-error
from common.djangoapps.student.roles import CourseInstructorRole, CourseStaffRole, GlobalStaff

from uni_bot.enums import UnibotInstructorWidgetDisplayingMode


class IsStaffOrInstructor(BasePermission):
    """
    Allow access to users with staff privileges and instructors.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        course_key = CourseKey.from_string(view.kwargs.get('course_id'))
        user = request.user

        return (
            GlobalStaff().has_user(user) or
            CourseStaffRole(course_key).has_user(user) or
            CourseInstructorRole(course_key).has_user(user)
        )


class IsCustomInstructorWidgetRenderedInSeparateTab(BasePermission):
    """
    Control access based on the enabled instructor widget displaying mode.

    Allow access for requests if the mode in which the custom unibot instructor
    widget is rendered in the separate tab is enabled.
    """

    def has_permission(self, *_) -> bool:
        return UnibotInstructorWidgetDisplayingMode.CUSTOM_WIDGET_IN_SEPARATE_TAB.is_enabled()
