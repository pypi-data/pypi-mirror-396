"""
Contains utility functions.
"""

import io
import json
import zipfile
from pathlib import Path
from typing import List, Optional, Sequence
from urllib.parse import urljoin

import requests

# pylint: disable=import-error
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.storage import Storage, default_storage
from django.http import HttpResponse
# pylint: disable=import-error
from common.djangoapps.student.models import CourseAccessRole
from openedx.core.djangoapps.django_comment_common.models import Role
from xblock.core import XBlock
from xblock.fields import ScopeBase

from uni_bot import configuration_helpers
from uni_bot.constants import CONTAINER_BLOCK_TYPES
from uni_bot.enums import (
    BotReadinessStatus,
    BotStatus,
    UnibotInstructorWidgetDisplayingMode,
)


def get_not_container_descendants(block: XBlock) -> List[XBlock]:
    """
    Provide a block descendants that cannot wrap another blocks.
    """

    not_container_descendants = []
    children = block.get_children()

    for child in children:
        if child.location.block_type in CONTAINER_BLOCK_TYPES:
            not_container_descendants.extend(get_not_container_descendants(child))
        else:
            not_container_descendants.append(child)

    return not_container_descendants


def get_block_ancestors(block: XBlock) -> List[XBlock]:
    """
    Provide a block ancestors in hierarchical order.
    """

    if parent := block.get_parent():
        return [*get_block_ancestors(parent), parent]
    return []


def get_block_fields_content(block: XBlock, scopes: Sequence[ScopeBase]) -> dict:
    """
    Provide the content of the block fields with specific scopes.
    """

    block_fields_content = {}

    for field in block.fields.values():
        if field.scope in scopes:
            try:
                block_fields_content[field.name] = field.read_json(block)
            except TypeError as exception:
                exception_message = (
                    f'JSON field "{field.name}" value is failed for block "{block.location}" is failed with the error: '
                    f'"{exception}".'
                )
                raise TypeError(exception_message) from exception
    return block_fields_content


def define_bot_status(
    bot_readiness_status: str,
    is_bot_disabled: bool,
    is_course_structure_outdated: bool,
) -> BotStatus:
    """
    Define a bot status.
    """
    if bot_readiness_status == BotReadinessStatus.NOT_READY:
        bot_status = BotStatus.DEACTIVATED
    elif is_bot_disabled or is_course_structure_outdated:
        bot_status = BotStatus.IN_TRAINING
    else:
        bot_status = BotStatus.ACTIVE

    return bot_status


def get_user_course_role_name(user_id: int, course_id: str) -> Optional[str]:
    """
    Provide the name of the user role on the course.
    """
    if course_access_role_name := (
        CourseAccessRole.objects.filter(course_id=course_id, user__id=user_id)
        .values_list("role", flat=True)
        .first()
    ):
        return course_access_role_name
    return (
        Role.objects.filter(course_id=course_id, users__id=user_id)
        .values_list("name", flat=True)
        .first()
    )


def zip_directory_content(
    directory_path: Path,
    zip_file: zipfile.ZipFile,
    base_archive_path: Path = Path(""),
    storage: Storage = default_storage,
) -> None:
    """
    Recursively add files and directories to a ZIP file.
    """
    directory_names, filenames = storage.listdir(directory_path)

    for filename in filenames:
        directory_file_path = directory_path / filename
        with storage.open(directory_file_path, "rb") as file:
            archive_file_path = base_archive_path / filename

            zip_file.writestr(str(archive_file_path), file.read())

    for directory_name in directory_names:
        subdirectory_path = directory_path / directory_name
        subdirectory_archive_path = base_archive_path / directory_name

        zip_directory_content(
            subdirectory_path,
            zip_file,
            base_archive_path=subdirectory_archive_path,
            storage=storage,
        )


def create_directory_zip(
    directory_path: Path, storage: Storage = default_storage
) -> io.BytesIO:
    """
    Create a ZIP archive of a directory and its subfolders from Django storage.
    """
    in_memory_zip = io.BytesIO()

    with zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_directory_content(directory_path, zip_file, storage=storage)

    in_memory_zip.seek(0)

    return in_memory_zip


def parse_support_json(data: json):
    """
    Parses support-related data from a JSON object and structures it into a specific format.
    """
    parsed_data = {
        "support": {
            "email": data["support"].get("email", ""),
            "url": data["support"]["webhook"].get("url", ""),
            "method": data["support"]["webhook"].get("method", ""),
            "headers": data["support"]["webhook"].get("headers", ""),
            "set": data["support"]["webhook"]["system"].get("set", ""),
            "items": [
                (item.get("code", ""), item.get("name", ""))
                for item in data["support"]["webhook"]["system"].get("items", [])
            ],
        }
    }
    return parsed_data


def send_to_backend(data: json):
    """
    Sends data to a backend API via an HTTP PUT request.
    """
    try:
        base_url = configuration_helpers.get_unibot_base_url()
        api_url = urljoin(base_url, settings.UNIBOT_GLOBAL_SETTINGS_ENDPOINT)
        response = requests.put(
            api_url,
            data=json.dumps(data, indent=2),
            headers=configuration_helpers.get_api_headers(),
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as request_error:
        print(f"Failed to send data to backend: {request_error}")


def get_disabled_languages(backend_data: dict):
    """
    Retrieves a list of disabled languages from the backend API.
    """
    languages = backend_data.get("appearance").get("languages")
    disabled_laguages = {
        language["iso_639_1"]: language["is_enabled"]
        for language in languages
        if language["restricted"]
    }
    return dict(disabled_laguages)


def append_script_to_response_html_body(
    response: HttpResponse, script_content: str
) -> None:
    """
    Alter the response content by adding the script to the end of HTML body.
    """
    response_content = response.content.decode("utf-8")
    soup = BeautifulSoup(response_content)

    script_tag = soup.new_tag("script")
    script_tag.string = script_content

    soup.body.append(script_tag)
    response.content = soup.prettify().encode("utf-8")


def is_enabled_instructor_widget_displaying_mode_in(
    plugin_modes: Sequence[UnibotInstructorWidgetDisplayingMode],
) -> bool:
    """
    Decide whether the enabled widget mode in the provided modes.
    """
    return any(mode.is_enabled() for mode in plugin_modes)
