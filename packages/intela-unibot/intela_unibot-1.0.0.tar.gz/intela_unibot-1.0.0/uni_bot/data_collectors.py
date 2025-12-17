"""
Provides entities that collects data from data sources.
"""
from abc import ABC, abstractmethod
from base64 import b64encode
from collections import ChainMap
from pathlib import Path
from typing import Any, Callable, ChainMap as ChainMapType, Dict, List, Optional, Tuple, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from edxval.models import VideoTranscript
from opaque_keys.edx.keys import CourseKey, UsageKey
from xblock.core import XBlock
from xblock.fields import Scope

# pylint: disable=import-error
from openedx.core.djangoapps.models.course_details import CourseDetails
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from xmodule.course_block import CourseBlock
from xmodule.modulestore.django import modulestore
from xmodule.seq_block import SectionBlock

from uni_bot import configuration_helpers
from uni_bot.serializers import VideoTranscriptSerializer
from uni_bot.utils import (
    create_directory_zip,
    get_block_ancestors,
    get_block_fields_content,
    get_not_container_descendants,
    get_user_course_role_name,
)


User = get_user_model()


# pylint: disable=too-few-public-methods
class BaseDataCollector(ABC):
    """
    The abstract base class for data collection.
    """

    @abstractmethod
    def collect(self, *args, **kwargs) -> Any:
        """
        Provide the collected data.
        """


