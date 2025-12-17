"""
Widget streaming API view.
"""

from typing import Union

import requests
from django.http import HttpResponse, StreamingHttpResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from uni_bot.api.client import UniBotWidgetClient


class WidgetView(APIView):
    """
    Provide widget streaming endpoint.

    Proxies requests to UniBot backend and handles both streaming
    and regular JSON responses based on response headers.
    """

    authentication_classes = [
        SessionAuthentication,
        JwtAuthentication,
    ]

    def post(self, request: Request) -> Union[StreamingHttpResponse, Response]:
        """
        Handle widget requests with streaming support.

        **Example Request**

            POST /uni_bot/api/widget/

        Accept full payload from frontend as-is and proxy it to backend.

        For example:

        ```json
        {
            "product_id": "d70e5a8e-eee7-4a63-be3b-dd8f2055eeda",
            "session_id": "318cbf41-fb2c-4515-975d-212cf02789af",
            "agent_lang": "en-US",
            "query_type": "question_data",
            "query_data": "What is machine learning?",
            "location": {
                "section_name": null,
                "subsection_name": null,
                "unit_name": null,
                "client_email": "user@email.com"
            }
        }
        ```

        **Response Values**

        If the request is successful and the response is streaming,
        an HTTP 200 "OK" with text/plain content-type is returned.

        If the response is JSON, an HTTP 200 "OK" with application/json
        content-type is returned.

        **Example Streaming Response**

        Plain text stream arriving word by word.

        **Example JSON Response**

        ```json
        {
            "status": "success",
            "data": "Response data"
        }
        ```
        """
        try:
            client = UniBotWidgetClient()

            filtered_headers = {}
            for key, value in request.headers.items():
                if key.lower() not in [
                    "host",
                    "cookie",
                    "x-forwarded-for",
                    "x-forwarded-host",
                    "x-forwarded-port",
                    "x-forwarded-proto",
                    "x-csrftoken",
                ]:
                    filtered_headers[key] = value

            backend_response = client.send_widget_request(
                request_data=request.data,
                user=request.user,
                headers=filtered_headers,
            )

            return self.handle_backend_response(backend_response)

        except requests.exceptions.SSLError as e:
            return Response(
                {
                    "error": "SSL error connecting to UniBot backend server",
                    "backend_url": client.base_url,
                    "details": str(e),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except requests.exceptions.ConnectionError as e:
            return Response(
                {
                    "error": "Unable to connect to UniBot backend server",
                    "backend_url": client.base_url,
                    "details": str(e),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except requests.exceptions.Timeout as e:
            return Response(
                {
                    "error": "UniBot backend server timeout",
                    "backend_url": client.base_url,
                    "details": str(e),
                },
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except Exception as e:  # pylint: disable=broad-except
            return Response(
                {
                    "error": f"Proxy error: {str(e)}",
                    "backend_url": getattr(client, "base_url", "unknown"),
                    "error_type": type(e).__name__,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def handle_backend_response(
        self,
        backend_response: requests.Response,
    ) -> Union[StreamingHttpResponse, Response]:
        """
        Handle backend response based on content type.

        Determines if the response is streaming or regular JSON
        and returns appropriate Django response.
        """
        if self.is_streaming_response(backend_response):
            return self.create_streaming_response(backend_response)

        return self.create_json_response(backend_response)

    @staticmethod
    def is_streaming_response(backend_response: requests.Response) -> bool:
        """
        Determine if backend response is streaming based on headers.

        Checks for:
        - text/event-stream content type
        - text/plain with chunked encoding

        Returns False for application/json responses.
        """
        content_type = backend_response.headers.get("Content-Type", "").lower()
        transfer_encoding = backend_response.headers.get(
            "Transfer-Encoding", ""
        ).lower()

        is_streaming = (
            "text/event-stream" in content_type or transfer_encoding == "chunked"
        )

        return is_streaming

    @staticmethod
    def create_streaming_response(
        backend_response: requests.Response,
    ) -> StreamingHttpResponse:
        """
        Create Django StreamingHttpResponse from backend response.

        Streams content chunk by chunk from backend to client.
        """

        def stream_generator():
            """Generate streaming chunks from backend response."""
            for chunk in backend_response.iter_content(
                chunk_size=None, decode_unicode=True
            ):
                if chunk:
                    yield chunk

        streaming_response = StreamingHttpResponse(
            stream_generator(),
            content_type=backend_response.headers.get(
                "Content-Type", "text/plain; charset=utf-8"
            ),
            status=backend_response.status_code,
        )
        streaming_response["Cache-Control"] = "no-cache"
        streaming_response["X-Accel-Buffering"] = "no"

        return streaming_response

    @staticmethod
    def create_json_response(backend_response: requests.Response) -> Response:
        """
        Create Django Response from backend JSON response.

        Attempts to parse JSON, falls back to text if parsing fails.
        """
        try:
            json_data = backend_response.json()
            return Response(json_data, status=backend_response.status_code)
        except ValueError:
            return Response(
                {"data": backend_response.text},
                status=backend_response.status_code,
            )


class WidgetLoaderView(APIView):
    """
    Provide widget loader endpoint.

    Handles loader-specific requests for the widget system.
    Similar to WidgetView but designed for loader operations.
    """

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        """
        Handle widget loader requests.

        **Example Request**

            POST /uni_bot/api/widget/loader/

        Accept payload from frontend for loader-specific operations.
        This endpoint can be customized for different loader requirements.

        For example:

        ```json
        {
            "host": "apps.edx.com",
            "path": "/learning/course/course-v1:course_id/home"
        }
        ```

        **Response Values**

        If the request is successful and the response is streaming,
        an HTTP 200 "OK" with text/plain content-type is returned.

        If the response is JSON, an HTTP 200 "OK" with application/json
        content-type is returned.

        **Example Response**

        ```json
        {
            "verified": true,
            "message": "Service is enabled",
            "product_id": "d70e5a8e-eee7-4a63-be3b-dd8f2055eeda",
            "edx_lms_host": "edx-lab.intela.dev",
            "slug": "course-v1:Intela+CS-47+2025",
            "options": {
                "session_timeout": 15,
                "window_width": "350px",
                "window_height": "700px",
                "window_radius": "16px",
                "offset_right": "32px",
                "offset_bottom": "32px",
                "color_ground": "#FFFFFF",
                "color_accent": "#9640f2",
                "color_canvas": "#f7fAfB",
                "color_border": "#E9E9E9",
                "color_bubble": "#DAE5FC",
                "color_marker": "#F49931",
                "color_text_bright": "#474848",
                "color_text_muted": "rgba(0, 0, 0, 0.50)"
            },
            "position": "right"
        }
        ```
        """
        try:
            client = UniBotWidgetClient()

            backend_response = client.send_loader_request(
                request_data=request.data,
                user=request.user,
            )

            json_data = backend_response.json()

            return Response(json_data, status=backend_response.status_code)

        except requests.exceptions.SSLError as e:
            return Response(
                {
                    "error": "SSL error connecting to UniBot backend server",
                    "backend_url": client.base_url,
                    "details": str(e),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except requests.exceptions.ConnectionError as e:
            return Response(
                {
                    "error": "Unable to connect to UniBot backend server",
                    "backend_url": client.base_url,
                    "details": str(e),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except requests.exceptions.Timeout as e:
            return Response(
                {
                    "error": "UniBot backend server timeout",
                    "backend_url": client.base_url,
                    "details": str(e),
                },
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except Exception as e:  # pylint: disable=broad-except
            return Response(
                {
                    "error": f"Loader proxy error: {str(e)}",
                    "backend_url": getattr(client, "base_url", "unknown"),
                    "error_type": type(e).__name__,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class WidgetStaticView(APIView):
    """
    Provide widget static JavaScript endpoint.

    Proxies static JavaScript file requests to UniBot backend.
    """

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, filename: str) -> HttpResponse:
        """
        Handle static JavaScript file requests.

        **Example Request**

            GET /uni_bot/api/widget/static/{filename}

        Retrieves static JavaScript file from the backend.

        **Parameters**

        - filename: The name of the static file to retrieve

        **Response Values**

        If the request is successful, an HTTP 200 "OK" with
        application/javascript content-type is returned.

        **Example Response**

        JavaScript file content with proper content-type header.
        """
        try:
            client = UniBotWidgetClient()

            backend_response = client.send_static_request(
                user=request.user,
                filename=filename,
            )

            return HttpResponse(
                backend_response.content,
                content_type=backend_response.headers.get(
                    "Content-Type", "application/javascript"
                ),
                status=backend_response.status_code,
            )

        except requests.exceptions.SSLError as e:
            return HttpResponse(
                f"// SSL error connecting to UniBot backend server: {str(e)}",
                content_type="application/javascript",
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except requests.exceptions.ConnectionError as e:
            return HttpResponse(
                f"// Unable to connect to UniBot backend server: {str(e)}",
                content_type="application/javascript",
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except requests.exceptions.Timeout as e:
            return HttpResponse(
                f"// UniBot backend server timeout: {str(e)}",
                content_type="application/javascript",
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except Exception as e:  # pylint: disable=broad-except
            return HttpResponse(
                f"// Proxy error: {str(e)}",
                content_type="application/javascript",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
