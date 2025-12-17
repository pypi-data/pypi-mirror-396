"""
Contains unibot-related models.
"""
import datetime
import requests

from config_models.models import ConfigurationModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from jsonfield.fields import JSONField
from opaque_keys.edx.django.models import CourseKeyField

from . import configuration_helpers
from .constants import REQUEST_METHOD_CHOICES
from .utils import parse_support_json, send_to_backend


class CourseMetadata(models.Model):  # pylint: disable=too-few-public-methods
    """
    Persists course metadata.
    """

    course_key = CourseKeyField(db_index=True, primary_key=True, max_length=255)
    last_published = models.DateTimeField(blank=True, verbose_name=_("Last published"))

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        verbose_name = _("Course metadata")
        verbose_name_plural = _("Courses metadata")

    def __str__(self) -> str:
        return f"Course metadata for course {self.course_key}"

    def is_course_structure_outdated(
        self, last_upload_datetime: datetime.datetime
    ) -> bool:
        """
        Checks whether the course structure is outdated.
        """
        return self.last_published >= last_upload_datetime


class UniBotSettingsConfiguration(ConfigurationModel):  # pylint: disable=too-few-public-methods
    """
    Stores the `uni_bot` plugin settings configuration.
    """

    config_values = JSONField(
        null=False, blank=True, default=dict, verbose_name=_("Configuration values")
    )

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        verbose_name = _("UniBot settings configuration")
        verbose_name_plural = _("UniBot settings configurations")


class AreEnabled(models.Model):  # pylint: disable=too-few-public-methods
    """
    A model representing a boolean flag to indicate whether an all courses is enabled.
    """

    are_enabled = models.BooleanField()

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        verbose_name = _("Are Enabled")
        verbose_name_plural = _("Are Enabled")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = configuration_helpers.fetch_unibot_data()
        data["are_enabled"] = self.are_enabled
        send_to_backend(data)


class Appearance(models.Model):  # pylint: disable=too-few-public-methods
    """
    Represents the visual configuration of an application.
    """

    logo_content = models.TextField(default="")
    logo_filename = models.CharField(max_length=255, default="")
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    greeting = models.TextField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    accent_color = models.CharField(max_length=7)
    languages = models.JSONField(default=list, blank=True)
    position = models.CharField(max_length=255, blank=True)

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        verbose_name = _("Appearance")
        verbose_name_plural = _("Appearance")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = configuration_helpers.fetch_unibot_data()
        appearance_data = {
            "logo": {"content": self.logo_content, "filename": self.logo_filename},
            "title": self.title,
            "subtitle": self.subtitle,
            "greeting": self.greeting,
            "width": self.width,
            "height": self.height,
            "accent_color": self.accent_color,
            "languages": self.languages,
            "position": {
                "set": self.position,
                "items": data["appearance"]["position"]["items"],
            },
        }
        data["appearance"] = appearance_data
        send_to_backend(data)


class Support(models.Model):  # pylint: disable=too-few-public-methods
    """
    Represents support configurations for a service.
    """

    email = models.CharField(max_length=1024, default="example@mail.com")
    url = models.CharField(max_length=100, blank=True)
    headers = models.TextField(blank=True)
    method = models.CharField(
        blank=True, max_length=100, choices=REQUEST_METHOD_CHOICES
    )
    provider = models.CharField(max_length=255, blank=True, null=True)

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        verbose_name = _("Support")
        verbose_name_plural = _("Support")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = configuration_helpers.fetch_unibot_data()
        parsed_data = parse_support_json(data)
        provider_choises = (
            parsed_data.get("support").get("items")
            if parsed_data
            else [
                ("CONFIGUR YOUR API KEY", "CONFIGUR YOUR API KEY"),
            ]
        )
        data["support"] = {
            "email": self.email,
            "webhook": {
                "url": self.url,
                "method": self.method,
                "headers": self.headers,
                "system": {
                    "set": self.provider,
                    "items": [
                        {"code": provider[0], "name": provider[1]}
                        for provider in provider_choises
                    ],
                },
            },
        }
        send_to_backend(data)


class LLMVendors(models.Model):  # pylint: disable=too-few-public-methods
    """
    A model to store API credentials and configuration details for different
    large language model (LLM) vendors such as WatsonX, Ollama, and OpenAI.
    """

    watsonx_api_key = models.CharField(max_length=255, default="", blank=True)
    watsonx_url = models.URLField(blank=True, default="")
    watsonx_project_id = models.CharField(max_length=255, blank=True, default="")
    ollama_api_key = models.CharField(max_length=255, default="", blank=True)
    ollama_url = models.URLField(blank=True, default="")
    openai_api_key = models.CharField(max_length=255, default="", blank=True)

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        verbose_name = _("LLM Vendor")
        verbose_name_plural = _("LLM Vendors")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = configuration_helpers.fetch_unibot_data()
        data["llm_vendors"] = {
            "watsonx": {
                "api_key": self.watsonx_api_key,
                "url": self.watsonx_url,
                "project_id": self.watsonx_project_id,
            },
            "ollama": {"api_key": self.ollama_api_key, "url": self.ollama_url},
            "openai": {"api_key": self.openai_api_key},
        }
        send_to_backend(data)


class LLMPreset(models.Model):  # pylint: disable=too-few-public-methods
    """
    Represents a preset configuration for an LLM in the system.
    """

    selected_preset_code = models.CharField(max_length=255, blank=True, null=True)

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        verbose_name = _("LLM Preset")
        verbose_name_plural = _("LLM Presets")

    def __str__(self) -> str:
        return str(self.selected_preset_code)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = configuration_helpers.fetch_unibot_data()
        data["llm_presets"]["set"] = self.selected_preset_code
        send_to_backend(data)


class Restriction(models.Model):  # pylint: disable=too-few-public-methods
    """
    Represents restrictions for course components.
    """

    graded = models.BooleanField()
    non_graded = models.BooleanField()

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        verbose_name = _("Restriction")
        verbose_name_plural = _("Restrictions")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = configuration_helpers.fetch_unibot_data()
        data["restrict"] = {"graded": self.graded, "non_graded": self.non_graded}
        send_to_backend(data)


class AdditionalContext(models.Model):  # pylint: disable=too-few-public-methods
    """
    Represents additional global context in the platform.
    """

    file = models.FileField(upload_to="markdown_files/")  # pylint: disable=no-member

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        verbose_name = _("Additional Context")
        verbose_name_plural = _("Additional Context")

    def save(self, *args, **kwargs):
        # Check if the instance already exists in the database
        if self.pk:
            old_instance = AdditionalContext.objects.filter(pk=self.pk).first()  # pylint: disable=no-member
            if old_instance and old_instance.file != self.file:
                # Remove the old file
                old_instance.file.delete(save=False)  # pylint: disable=no-member
        super().save(*args, **kwargs)
        api_url = configuration_helpers.get_unibot_base_url()

        headers = configuration_helpers.get_api_headers()

        filename = str(self.file.name).rsplit('/', maxsplit=1)[-1]

        with open(self.file.path, "rb") as file:  # pylint: disable=no-member
            files = {
                "file": (filename, file, "multipart/form-data"),
            }

            requests.post(api_url, headers=headers, files=files, timeout=30)

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)  # pylint: disable=no-member
        super().delete(*args, **kwargs)
