"""
Module for tab fragment.
"""
from typing import Dict

from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic import TemplateView
from opaque_keys.edx.keys import CourseKey

# pylint: disable=import-error
from lms.djangoapps.courseware.courses import get_course_by_id
from xmodule.course_block import CourseBlock

from uni_bot.tab import UniBotDashboardTab


class UniBotTabView(TemplateView):
    """
    Render the UniBot board tab page.
    """

    template_name = 'uni_tab/unibot_tab.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.course = None

    # pylint: disable=arguments-differ
    def get(self, request: HttpRequest, course_id: str, *args, **kwargs) -> HttpResponse:
        course_key = CourseKey.from_string(course_id)
        self.course = get_course_by_id(course_key, depth=0)

        if not UniBotDashboardTab.is_enabled(self.course, request.user):
            raise Http404

        return super().get(request, course_id=course_id, *args, **kwargs)

    def get_context_data(self, **kwargs) -> Dict[str, CourseBlock]:
        return {'course': self.course}
