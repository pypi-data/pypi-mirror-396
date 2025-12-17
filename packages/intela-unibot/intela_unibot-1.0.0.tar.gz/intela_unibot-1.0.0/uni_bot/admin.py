"""
Django admin integration for the unibot application.
"""

# pylint: disable=no-member,too-few-public-methods,invalid-name

# Standard library imports
import base64
from io import BytesIO

# Django imports
from django import forms
from django.contrib import admin, messages
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.html import format_html

# Third-party imports
from config_models.admin import ConfigurationModelAdmin

# Local imports
from uni_bot import configuration_helpers
from uni_bot.models import (
    CourseMetadata,
    UniBotSettingsConfiguration,
    Support,
    AreEnabled,
    Appearance,
    LLMPreset,
    LLMVendors,
    Restriction,
    AdditionalContext,
)
from uni_bot.utils import parse_support_json, get_disabled_languages


@admin.register(CourseMetadata)
class ExtraCourseSettingsAdmin(admin.ModelAdmin):
    """
    Admin class for managing CourseMetadata in the Django admin interface.
    """

    list_display = ("course_key",)
    search_fields = ("course_key",)


@admin.register(UniBotSettingsConfiguration)
class UniBotSettingsConfigurationAdmin(ConfigurationModelAdmin):
    """
    Manages UniBotSettingsConfiguration in the Django admin interface.
    """

    list_display = ("config_values",)


class DisabledOptionSelect(forms.CheckboxSelectMultiple):
    """
    A custom form widget that extends `CheckboxSelectMultiple` to allow disabling
    specific checkbox options and optionally marking them as checked.
    """

    def __init__(self, *args, **kwargs):
        self.disabled_languages = kwargs.pop("disabled_languages", {})
        super().__init__(*args, **kwargs)

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        normalized_value = str(value)
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        if normalized_value in self.disabled_languages.keys():
            option["attrs"]["disabled"] = "disabled"
            if self.disabled_languages[normalized_value]:
                option["attrs"]["checked"] = "checked"

        return option


class AreEnabledForm(forms.ModelForm):
    """
    A Django ModelForm that initializes field values based on data fetched from an external backend.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        backend_data = configuration_helpers.fetch_unibot_data(param="are_enabled")
        if backend_data:
            for field in backend_data:
                self.initial[field] = backend_data[field]


@admin.register(AreEnabled)
class AreEnabledAdmin(admin.ModelAdmin):
    """
    Admin interface for managing the AreEnabled model.
    """

    form = AreEnabledForm

    def has_add_permission(self, request):
        """Check if adding new AreEnabled objects is allowed."""
        return not AreEnabled.objects.filter().exists()

    def has_delete_permission(self, request, obj=...):
        return True


class SupportForm(forms.ModelForm):
    """
    A Django form that dynamically configures fields and initial data based on backend configuration.
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        backend_data = configuration_helpers.fetch_unibot_data(param="support")
        self.backend_data_available = bool(backend_data)
        if backend_data:
            parsed_data = parse_support_json(backend_data)
            items = (
                backend_data.get("support", {})
                .get("webhook", {})
                .get("system", {})
                .get("items")
            )
            choices = [(item["code"], item["name"]) for item in items]
            self.fields["provider"].widget = forms.Select(choices=choices)
            for field in parsed_data.get("support", {}):
                if field == "items":
                    self.initial["provider"] = parsed_data["support"].get("set")
                else:
                    self.initial[field] = parsed_data["support"].get(field)

            if self.instance and self.instance.provider:
                provider_choices = parsed_data["support"].get("items", [])
                self.fields["provider"].choices = provider_choices
                self.initial["provider"] = parsed_data["support"].get("set")
        else:
            if self.request:
                messages.error(
                    self.request,
                    "Your API Key or UNI bot settings configuration is invalid",
                )
            for field in self._meta.model._meta.get_fields():
                if field.concrete and not field.auto_created:
                    field_name = field.name
                    self.initial[field_name] = "INVALID CONFIGURATION"


