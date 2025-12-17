"""
Helper functions for Django views.
"""
import json

from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers  # pylint: disable=import-error


def render_script_inserter_for_user(user: User) -> str:
    """
    Render the external script inserter template for the given user.
    """
    mfe_config = configuration_helpers.get_value('MFE_CONFIG', settings.MFE_CONFIG)
    external_scripts = mfe_config.get('EXTERNAL_SCRIPTS', [])

    context = {
        'external_scripts': json.dumps(external_scripts),
        'is_user_authenticated': user.is_authenticated,
    }

    return render_to_string('uni_bot/script_inserter.js', context)
