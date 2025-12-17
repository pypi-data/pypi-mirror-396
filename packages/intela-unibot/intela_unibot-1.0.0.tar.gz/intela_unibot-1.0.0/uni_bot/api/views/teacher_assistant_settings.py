"""
Teacher assistant settings API views.
"""
from django.http import HttpResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import FormParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from uni_bot.api.client import UniBotTeacherAssistantClient
from uni_bot.api.permissions import IsCustomInstructorWidgetRenderedInSeparateTab, IsStaffOrInstructor


class TeacherAssistantSettingsView(APIView):
    """
    Provide endpoints for TA settings retrieving and sending for the course.

    Proxy requests to the bot endpoints.
    """

    authentication_classes = [SessionAuthentication, JwtAuthentication]
    permission_classes = [IsCustomInstructorWidgetRenderedInSeparateTab, IsStaffOrInstructor]

    def get(self, __, course_id: str) -> Response:
        """
        Provide TA settings for the course.

        **Example Request**

            GET /uni_bot/api/ta_settings/course-v1:OpenedX+DemoX+DemoCourse/

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "widget": {
                "name": "InfoMate",
                "description": "Helpdesk TA",
                "greeting_string": "Hello world!",
                "feedback_string": "feedback example",
                "width": "300",
                "height": "500",
                "bg_color": "d4dee8",
                "accent_color": "1adee3",
                "text_color": "ffffff",
                "tab_name": "Uni Bot tab"
            },
            "languages": {
                "selected": [
                    {
                        "value": "GB",
                        "label": "English"
                    },
                    {
                        "value": "UA",
                        "label": "Ukrainian"
                    }
                ],
                "available": [
                    {
                        "value": "RU",
                        "label": "Russian"
                    },
                    {
                        "value": "JP",
                        "label": "Japanese"
                    },
                    {
                        "value": "DE",
                        "label": "German"
                    },
                    {
                        "value": "RO",
                        "label": "Romanian"
                    },
                    {
                        "value": "FR",
                        "label": "French"
                    },
                    {
                        "value": "FI",
                        "label": "Finnish"
                    },
                    {
                        "value": "KR",
                        "label": "Korean"
                    },
                    {
                        "value": "ES",
                        "label": "Spanish"
                    },
                    {
                        "value": "PT",
                        "label": "Portuguese"
                    },
                    {
                        "value": "GR",
                        "label": "Greek"
                    },
                    {
                        "value": "CN",
                        "label": "Chinese"
                    },
                    {
                        "value": "DK",
                        "label": "Danish"
                    },
                    {
                        "value": "PL",
                        "label": "Polish"
                    },
                    {
                        "value": "IT",
                        "label": "Italian"
                    },
                    {
                        "value": "NL",
                        "label": "Dutch"
                    },
                    {
                        "value": "HR",
                        "label": "Croatian"
                    },
                    {
                        "value": "LT",
                        "label": "Lithuanian"
                    },
                    {
                        "value": "SI",
                        "label": "Slovenian (Slovene)"
                    },
                    {
                        "value": "ES",
                        "label": "Catalan"
                    },
                    {
                        "value": "MK",
                        "label": "Macedonian"
                    }
                ]
            }
        }
        ```
        """
        redirection_response = UniBotTeacherAssistantClient().retrieve_teacher_assistant_settings(course_id)

        return Response(redirection_response.json(), status=redirection_response.status_code)

    def post(self, request: Request, course_id: str) -> Response:
        """
        Create/update TA settings for the course.

        **Example Request**

            POST /uni_bot/api/ta_settings/course-v1:OpenedX+DemoX+DemoCourse/

        Accept payload with required values:
            - languages,
            - widget:
                - name
                - description
                - greeting_string
                - feedback_string
                - width
                - height
                - bg_color
                - accent_color
                - text_color
                - tab_name

        For example:

        ```json
        {
            "languages": [
                {
                    "value": "GB",
                    "label": "English"
                },
                {
                    "value": "UA",
                    "label": "Ukrainian"
                }
            ],
            "widget": {
                "name": "InfoMate",
                "description": "Helpdesk TA",
                "greeting_string": "Hello world!",
                "feedback_string": "feedback example",
                "width": "300",
                "height": "500",
                "bg_color": "d4dee8",
                "accent_color": "1adee3",
                "text_color": "ffffff",
                "tab_name": "Uni Bot tab"
            }
        }
        ```

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**
        ```json
        {
            "widget": {
                "name": "InfoMate",
                "description": "Helpdesk TA",
                "greeting_string": "Hello world!",
                "feedback_string": "feedback example",
                "width": "300",
                "height": "500",
                "bg_color": "d4dee8",
                "accent_color": "1adee3",
                "text_color": "ffffff",
                "tab_name": "Uni Bot tab"
            },
            "languages": {
                "selected": [
                    {
                        "value": "GB",
                        "label": "English"
                    },
                    {
                        "value": "UA",
                        "label": "Ukrainian"
                    }
                ],
                "available": [
                    {
                        "value": "RU",
                        "label": "Russian"
                    },
                    {
                        "value": "JP",
                        "label": "Japanese"
                    },
                    {
                        "value": "DE",
                        "label": "German"
                    },
                    {
                        "value": "RO",
                        "label": "Romanian"
                    },
                    {
                        "value": "FR",
                        "label": "French"
                    },
                    {
                        "value": "FI",
                        "label": "Finnish"
                    },
                    {
                        "value": "KR",
                        "label": "Korean"
                    },
                    {
                        "value": "ES",
                        "label": "Spanish"
                    },
                    {
                        "value": "PT",
                        "label": "Portuguese"
                    },
                    {
                        "value": "GR",
                        "label": "Greek"
                    },
                    {
                        "value": "CN",
                        "label": "Chinese"
                    },
                    {
                        "value": "DK",
                        "label": "Danish"
                    },
                    {
                        "value": "PL",
                        "label": "Polish"
                    },
                    {
                        "value": "IT",
                        "label": "Italian"
                    },
                    {
                        "value": "NL",
                        "label": "Dutch"
                    },
                    {
                        "value": "HR",
                        "label": "Croatian"
                    },
                    {
                        "value": "LT",
                        "label": "Lithuanian"
                    },
                    {
                        "value": "SI",
                        "label": "Slovenian (Slovene)"
                    },
                    {
                        "value": "ES",
                        "label": "Catalan"
                    },
                    {
                        "value": "MK",
                        "label": "Macedonian"
                    }
                ]
            }
        }
        ```
        """
        client = UniBotTeacherAssistantClient()
        redirection_response = client.send_teacher_assistant_settings(course_id, request.data, request.user)

        return Response(redirection_response.json(), status=redirection_response.status_code)


