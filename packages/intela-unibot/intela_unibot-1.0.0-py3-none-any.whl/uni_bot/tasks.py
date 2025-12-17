"""
Provides bot-related Celery tasks.
"""
import logging

import requests
from celery import shared_task

from uni_bot.api.client import UniBotCourseContextClient

logger = logging.getLogger(__name__)


@shared_task(
    autoretry_for=(requests.exceptions.RequestException,),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
)
def notify_bot_about_created_course(course_id: str) -> None:
    """
    Notify the bot about a course creation.
    """
    signal_data = {'course_id': course_id}

    response = UniBotCourseContextClient().send_course_creation_signal(course_id, signal_data)

    try:
        response.raise_for_status()
        logger.info('A signal about course %s creation is successfully sent to the bot.', course_id)
    except requests.exceptions.HTTPError:
        message = response.content.decode('utf-8')
        logger.info('Failed to send a signal about course %s creation to the bot: "%s".', course_id, message)
