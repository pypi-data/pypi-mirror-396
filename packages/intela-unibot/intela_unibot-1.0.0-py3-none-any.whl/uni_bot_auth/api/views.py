from django.conf import settings
from edx_rest_framework_extensions.settings import get_first_jwt_issuer
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from openedx.core.djangoapps.oauth_dispatch.jwt import create_jwt_for_user

from uni_bot import configuration_helpers


class GenerateJwtView(APIView):
    """
    Allow to generate a Uni Bot-related JWT token.
    """

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        """
        Provide JWT token for the user authenticated by session.

        **Example Request**

            GET /uni_bot_auth/api/jwt/generate/

        **Response Values**

        If the request is successful, an HTTP 200 "OK" response is returned.

        **Example Response**

        ```json
        {
            "jwt": "<JWT_TOKEN_HERE>"
        }
        ```
        """
        scopes = ['read', 'write', 'email', 'profile']
        jwt_issuer = get_first_jwt_issuer()
        unibot_jwt_secret_key = configuration_helpers.get_value('UNIBOT_JWT_SECRET_KEY', settings.UNIBOT_JWT_SECRET_KEY)
        jwt = create_jwt_for_user(request.user, unibot_jwt_secret_key, aud=jwt_issuer['AUDIENCE'], scopes=scopes)

        return Response({'jwt': jwt})