@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    """
    Admin interface for managing the Support model.
    """
    form = SupportForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Returns a Form class for use in the admin add/change views.
        """
        FormClass = super().get_form(request, obj, change, **kwargs)

        class SupportFormWithRequest(FormClass):  # pylint: disable=missing-class-docstring
            def __init__(self, *args, **form_kwargs):
                form_kwargs["request"] = request
                super().__init__(*args, **form_kwargs)

        return SupportFormWithRequest

    def has_add_permission(self, request):
        """Check if adding new Support objects is allowed."""
        return not Support.objects.filter().exists()

    def has_delete_permission(self, request, obj=None):
        """Check if deleting Support objects is allowed."""
        return True

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}

        form_instance = self.get_form(request)(request.POST or None)
        if not form_instance.backend_data_available:
            extra_context["show_save_and_add_another"] = False
            extra_context["show_save_and_continue"] = False
            extra_context["show_save"] = False

        return super().changeform_view(
            request, object_id, form_url, extra_context=extra_context
        )


class AppearanceForm(forms.ModelForm):
    """
    This form integrates with the Appearance model to handle the customization of appearance-related settings,
    including uploading a logo file, selecting languages, and configuring positions.

    The form includes:
    - A file upload field for logos with validation and storage as base64-encoded content.
    - A multiple choice field for selecting languages, supporting backend-defined restrictions.
    - Dynamic configuration of position choices and field initializations based on backend-provided data.
    - Validation and cleanup methods to ensure proper handling of language selections and restrictions.

    This class provides methods to clean language inputs and to save the instance with the updated logo
    and other configurations.
    """

    logo_file = forms.FileField(
        required=False,
        label="Upload Logo",
        widget=forms.ClearableFileInput(attrs={"class": "custom-file-input"}),
    )

    languages = forms.MultipleChoiceField(
        choices=[],
        label="Languages",
        required=False,
    )

    class Meta:
        """
        Meta class for AppearanceForm configuration.
        """
        model = Appearance
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        self.backend_data = configuration_helpers.fetch_unibot_data(param="appearance")

        if self.backend_data:
            self.fields["languages"].widget = DisabledOptionSelect(
                disabled_languages=get_disabled_languages(self.backend_data)
            )
            items = (
                self.backend_data.get("appearance", {})
                .get("position", {})
                .get("items", [])
            )
            choices = [(item["code"], item["name"]) for item in items]
            self.fields["position"].widget = forms.Select(choices=choices)
            for field in self.backend_data.get("appearance", {}):
                if field != "logo":
                    self.initial[field] = self.backend_data["appearance"].get(field)
                else:
                    self.initial["logo_content"] = (
                        self.backend_data["appearance"].get(field).get("content")
                    )
                    self.initial["logo_filename"] = (
                        self.backend_data["appearance"].get(field).get("filename")
                    )
                    decoded_logo = base64.b64decode(
                        self.backend_data["appearance"].get(field).get("content")
                    )
                    file_name = (
                        self.backend_data["appearance"].get(field).get("filename")
                    )
                    logo_file = InMemoryUploadedFile(
                        BytesIO(decoded_logo),
                        field_name="logo_file",
                        name=file_name,
                        content_type="application/octet-stream",
                        size=len(decoded_logo),
                        charset=None,
                    )
                    self.initial["logo_file"] = logo_file
                self.initial["position"] = (
                    self.backend_data.get("appearance", {})
                    .get("position", {})
                    .get("set", "")
                )
            if self.instance:
                language_choices = [
                    (lang["iso_639_1"], lang["name"])
                    for lang in self.initial["languages"]
                ]
                self.fields["languages"].choices = language_choices

                selected_languages = [
                    lang["iso_639_1"]
                    for lang in self.initial["languages"]
                    if lang["is_enabled"]
                ]
                self.initial["languages"] = selected_languages
        else:
            if self.request:
                messages.error(
                    self.request,
                    "Your API Key or UNI bot settings configuration is invalid",
                )
            for field in self._meta.model._meta.get_fields():
                if field.concrete and not field.auto_created:
                    field_name = field.name
                    self.initial[field_name] = "INVALID CONFIGURATION"

    def clean_languages(self):
        """
        Clean and validate the languages field data.
        Returns a list of updated language configurations.
        """
        all_languages = self.backend_data["appearance"].get("languages", [])
        selected_languages = self.cleaned_data.get("languages", [])
        selected_languages += [
            language.get("iso_639_1")
            for language in all_languages
            if language.get("restricted") and language.get("is_enabled")
        ]

        updated_languages = [
            {
                "iso_639_1": lang["iso_639_1"],
                "name": lang["name"],
                "restricted": lang["restricted"],
                "is_enabled": lang["iso_639_1"] in selected_languages,
            }
            for lang in all_languages
        ]

        return updated_languages

    def save(self, commit=True):
        instance = super().save(commit=False)
        logo_file = self.cleaned_data.get("logo_file")

        if logo_file:
            # Save file content as base64
            instance.logo_content = base64.b64encode(logo_file.read()).decode()
            instance.logo_filename = logo_file.name

        if commit:
            instance.save()
        return instance


@admin.register(Appearance)
class AppearanceAdmin(admin.ModelAdmin):
    """
    Admin interface for managing the Appearance model.
    """

    form = AppearanceForm
    fields = (
        "logo_file",
        "title",
        "subtitle",
        "greeting",
        "width",
        "height",
        "position",
        "accent_color",
        "languages",
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "accent_color":
            kwargs["widget"] = forms.widgets.TextInput(attrs={"type": "color"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Returns a Form class for use in the admin add/change views.
        """
        FormClass = super().get_form(request, obj, change, **kwargs)

        class AppearanceFormWithRequest(FormClass):  # pylint: disable=missing-class-docstring
            def __init__(self, *args, **form_kwargs):
                form_kwargs["request"] = request
                super().__init__(*args, **form_kwargs)

        return AppearanceFormWithRequest

    def has_add_permission(self, request):
        """Check if adding new Appearance objects is allowed."""
        return not Appearance.objects.filter().exists()

    def has_delete_permission(self, request, obj=None):
        return True


