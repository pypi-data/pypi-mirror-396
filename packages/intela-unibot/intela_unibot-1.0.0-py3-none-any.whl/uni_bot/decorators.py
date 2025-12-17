"""
Contain plugin-wide decorators.
"""
import functools
from http import HTTPStatus
from typing import Callable

from django.http import HttpRequest, HttpResponse

from uni_bot.utils import append_script_to_response_html_body
from uni_bot.views.helpers import render_script_inserter_for_user


def inject_script_inserter_to_response_html_body(view_func: Callable) -> Callable:
    """
    Append script inserter to the successful response html body.
    """

    @functools.wraps(view_func)
    def inner(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        response = view_func(request, *args, **kwargs)

        if response.status_code == HTTPStatus.OK:
            script_inserter_content = render_script_inserter_for_user(request.user)

            append_script_to_response_html_body(response, script_inserter_content)

        return response

    return inner