# pylint: disable=too-few-public-methods
class CourseDataCollector(BaseDataCollector):
    """
    Collect course data.

    The provided data is in the format
    ```
    {
        "course_id": "course-v1:OpenedX+DemoX+DemoCourse",
        "course_name": "Math",
        "content": [
            {
                "section_id": "block-v1:OpenedX+DemoX+DemoCourse+type@chapter+block@f3aa2011b3c948f68eb03c5be0ffbde1",
                "section_name": "Integrals",
                "content": [
                    {
                        "block_id": "block-v1:OpenedX+DemoX+DemoCourse+type@video+block@4d982badf99d4c7ca77d2cf917ef806f",  # noqa, pylint: disable=line-too-long
                        "fields": {
                            "display_name": "What is an integral?",
                            "youtube_id_1_0": "7_yD_cEfoCk",
                        },
                        "breadcrumbs": "Math / Integrals / Integrals Introduction / First steps with integrals",
                        "unit_id": "block-v1:OpenedX+DemoX+DemoCourse+type@vertical+block@9d9334cce44c4c56bfe5b9ceff7ac780"  # noqa, pylint: disable=line-too-long
                    }
                ]
            },
            {
                "section_id": "block-v1:OpenedX+DemoX+DemoCourse+type@chapter+block@68aa2011c3c948868eb03c5be5babee7",
                "section_name": "Logarithms",
                "content": [
                    {
                        "block_id": "block-v1:OpenedX+DemoX+DemoCourse+type@html+block@b452a2391d8842858d78a029b43e1da5",  # noqa, pylint: disable=line-too-long
                        "fields": {
                            "display_name": "Logarithms concepts",
                            "data": "<div>A lot of theory</div>",
                        },
                        "breadcrumbs": "Math / Logarithms / Logarithms Introduction / First steps with logarithms",
                        "unit_id": "block-v1:OpenedX+DemoX+DemoCourse+type@vertical+block@2089c5c0bb9748fc9c675a3052152593"  # noqa, pylint: disable=line-too-long
                    }
                ]
            }
        ],
        "metadata": {
            "overview": "Welcome to the Open edX Demo Course!",
            "start_date": "2020-01-06T00:00:00Z"
        }
    }
    ```
    """

    # pylint:disable=arguments-differ
    def collect(self, data_source: CourseBlock, *args, **kwargs) -> Dict[str, Union[str, dict]]:
        course_content = [self._collect_section_data(section) for section in data_source.get_children()]

        return {
            'course_id': str(data_source.id),
            'course_name': data_source.display_name,
            'content': course_content,
            'metadata': CourseDetails.populate(data_source),
        }

    def _collect_section_data(self, section: SectionBlock) -> Dict[str, Union[str, dict]]:
        """
        Provide a course section data.
        """
        not_container_section_descendants = get_not_container_descendants(section)
        section_content = [self._collect_block_data(block) for block in not_container_section_descendants]

        return {
            'section_id': str(section.location),
            'section_name': section.display_name,
            'content': section_content,
        }

    def _collect_block_data(self, block: XBlock) -> Dict[str, Union[str, dict]]:
        """
        Provide a course block data.
        """
        block_fields_content = get_block_fields_content(block, (Scope.content, Scope.settings))

        block_ancestors = get_block_ancestors(block)

        breadcrumbs = ' / '.join([ancestor.display_name for ancestor in block_ancestors])
        ancestor_unit = next(ancestor for ancestor in block_ancestors if ancestor.location.block_type == 'vertical')

        block_specific_data = self._collect_block_specific_data(block)

        return {
            'block_id': str(block.location),
            'fields': block_fields_content,
            'breadcrumbs': breadcrumbs,
            'unit_id': str(ancestor_unit.location),
            **block_specific_data,
        }

    def _collect_block_specific_data(self, block: XBlock) -> Dict[str, Optional[Union[List[Dict[str, str]], str]]]:
        """
        Provide the data specific for the block type.
        """
        block_specific_data_collector = {
            'video': self._collect_video_specific_data,
            'scorm': self._collect_scorm_specific_data,
        }
        block_type = block.location.block_type

        return block_specific_data_collector.get(block_type, lambda _block: {})(block)

    def _collect_video_specific_data(self, block: XBlock) -> Dict[str, List[Dict[str, str]]]:
        """
        Provide the data specific for the video block.
        """
        return {'transcripts': self._collect_video_transcripts(block)}

    @staticmethod
    def _collect_video_transcripts(block: XBlock) -> List[Dict[str, str]]:
        """
        Provide the video transcript data.
        """
        if edx_video_id := block.edx_video_id:
            # pylint: disable=no-member
            video_transcripts = VideoTranscript.objects.filter(video__edx_video_id=edx_video_id)

            return VideoTranscriptSerializer(video_transcripts, many=True).data
        return []

    def _collect_scorm_specific_data(self, block: XBlock) -> Dict[str, Optional[str]]:
        """
        Provide the data specific for the scorm block.
        """
        scorm_specific_data = {}

        if configuration_helpers.include_file_content_during_data_collection():
            scorm_specific_data['file'] = self._collect_scorm_file_data(block)

        return scorm_specific_data

    @staticmethod
    def _collect_scorm_file_data(block: XBlock) -> Optional[str]:
        """
        Provide base64-encoded scorm file.
        """
        if not block.index_page_path:
            return None

        file_path = Path(block.extract_folder_path)
        scorm_zip = create_directory_zip(file_path, block.storage)
        scorm_zip_content = scorm_zip.getvalue()
        b64_encoded_scorm_zip_content = b64encode(scorm_zip_content).decode('utf-8')

        return b64_encoded_scorm_zip_content


