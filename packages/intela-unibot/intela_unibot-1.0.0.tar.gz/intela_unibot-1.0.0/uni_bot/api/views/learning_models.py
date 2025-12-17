"""
Learning models API views.
"""
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from uni_bot.api.client import UniBotLearningModelClient
from uni_bot.api.permissions import IsCustomInstructorWidgetRenderedInSeparateTab, IsStaffOrInstructor


class ModelsViewSet(ViewSet):
    """
    Provide endpoints for a course learning models.
    """

    authentication_classes = [SessionAuthentication, JwtAuthentication]
    permission_classes = [IsCustomInstructorWidgetRenderedInSeparateTab, IsStaffOrInstructor]

    def list(self, __, course_id: str) -> Response:  # pylint: disable=unused-argument
        """
        Provide available course learning models.

        **Example Request**

            GET /uni_bot/api/models/course-v1:OpenedX+DemoX+DemoCourse/

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "selected": [
                {
                    "label": "Unibot",
                    "value": "95aac5b8-934e-4d08-85c4-9127f7e0934a",
                    "data": {
                        "credentials": "System",
                        "description": "Unibot"
                    },
                    "mutable": false,
                    "message": "This model cannot be changed.",
                    "configuration_level": "course"
                }
            ],
            "available": [
                {
                    "label": "Unibot",
                    "value": "95aac5b8-934e-4d08-85c4-9127f7e0934a",
                    "data": {
                        "description": "Unibot",
                        "credentials": "Not set"
                    },
                    "mutable": false,
                    "message": "This model cannot be changed.",
                    "configuration_level": "course"
                },
                {
                    "label": "OpenAI (gpt-4o-mini)",
                    "value": "01c7e8e8-1b15-4fc4-a2d4-afcc69fee781",
                    "data": {
                        "description": "OpenAI",
                        "credentials": "Not set"
                    },
                    "mutable": true,
                    "message": null,
                    "configuration_level": "connection"
                },
                {
                    "label": "WatsonX (llama-3-1-8b)",
                    "value": "9b21eed8-01aa-45e5-b2a9-bfb2694f2843",
                    "data": {
                        "description": "WatsonX",
                        "credentials": "Not set"
                    },
                    "mutable": true,
                    "message": null,
                    "configuration_level": "connection"
                }
            ]
        }
        ```
        """
        redirection_response = UniBotLearningModelClient().list_learning_models(course_id)

        return Response(redirection_response.json(), status=redirection_response.status_code)

    def retrieve(self, __, course_id: str, uuid: str) -> Response:
        """
        Provide a course learning model details.

        **Example Request**

            GET /uni_bot/api/models/course-v1:OpenedX+DemoX+DemoCourse/67a1d42a-ff37-4444-88c1-c1c57d21c1f2/

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "has_credentials": false,
            "fields": {
                "available": {
                    "required_fields": [
                        {
                            "label": "OpenAI Api key",
                            "value": "api_key"
                        }
                    ]
                }
            }
        }
        ```
        """
        redirection_response = UniBotLearningModelClient().retrieve_learning_model(course_id, uuid)

        return Response(redirection_response.json(), status=redirection_response.status_code)

    def update(self, request: Request, course_id: str, uuid: str) -> Response:
        """
        Update an available course learning model.

        **Example Request**

            PUT /uni_bot/api/models/course-v1:OpenedX+DemoX+DemoCourse/67a1d42a-ff37-4444-88c1-c1c57d21c1f2/

        For example:

        ```json
        {
            "use_personal": true,
            "credentials": {
                "api_key": "12345abcde67890fghij"
            }
        }
        ```

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.
        """
        client = UniBotLearningModelClient()
        redirection_response = client.update_learning_model(course_id, uuid, request.data, request.user)

        return Response(redirection_response.json(), status=redirection_response.status_code)