class LLMVendorForm(forms.ModelForm):
    """
    A Django form that dynamically configures LLMVendor related fields and initial data based on backend configuration.
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        backend_data = configuration_helpers.fetch_unibot_data(param="llm_vendors")
        llm_vendors_backend_data = backend_data.get("llm_vendors", {})
        if llm_vendors_backend_data:
            self.initial["watsonx_api_key"] = llm_vendors_backend_data.get(
                "watsonx", {}
            ).get("api_key", "")
            self.initial["watsonx_url"] = llm_vendors_backend_data.get(
                "watsonx", {}
            ).get("url", "")
            self.initial["watsonx_project_id"] = llm_vendors_backend_data.get(
                "watsonx", {}
            ).get("project_id", "")
            self.initial["ollama_api_key"] = llm_vendors_backend_data.get(
                "ollama", {}
            ).get("api_key", "")
            self.initial["ollama_url"] = llm_vendors_backend_data.get("ollama", {}).get(
                "url", ""
            )
            self.initial["openai_api_key"] = llm_vendors_backend_data.get(
                "openai", {}
            ).get("api_key", "")
        else:
            if self.request:
                messages.error(
                    self.request,
                    "Your API Key or UNI bot settings configuration is invalid",
                )
            for field in self._meta.model._meta.get_fields():
                if field.concrete and not field.auto_created:
                    field_name = field.name
                    self.initial[field_name] = "INVALID CONFIGURATION"


@admin.register(LLMVendors)
class LLMVendorAdmin(admin.ModelAdmin):
    """
    Admin interface for managing the LLMVendor model.
    """

    form = LLMVendorForm
    fieldsets = (
        (
            "WatsonX Settings",
            {"fields": ("watsonx_api_key", "watsonx_url", "watsonx_project_id")},
        ),
        ("Ollama Settings", {"fields": ("ollama_api_key", "ollama_url")}),
        ("OpenAI Settings", {"fields": ("openai_api_key",)}),
    )

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Returns a Form class for use in the admin add/change views.
        """
        FormClass = super().get_form(request, obj, change, **kwargs)

        class LLMVendorFormWithRequest(FormClass):  # pylint: disable=missing-class-docstring
            def __init__(self, *args, **form_kwargs):
                form_kwargs["request"] = request
                super().__init__(*args, **form_kwargs)

        return LLMVendorFormWithRequest

    def has_add_permission(self, request):
        """Check if adding new LLMVendors objects is allowed."""
        return not LLMVendors.objects.filter().exists()

    def has_delete_permission(self, request, obj=None):
        return True


