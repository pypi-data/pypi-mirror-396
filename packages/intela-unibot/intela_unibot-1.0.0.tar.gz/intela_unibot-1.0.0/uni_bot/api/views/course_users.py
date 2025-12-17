"""
Course users API views.
"""
import re
from typing import Dict, Optional
from urllib.parse import urlparse

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from django.conf import settings
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from uni_bot.api.permissions import IsStaffOrInstructor
from uni_bot.api.serializers import UserSerializer
from uni_bot.data_collectors import UserCourseLocationDataCollector
from uni_bot.services import UserService


class CourseUsersView(ListAPIView):
    """
    Enlist the course active users.

    **Use Case**

        Get information about the users enrolled on the course that contains
        the course role, User model fields and UserProfile fields.

    **Example Requests**

        GET /uni_bot/api/course_users/course-v1:OpenedX+DemoX+DemoCourse/

    **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.
        The HTTP 200 response contains a dict with page pagination information and `results`
        keys.

    **Example response**

        ```json
            {
                "next": null,
                "previous": null,
                "count": 2,
                "num_pages": 1,
                "current_page": 1,
                "start": 0,
                "results": [
                    {
                        "id": 4,
                        "profile": {
                            "id": 2,
                            "country": "",
                            "name": "Emily Brown",
                            "meta": "",
                            "courseware": "course.xml",
                            "language": "",
                            "location": "",
                            "year_of_birth": null,
                            "gender": null,
                            "level_of_education": null,
                            "mailing_address": null,
                            "city": null,
                            "state": null,
                            "goals": null,
                            "bio": null,
                            "profile_image_uploaded_at": null,
                            "phone_number": null,
                            "user": 4
                        },
                        "course_role": "Student",
                        "last_login": "2024-06-06T15:52:55.751993Z",
                        "is_superuser": false,
                        "username": "emily_brown",
                        "first_name": "",
                        "last_name": "",
                        "email": "emily.brown@example.com",
                        "is_staff": false,
                        "is_active": true,
                        "date_joined": "2024-06-06T01:14:57.101403Z",
                        "groups": [],
                        "user_permissions": []
                    },
                    {
                        "id": 10,
                        "profile": {
                            "id": 8,
                            "country": "AU",
                            "name": "David Wilson",
                            "meta": "",
                            "courseware": "course.xml",
                            "language": "",
                            "location": "",
                            "year_of_birth": 1950,
                            "gender": "m",
                            "level_of_education": "p",
                            "mailing_address": null,
                            "city": null,
                            "state": null,
                            "goals": null,
                            "bio": null,
                            "profile_image_uploaded_at": null,
                            "phone_number": null,
                            "user": 10
                        },
                        "course_role": "instructor",
                        "last_login": "2024-06-14T16:54:03.310527Z",
                        "is_superuser": false,
                        "username": "david_wilson",
                        "first_name": "",
                        "last_name": "",
                        "email": "david.wilson@example.com",
                        "is_staff": false,
                        "is_active": true,
                        "date_joined": "2024-06-14T15:02:08.437192Z",
                        "groups": [],
                        "user_permissions": []
                    }
                ]
            }
        ```
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [IsStaffOrInstructor]
    serializer_class = UserSerializer

    def get_queryset(self):
        return (
            UserService()
            .get_active_course_enrollers_with_roles(self.kwargs['course_id'])
            .select_related('profile')
        )


class UserCourseLocationView(APIView):
    """
    Provide user-related information about current location inside the course.

    **Example Requests**

        GET /uni_bot/api/user_course_location/

    **Example response**

        ```json
        {
            "user_nickname": "john_doe_24",
            "user_fullname": "John Doe",
            "user_email": "jd@example.com",
            "user_role": "instructor",
            "portal_name": "Intela",
            "portal_host": "lms.edx.intela.com",
            "course_id": "course-v1:Math+IT+M_7",
            "course_name": "Introduction to Mathematical Thinking",
            "section_id": "block-v1:Math+IT+M_7+type@chapter+block@f1f009f328764904a1ac4ff2f3082ce4",
            "section_name": "Boolean algebra",
            "subsection_id": "block-v1:Math+IT+M_7+type@sequential+block@4b0c200c078849b39ecf49378813327d",
            "subsection_name": "Laws of Boolean Algebra",
            "unit_id": "block-v1:RG+RG_IM2+6+type@vertical+block@4dce11f5e3dc4a09a19dbb7e636b6c89",
            "unit_name": "Distributive Law",
            "page_url": "https://apps.edx.intela.com/learning/course/course-v1:Math+IT+M_7/block-v1:Math+IT+M_7+type@sequential+block@4b0c200c078849b39ecf49378813327d/block-v1:RG+RG_IM2+6+type@vertical+block@4dce11f5e3dc4a09a19dbb7e636b6c89"  # noqa, pylint: disable=line-too-long
        }
        ```
    """

    authentication_classes = (SessionAuthentication,)

    def get(self, request: Request) -> Response:  # pylint: disable=missing-function-docstring
        if not (
            (referer := request.headers.get('Referer'))
            and referer.startswith(settings.LEARNING_MICROFRONTEND_URL)
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if not (referer_course_location_data := self._parse_referer_course_location_data(referer)):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response_data = UserCourseLocationDataCollector().collect(request.user, referer_course_location_data)
        response_data['page_url'] = referer

        return Response(response_data)

    @staticmethod
    def _parse_referer_course_location_data(referer: str) -> Optional[Dict[str, str]]:
        """
        Parse course location data from the referer URL.
        """
        referer_path = urlparse(referer).path

        sequential_key_pattern = settings.USAGE_KEY_PATTERN.replace('<usage_key_string>', '<sequential_key_string>')
        vertical_key_pattern = settings.USAGE_KEY_PATTERN.replace('<usage_key_string>', '<vertical_key_string>')
        accepted_path_regexes = [
            rf'^/learning/course/{settings.COURSE_ID_PATTERN}/{sequential_key_pattern}/{vertical_key_pattern}',
            rf'^/learning/course/{settings.COURSE_ID_PATTERN}/.*',
        ]

        for accepted_path_regex in accepted_path_regexes:
            if match := re.fullmatch(accepted_path_regex, referer_path):
                return match.groupdict()

        return None
