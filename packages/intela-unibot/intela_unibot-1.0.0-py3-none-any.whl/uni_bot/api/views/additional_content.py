"""
Additional content API views.
"""
from django.http import HttpResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from uni_bot.api.client import UniBotAdditionalContentClient
from uni_bot.api.permissions import IsCustomInstructorWidgetRenderedInSeparateTab, IsStaffOrInstructor


class AdditionalContentViewSet(ViewSet):
    """
    Provide endpoints for additional content.

    Proxy requests to the bot endpoints.
    """

    authentication_classes = [SessionAuthentication, JwtAuthentication]
    permission_classes = [IsCustomInstructorWidgetRenderedInSeparateTab, IsStaffOrInstructor]

    def list(self, _, course_id: str) -> Response:
        """
        Provide the course additional content.

        **Example Request**

            GET /uni_bot/api/additional_content/course-v1:OpenedX+DemoX+DemoCourse/

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "progress": 0.8,
            "contexts": [
                {
                    "name": "course_report",
                    "status": "In Training",
                    "uuid": "c8d18a07-da39-4726-b979-19a9878dd1ac"
                },
                {
                    "name": "additional_resources",
                    "status": "In Training",
                    "uuid": "93a41f1a-59b6-4607-b278-21c08adf9daf"
                }
            ]
        }
        ```
        """
        redirection_response = UniBotAdditionalContentClient().list_additional_content(course_id)

        return Response(redirection_response.json(), status=redirection_response.status_code)

    def create(self, request: Request, course_id: str) -> Response:
        """
        Populate the course additional content.

        **Example Request**

            POST /uni_bot/api/additional_content/course-v1:OpenedX+DemoX+DemoCourse/

        Accept payload with required `file` values. It can contain multiple files.

        **Response Values**

        If the request is successful, an HTTP 201 "Created" response is returned.

        **Example Response**

        ```json
        [
            {
                "name": "course_report",
                "status": "In Training",
                "uuid": "c8d18a07-da39-4726-b979-19a9878dd1ac"
            },
            {
                "name": "additional_resources",
                "status": "In Training",
                "uuid": "93a41f1a-59b6-4607-b278-21c08adf9daf"
            }
        ]
        ```
        """
        redirection_files = [
            (field_name, (uploaded_File.name, uploaded_File.file, uploaded_File.content_type))
            for field_name in request.data.keys()
            for uploaded_File in request.FILES.getlist(field_name)
        ]

        client = UniBotAdditionalContentClient()
        redirection_response = client.send_additional_content(course_id, redirection_files, request.user)

        return Response(redirection_response.json(), status=redirection_response.status_code)

    def destroy(self, request: Request, course_id: str, uuid: str) -> HttpResponse:  # pylint: disable=unused-argument
        """
        Delete the course additional content item.

        **Example Request**

            DELETE /uni_bot/api/additional_content/course-v1:OpenedX+DemoX+DemoCourse/d54a0051-f8f7-40a0-98b8-0b726780b8ab/  # noqa, pylint: disable=line-too-long

        **Response Values**

        If the request is successful, an HTTP 204 "No Content" response is returned.
        """
        redirection_response = UniBotAdditionalContentClient().delete_additional_content(uuid, request.user)

        response_kwargs = {'status': redirection_response.status_code}
        if content_type := redirection_response.headers.get('Content-Type'):
            response_kwargs['content_type'] = content_type

        return HttpResponse(redirection_response.content, **response_kwargs)
