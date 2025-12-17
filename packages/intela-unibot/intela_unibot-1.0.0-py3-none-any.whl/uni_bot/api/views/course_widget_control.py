"""
Course widget control API views.
"""
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet

from uni_bot.api.client import UniBotCourseWidgetControlClient


class CourseWidgetControlViewSet(ViewSet):
    """
    Provide endpoints for course widget control.

    Proxy requests to the bot endpoints.
    """

    @action(detail=False, methods=['post'], url_path='reset_widget', url_name='reset_widget')
    def reset_widget(self, request: Request, course_id: str) -> HttpResponse:
        """
        Reset all widget settings for the course to their defaults.

        **Example Request**

            POST /uni_bot/api/course_widget_control/course-v1:OpenedX+DemoX+DemoCourse/reset_widget/

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.
        """
        redirection_response = UniBotCourseWidgetControlClient().reset_widget(course_id, request.user)

        return HttpResponse(redirection_response.content, status=redirection_response.status_code)
