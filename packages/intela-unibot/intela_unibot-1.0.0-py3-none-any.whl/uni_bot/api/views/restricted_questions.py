"""
Restricted questions API views.
"""
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from uni_bot.api.client import UniBotRestrictedQuestionClient
from uni_bot.api.permissions import IsCustomInstructorWidgetRenderedInSeparateTab, IsStaffOrInstructor


class RestrictedQuestionViewSet(ViewSet):
    """
    Provide endpoints for restricted questions.

    Proxy requests to the bot endpoints.
    """

    authentication_classes = [SessionAuthentication, JwtAuthentication]
    permission_classes = [IsCustomInstructorWidgetRenderedInSeparateTab, IsStaffOrInstructor]

    def list(self, __, course_id: str) -> Response:
        """
        Provide restricted questions for the course.

        **Example Request**

            GET /uni_bot/api/restricted_question/course-v1:OpenedX+DemoX+DemoCourse/

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "restrict_graded": true,
            "restrict_non_graded": true,
            "questions": [
                {
                    "context": "Integrals",
                    "restricted_questions": [
                        {
                          "_id": 1,
                          "uuid": "d54a0051-f8f7-40a0-98b8-0b726780b8ab",
                          "content": "Review the image. Calculate the area of the shaded figure using the integral.",
                          "hint": "",
                          "state": "Graded",
                          "status": "Active"
                        }
                    ]
                },
                {
                    "context": "Logarithms",
                    "restricted_questions": [
                        {
                          "_id": 2,
                          "uuid": "80f66d53-0aaf-41ee-8af8-0ff1ba80af1b",
                          "content": "Solve the following logarithmic equation for x.",
                          "hint": "",
                          "state": "Graded",
                          "status": "Active"
                        }
                    ]
                }
            ]
        }
        ```
        """
        redirection_response = UniBotRestrictedQuestionClient().list_restricted_questions(course_id)

        return Response(redirection_response.json(), status=redirection_response.status_code)

    def update(self, request: Request, course_id: str, uuid: str) -> Response:
        """
        Update the restricted question data.

        **Example Request**

            PUT /uni_bot/api/restricted_question/course-v1:OpenedX+DemoX+DemoCourse/d54a0051-f8f7-40a0-98b8-0b726780b8ab/  # noqa, pylint: disable=line-too-long

        Accept payload with `is_active` required value.

        For example:

        ```json
        {
            "is_active": false,
            "hint": "Please, review the lecture 5."
        }
        ```

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "uuid": "d54a0051-f8f7-40a0-98b8-0b726780b8ab",
            "question": "Review the image. Calculate the area of the shaded figure using the integral.",
            "hint": "Please, review the lecture 5.",
            "status": "Disabled"
        }
        ```
        """
        client = UniBotRestrictedQuestionClient()
        redirection_response = client.update_restricted_question(course_id, uuid, request.data, request.user)

        return Response(redirection_response.json(), status=redirection_response.status_code)

    @action(detail=False, methods=['post'], url_path='restrict', url_name='restrict')
    def restrict(self, request: Request, course_id: str) -> Response:
        """
        Set restricted questions restriction status.

        **Example Request**

            POST /uni_bot/api/restricted_question/course-v1:OpenedX+DemoX+DemoCourse/restrict/

        Accept payload with required values:
            - restrict_graded
            - restrict_non_graded

        For example:

        ```json
        {
          "restrict_graded": true,
          "restrict_non_graded": false
        }
        ```

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "restrict_graded": true,
            "restrict_non_graded": false,
            "questions": [
                {
                    "context": "Integrals",
                    "restricted_questions": [
                        {
                          "_id": 1,
                          "uuid": "d54a0051-f8f7-40a0-98b8-0b726780b8ab",
                          "content": "Review the image. Calculate the area of the shaded figure using the integral.",
                          "hint": "",
                          "state": "Graded",
                          "status": "Active"
                        }
                    ]
                },
                {
                    "context": "Logarithms",
                    "restricted_questions": [
                        {
                          "_id": 2,
                          "uuid": "80f66d53-0aaf-41ee-8af8-0ff1ba80af1b",
                          "content": "Solve the following logarithmic equation for x.",
                          "hint": "",
                          "state": "Graded",
                          "status": "Active"
                        }
                    ]
                }
            ]
        }
        ```
        """
        client = UniBotRestrictedQuestionClient()
        redirection_response = client.send_restricted_questions_restriction_status(
            course_id,
            request.data,
            request.user,
        )

        return Response(redirection_response.json(), status=redirection_response.status_code)
