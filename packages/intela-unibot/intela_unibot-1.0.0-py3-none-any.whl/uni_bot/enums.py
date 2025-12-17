"""
Contains enumerations.
"""
from enum import Enum

from typing import Tuple

from django.conf import settings

from uni_bot import configuration_helpers


class BotStatus(str, Enum):
    """

    Enumerate bot statuses.
    """

    DEACTIVATED = 'deactivated'
    IN_TRAINING = 'in_training'
    ACTIVE = 'active'


class BotReadinessStatus(str, Enum):
    """
    Enumerate bot readiness statuses.
    """

    READY = 'ready'
    NOT_READY = 'not_ready'


class UnibotInstructorWidgetDisplayingMode(str, Enum):
    """
    Enumerate unibot instructor widget displaying modes.
    """

    CUSTOM_WIDGET_IN_SEPARATE_TAB = 'custom_widget_in_separate_tab'
    EMBEDDED_WIDGET_IN_SEPARATE_TAB = 'embedded_widget_in_separate_tab'
    EMBEDDED_WIDGET_IN_INSTRUCTOR_TAB = 'embedded_widget_in_instructor_tab'

    @classmethod
    def get_widget_in_separate_tab_modes(cls) -> Tuple['UnibotInstructorWidgetDisplayingMode', ...]:
        """
        Provide modes in which the widget is rendered in separate tab.
        """
        return (cls.CUSTOM_WIDGET_IN_SEPARATE_TAB, cls.EMBEDDED_WIDGET_IN_SEPARATE_TAB)

    def is_enabled(self) -> bool:
        """
        Decide whether the mode is enabled.
        """
        unibot_instructor_widget_displaying_mode = configuration_helpers.get_value(
            'UNIBOT_INSTRUCTOR_WIDGET_DISPLAYING_MODE',
            settings.UNIBOT_INSTRUCTOR_WIDGET_DISPLAYING_MODE,
        )
        return self == unibot_instructor_widget_displaying_mode