class TeacherAssistantSettingsAvatarView(APIView):
    """
    Provide endpoints for TA settings avatar retrieving and sending.

    Proxy requests to the bot endpoints.
    """

    authentication_classes = [SessionAuthentication, JwtAuthentication]
    permission_classes = [IsStaffOrInstructor]
    parser_classes = [FormParser]

    def get(self, __, course_id: str):
        """
        Provide TA settings avatar for the course.

        **Example Request**

            GET /uni_bot/api/ta_settings/course-v1:OpenedX+DemoX+DemoCourse/avatar/

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response with attached
        file is returned.
        """
        redirection_response = UniBotTeacherAssistantClient().retrieve_teacher_assistant_settings_avatar(course_id)

        response = HttpResponse(redirection_response.content, content_type=redirection_response.headers['Content-Type'])
        response['Content-Disposition'] = redirection_response.headers['content-disposition']
        return response

    def post(self, request: Request, course_id: str) -> Response:
        """
        Create/update TA settings avatar for the course.

        **Example Request**

            POST /uni_bot/api/ta_settings/course-v1:OpenedX+DemoX+DemoCourse/avatar/

        Accept payload with required values:
            - avatar

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**
        "Avatar successfully saved"
        """
        client = UniBotTeacherAssistantClient()
        redirection_response = client.send_teacher_assistant_settings_avatar(
            course_id,
            {'avatar': request.data['avatar'].file},
            request.user,
        )

        return Response(redirection_response.json(), status=redirection_response.status_code)
