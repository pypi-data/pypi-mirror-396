"""
Provides signal handlers.
"""
import datetime

from django.dispatch import receiver
from openedx_events.content_authoring.signals import COURSE_CREATED, XBLOCK_PUBLISHED

from uni_bot.constants import PUBLISHABLE_COURSE_STRUCTURE_BLOCK_TYPES
from uni_bot.models import CourseMetadata
from uni_bot.tasks import notify_bot_about_created_course as notify_bot_about_created_course_task


@receiver(XBLOCK_PUBLISHED)
def update_course_content_publishing_time(**kwargs) -> None:
    """
    Save current timestamp as course last publishing time.
    """
    xblock_info = kwargs['xblock_info']

    if xblock_info.block_type in PUBLISHABLE_COURSE_STRUCTURE_BLOCK_TYPES:
        course_key = xblock_info.usage_key.course_key
        current_utc_timestamp_iso_format = datetime.datetime.now(datetime.timezone.utc).isoformat()

        CourseMetadata.objects.update_or_create(  # pylint: disable=no-member
            course_key=course_key,
            defaults={'last_published': current_utc_timestamp_iso_format},
        )


@receiver(COURSE_CREATED)
def notify_bot_about_created_course(**kwargs) -> None:
    """
    Catch course creation and runs task to notify a bot about it.
    """
    course_key = kwargs['course'].course_key
    notify_bot_about_created_course_task.delay(str(course_key))
