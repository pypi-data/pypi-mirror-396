"""
Course context API views.
"""
from typing import List

from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from opaque_keys.edx.keys import CourseKey
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

# pylint: disable=import-error
from cms.djangoapps.models.settings.encoder import CourseSettingsEncoder
from xmodule.modulestore.django import modulestore

from uni_bot.api.client import UniBotCourseContextClient
from uni_bot.api.permissions import IsCustomInstructorWidgetRenderedInSeparateTab, IsStaffOrInstructor
from uni_bot.data_collectors import CourseDataCollector


class CourseContextViewSet(ViewSet):
    """
    Provide endpoints for course context.
    """

    authentication_classes = [SessionAuthentication, JwtAuthentication]

    def get_permissions(self) -> List[BasePermission]:
        permissions = [IsStaffOrInstructor()]

        if self.action in ('list', 'update'):
            permissions.append(IsCustomInstructorWidgetRenderedInSeparateTab())

        return permissions

    def list(self, __, course_id: str) -> Response:
        """
        Provide course contexts.

        Proxy the request to the bot endpoint.

        **Example Request**

            GET /uni_bot/api/course_context/course-v1:OpenedX+DemoX+DemoCourse/

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "progress": 0.6,
            "contexts": [
                {
                    "section_id": "block-v1:OpenedX+DemoX+DemoCourse+type@chapter+block@f3aa2011b3c948f68eb03c5be0ffbde1",  # noqa, pylint: disable=line-too-long
                    "name": "Integrals",
                    "status": "Disabled"
                },
                {
                    "section_id": "block-v1:OpenedX+DemoX+DemoCourse+type@chapter+block@68aa2011c3c948868eb03c5be5babee7",  # noqa, pylint: disable=line-too-long
                    "name": "Logarithms",
                    "status": "Active"
                }
            ]
        }
        ```
        """
        redirection_response = UniBotCourseContextClient().list_course_contexts(course_id)

        return Response(redirection_response.json(), status=redirection_response.status_code)

    @action(detail=False, methods=['get'], url_path='scan', url_name='scan')
    def scan(self, __, course_id: str) -> HttpResponse:
        """
        Scan the course and provides the collected course contexts.

        **Example Request**

            GET /uni_bot/api/course_context/course-v1:OpenedX+DemoX+DemoCourse/scan/

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "course_id": "course-v1:OpenedX+DemoX+DemoCourse",
            "course_name": "Math",
            "content": [
                {
                    "section_id": "block-v1:OpenedX+DemoX+DemoCourse+type@chapter+block@f3aa2011b3c948f68eb03c5be0ffbde1",  # noqa, pylint: disable=line-too-long
                    "section_name": "Integrals",
                    "content": [
                        {
                            "block_id": "block-v1:OpenedX+DemoX+DemoCourse+type@video+block@4d982badf99d4c7ca77d2cf917ef806f",  # noqa, pylint: disable=line-too-long
                            "fields": {
                                "display_name": "What is an integral?",
                                "youtube_id_1_0": "7_yD_cEfoCk",
                            },
                            "breadcrumbs": "Math / Integrals / Integrals Introduction / First steps with integrals",
                            "unit_id": "block-v1:OpenedX+DemoX+DemoCourse+type@vertical+block@9d9334cce44c4c56bfe5b9ceff7ac780"  # noqa, pylint: disable=line-too-long
                        }
                    ]
                },
                {
                    "section_id": "block-v1:OpenedX+DemoX+DemoCourse+type@chapter+block@68aa2011c3c948868eb03c5be5babee7",  # noqa, pylint: disable=line-too-long
                    "section_name": "Logarithms",
                    "content": [
                        {
                            "block_id": "block-v1:OpenedX+DemoX+DemoCourse+type@html+block@b452a2391d8842858d78a029b43e1da5",  # noqa, pylint: disable=line-too-long
                            "fields": {
                                "display_name": "Logarithms concepts",
                                "data": "<div>A lot of theory</div>",
                            },
                            "breadcrumbs": "Math / Logarithms / Logarithms Introduction / First steps with logarithms",
                            "unit_id": "block-v1:OpenedX+DemoX+DemoCourse+type@vertical+block@2089c5c0bb9748fc9c675a3052152593"  # noqa, pylint: disable=line-too-long
                        }
                    ]
                }
            ],
            "metadata": {
                "overview": "Welcome to the Open edX Demo Course!",
                "start_date": "2020-01-06T00:00:00Z"
            }
        }
        ```

        If the course is not found, an HTTP 404 "Not Found" response is returned.
        """
        course_key = CourseKey.from_string(course_id)
        course = modulestore().get_course(course_key)
        if course is None:
            return HttpResponseNotFound()

        course_data = CourseDataCollector().collect(course)

        return JsonResponse(course_data, CourseSettingsEncoder)

    def create(self, request: Request, course_id: str) -> Response:
        """
        Collect the course context and provides the contexts data.

        **Example Request**

            POST /uni_bot/api/course_context/course-v1:OpenedX+DemoX+DemoCourse/

        The request doesn't expect the body content.

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "progress": 0.6,
            "contexts": [
                {
                    "section_id": "block-v1:OpenedX+DemoX+DemoCourse+type@chapter+block@f3aa2011b3c948f68eb03c5be0ffbde1",  # noqa, pylint: disable=line-too-long
                    "name": "Integrals",
                    "status": "Disabled"
                },
                {
                    "section_id": "block-v1:OpenedX+DemoX+DemoCourse+type@chapter+block@68aa2011c3c948868eb03c5be5babee7",  # noqa, pylint: disable=line-too-long
                    "name": "Logarithms",
                    "status": "Active"
                }
            ]
        }
        ```
        """
        course_key = CourseKey.from_string(course_id)
        course = modulestore().get_course(course_key)
        if course is None:
            return HttpResponseNotFound()

        course_data = CourseDataCollector().collect(course)
        redirection_response = UniBotCourseContextClient().send_course_contexts(course_id, course_data, request.user)

        return Response(redirection_response.json(), status=redirection_response.status_code)

    def update(self, request: Request, course_id: str, usage_key_string: str) -> Response:
        """
        Update the course context data.

        Proxy the request to the bot endpoint.

        **Example Request**

            PUT /uni_bot/api/course_context/course-v1:OpenedX+DemoX+DemoCourse/block-v1:OpenedX+DemoX+DemoCourse+type@chapter+block@f3aa2011b3c948f68eb03c5be0ffbde1/  # noqa, pylint: disable=line-too-long

        Accept payload with `is_active` required value.

        For example:

        ```json
        {
            "is_active": true
        }
        ```

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "section_id": "block-v1:OpenedX+DemoX+DemoCourse+type@chapter+block@f3aa2011b3c948f68eb03c5be0ffbde1",
            "name": "Integrals",
            "status": "Active"
        }
        ```
        """
        client = UniBotCourseContextClient()
        redirection_response = client.update_course_context(course_id, usage_key_string, request.data, request.user)

        return Response(redirection_response.json(), status=redirection_response.status_code)