class UserCourseLocationDataCollector(BaseDataCollector):
    """
    Collect the data about a user location inside the course.

    The provided data is in the format
    ```
    {
        "user_nickname": "john_doe_24",
        "user_fullname": "John Doe",
        "user_email": "jd@example.com",
        "user_role": "instructor",
        "portal_name": "Intela",
        "portal_host": "lms.edx.intela.com",
        "course_id": "course-v1:Math+IT+M_7",
        "course_name": "Introduction to Mathematical Thinking",
        "section_id": "block-v1:Math+IT+M_7+type@chapter+block@f1f009f328764904a1ac4ff2f3082ce4",
        "section_name": "Boolean algebra",
        "subsection_id": "block-v1:Math+IT+M_7+type@sequential+block@4b0c200c078849b39ecf49378813327d",
        "subsection_name": "Laws of Boolean Algebra",
        "unit_id": "block-v1:RG+RG_IM2+6+type@vertical+block@4dce11f5e3dc4a09a19dbb7e636b6c89",
        "unit_name": "Distributive Law"
    }
    ```
    """

    # pylint:disable=arguments-differ
    def collect(
        self,
        user: User,
        raw_course_location_data: Dict[str, str],
        *args,
        **kwargs,
    ) -> ChainMapType[str, Optional[str]]:
        return ChainMap(
            self._collect_course_location_data(raw_course_location_data),
            self._collect_portal_data(),
            self._collect_user_data(user, raw_course_location_data['course_id']),
        )

    def _collect_course_location_data(self, raw_course_location_data: Dict[str, str]) -> ChainMap[str, Optional[str]]:
        """
        Collect the data about course location structure blocks.
        """
        return ChainMap(*(
            data_collector(raw_course_location_data)
            for data_collector in self._course_location_data_collectors
        ))

    @property
    def _course_location_data_collectors(self) -> Tuple[Callable[[Dict[str, str]], Dict[str, Optional[str]]], ...]:
        """
        Provide the course location structure blocks data collectors.
        """
        return (
            self._collect_course_data,
            self._collect_chapter_data,
            self._collect_sequential_data,
            self._collect_vertical_data,
        )

    @staticmethod
    def _collect_course_data(raw_course_location_data: Dict[str, str]) -> Dict[str, str]:
        """
        Collect location data about the course block itself.
        """
        course_id = raw_course_location_data['course_id']
        course_key = CourseKey.from_string(course_id)
        course = modulestore().get_course(course_key)

        return {
            'course_id': course_id,
            'course_name': course.display_name,
        }

    @staticmethod
    def _collect_chapter_data(raw_course_location_data: Dict[str, str]) -> Dict[str, Optional[str]]:
        """
        Collect location data about the chapter block.
        """
        chapter_data = {'section_id': None, 'section_name': None}

        if sequential_id := raw_course_location_data.get('sequential_key_string'):
            sequential_key = UsageKey.from_string(sequential_id)
            sequential = modulestore().get_item(sequential_key)
            chapter = sequential.get_parent()

            chapter_data.update({'section_id': str(chapter.location), 'section_name': chapter.display_name})

        return chapter_data

    @staticmethod
    def _collect_sequential_data(raw_course_location_data: Dict[str, str]) -> Dict[str, Optional[str]]:
        """
        Collect location data about the sequential block.
        """
        sequential_data = {'subsection_id': None, 'subsection_name': None}

        if sequential_id := raw_course_location_data.get('sequential_key_string'):
            sequential_key = UsageKey.from_string(sequential_id)
            sequential = modulestore().get_item(sequential_key)

            sequential_data.update({'subsection_id': sequential_id, 'subsection_name': sequential.display_name})

        return sequential_data

    @staticmethod
    def _collect_vertical_data(raw_course_location_data: Dict[str, str]) -> Dict[str, Optional[str]]:
        """
        Collect location data about the vertical block.
        """
        vertical_data = {'unit_id': None, 'unit_name': None}

        if vertical_id := raw_course_location_data.get('vertical_key_string'):
            vertical_key = UsageKey.from_string(vertical_id)
            vertical = modulestore().get_item(vertical_key)

            vertical_data.update({'unit_id': vertical_id, 'unit_name': vertical.display_name})

        return vertical_data

    @staticmethod
    def _collect_portal_data() -> Dict[str, str]:
        """
        Collect platform-related data.
        """
        return {
            'portal_name': configuration_helpers.get_value('platform_name', settings.PLATFORM_NAME),
            'portal_host': configuration_helpers.get_value('LMS_BASE', settings.LMS_BASE),
        }

    @staticmethod
    def _collect_user_data(user: User, course_id: str) -> Dict[str, str]:
        """
        Collect information about a user.
        """
        return {
            'user_nickname': user.username,
            'user_fullname': user.profile.name,
            'user_email': user.email,
            'user_role': get_user_course_role_name(user.id, course_id),
        }
