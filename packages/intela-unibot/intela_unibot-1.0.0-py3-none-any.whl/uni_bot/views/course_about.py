"""
Module for course about views.
"""
from lms.djangoapps.courseware.views.views import course_about as original_course_about  # pylint: disable=import-error

from uni_bot.decorators import inject_script_inserter_to_response_html_body

course_about = inject_script_inserter_to_response_html_body(original_course_about)
