"""
Bot status API views.
"""
import datetime
from typing import Dict, Optional, Union

import requests
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from uni_bot.api.client import UniBotStatusClient
from uni_bot.api.permissions import IsStaffOrInstructor
from uni_bot.models import CourseMetadata
from uni_bot.utils import define_bot_status


class BotStatusView(APIView):
    """
    Provide endpoints for bot statuses.
    """

    authentication_classes = [SessionAuthentication, JwtAuthentication]
    permission_classes = [IsStaffOrInstructor]

    def get(self, __, course_id: str) -> Response:
        """
        Provide bot-related statuses.

        **Example Request**

            GET /uni_bot/api/bot_status/course-v1:OpenedX+DemoX+DemoCourse/

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "bot_status": "active"
            "is_disabled": false,
            "is_outdated": false,
            "ai_assistant_status": false,
            "ai_assistant_message": "Dummy message."
        }
        ```
        """
        redirection_response = UniBotStatusClient().retrieve_unibot_status(course_id)

        return self.generate_response(course_id, redirection_response)

    def generate_response(self, course_id: str, redirection_response: requests.Response) -> Response:
        """
        Generate the view response based on redirection response.
        """
        if redirection_response.status_code == status.HTTP_200_OK:
            response_body = self.build_status_getting_response_body(course_id, redirection_response.json())

            return Response(response_body, status=status.HTTP_200_OK)
        return Response(redirection_response.json(), status=redirection_response.status_code)

    def build_status_getting_response_body(
        self,
        course_id: str,
        redirection_response_body: Dict[str, Union[bool, str]],
    ) -> Dict[str, bool]:
        """
        Build a body for `GET` request response.
        """
        is_bot_disabled = redirection_response_body['is_disabled']
        is_course_structure_outdated = self.is_course_structure_outdated(
            course_id,
            redirection_response_body['last_upload'],
        )
        bot_readiness_status = redirection_response_body['bot_status']
        bot_status = define_bot_status(bot_readiness_status, is_bot_disabled, is_course_structure_outdated)

        return {
            'bot_status': bot_status,
            'is_disabled': is_bot_disabled,
            'is_outdated': is_course_structure_outdated,
            'ai_assistant_status': redirection_response_body['ai_assistant_status'],
            'ai_assistant_message': redirection_response_body['ai_assistant_message'],
        }

    @staticmethod
    def is_course_structure_outdated(course_id: str, last_upload_data: Optional[str]) -> bool:
        """
        Check whether a course structure is outdated.
        """
        if last_upload_data:
            last_upload_timestamp = datetime.datetime.fromisoformat(last_upload_data)

            try:
                return (
                    CourseMetadata.objects.get(course_key=course_id)  # pylint: disable=no-member
                    .is_course_structure_outdated(last_upload_timestamp)
                )
            except CourseMetadata.DoesNotExist:  # pylint: disable=no-member
                return True
        return False

    def put(self, request, course_id: str) -> Response:
        """
        Update bot-related statuses.

        Proxy requests to the bot endpoints.

        **Example Request**

            PUT /uni_bot/api/bot_status/course-v1:OpenedX+DemoX+DemoCourse/

        Accept payload with `is_disabled` required value.

        For example:

        ```json
        {
            "is_disabled": true
        }
        ```

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "bot_status": "in_training"
            "is_disabled": true,
            "is_outdated": false,
            "ai_assistant_status": true,
            "ai_assistant_message": null
        }
        ```
        """
        redirection_response = UniBotStatusClient().update_bot_status(course_id, request.data, request.user)

        return self.generate_response(course_id, redirection_response)