class RestrictionForm(forms.ModelForm):
    """
    A Django form that dynamically configures Restriction related fields
    and initial data based on backend configuration.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        backend_data = configuration_helpers.fetch_unibot_data(param="restrict")
        restrict_backend_data = backend_data.get("restrict", {})

        if restrict_backend_data:
            for field in restrict_backend_data:
                self.initial[field] = restrict_backend_data[field]


@admin.register(Restriction)
class RestrictionsAdmin(admin.ModelAdmin):
    """
    Admin interface for managing the Restriction model.
    """

    form = RestrictionForm

    def has_add_permission(self, request):
        """Check if adding new Restriction objects is allowed."""
        return not Restriction.objects.filter().exists()

    def has_delete_permission(self, request, obj=None):
        return True


class LLMPresetForm(forms.ModelForm):
    """
    Form for managing LLM preset configurations.
    Provides a dynamic selection of preset options based on backend data.
    """

    class Meta:  # pylint: disable=missing-class-docstring
        model = LLMPreset
        fields = ["selected_preset_code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        backend_data = configuration_helpers.fetch_unibot_data(param="llm_presets")
        if backend_data:
            items = backend_data.get("llm_presets", {}).get("items", [])
            choices = [(item["code"], item["name"]) for item in items]
            self.fields["selected_preset_code"].widget = forms.Select(choices=choices)
        else:
            self.fields["selected_preset_code"].widget = forms.Select(choices=[])


@admin.register(LLMPreset)
class LLMPresetAdmin(admin.ModelAdmin):
    """
    Admin interface for managing LLM presets.
    Provides functionality to select and configure LLM presets.
    """
    form = LLMPresetForm


class AdditionalContextForm(forms.ModelForm):
    """
    A form for the AdditionalContext model with a single file field.

    This form uses a custom ClearableFileInput widget with drag-and-drop
    styling and accepts files with the markdown extension.
    """

    class Meta:  # pylint: disable=missing-class-docstring
        """
        Meta class for AdditionalContextForm configuration.
        """
        model = AdditionalContext
        fields = ["file"]
        widgets = {
            "file": forms.ClearableFileInput(
                attrs={
                    "class": "drag-drop-upload",
                    "accept": ".md",
                }
            ),
        }


@admin.register(AdditionalContext)
class AdditionalContextAdmin(admin.ModelAdmin):
    """
    Admin interface for managing the AdditionalContext model.
    """

    form = AdditionalContextForm

    fields = ("file", "download_link")
    readonly_fields = ("download_link",)

    def download_link(self, obj):
        """
        Generate a download link for the additional context file.

        Args:
            obj: The AdditionalContext instance

        Returns:
            str: HTML formatted download link or message if no file exists
        """
        if obj.file:
            return format_html(
                '<a class="button" href="{}" download>Download File</a>',
                obj.file.url,
            )
        return "No file available"

    def has_add_permission(self, request):
        """Check if adding new AdditionalContext objects is allowed."""
        return not AdditionalContext.objects.filter().exists()

    download_link.short_description = "Download Link"
