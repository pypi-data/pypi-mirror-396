"""
Uni Bot plugin serializers.
"""
from base64 import b64encode
from pathlib import Path

from edxval.models import VideoTranscript
from rest_framework import serializers

from uni_bot import configuration_helpers


class VideoTranscriptSerializer(serializers.ModelSerializer):
    """
    Serialize VideoTranscript model data.
    """

    filename = serializers.SerializerMethodField()

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        model = VideoTranscript
        fields = ('language_code', 'file_format', 'filename')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if configuration_helpers.include_file_content_during_data_collection():
            self.fields['transcript'] = serializers.SerializerMethodField()

    def get_transcript(self, video_transcript: VideoTranscript) -> str:
        """
        Provide base64-encoded transcript file.
        """
        file_content = video_transcript.transcript.open().file.file.read()
        return b64encode(file_content).decode('utf-8')

    def get_filename(self, video_transcript: VideoTranscript) -> str:
        """
        Provide the transcript file name.
        """
        return Path(video_transcript.transcript.name).name
