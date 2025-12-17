import re
from typing import Literal

from pydantic import Field, field_validator, model_validator

from ..utils import Utils
from .base_model import BaseFieldComponent

HEX_COLOR_REGEX = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")


class PageMetadata(BaseFieldComponent):
    show_submit_button: bool = Field(
        default=True, description="Show submit button of the page"
    )
    previous_button_text: str = Field(
        default="Previous", description="Previous button text of the page"
    )
    next_button_text: str = Field(
        default="Next", description="Next button text of the page"
    )


class ExternalStatusDefinition(BaseFieldComponent):
    name: str = Field(..., min_length=1, description="Name of the status")
    color: str = Field(
        ..., min_length=1, description="Color of the status in hex format"
    )

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not HEX_COLOR_REGEX.match(v):
            raise ValueError(
                "Status color must be a valid hex code (e.g. #000000 or #FFF)"
            )
        return v


class FilterField(BaseFieldComponent):
    key: str = Field(
        min_length=1, description="Filter key field name, Example: 'field_name'"
    )
    value: str = Field(description="Filter value, Example: 'value'")

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str | None:
        return Utils.non_empty_string_validator(v, "Filter key")


class ExternalSectionDetails(BaseFieldComponent):
    name: str = Field(description="Name of the section")
    description: str | None = Field(
        default=None, description="Description of the section"
    )
    add_section_text: str = Field(
        "Add another Section", description="Text to display for add section button"
    )
    add_section_text_position: Literal["right", "left", "center"] = Field(
        "right",
        description="Position of the add section button, allowed values: right, left, center",
    )
    display_condition: str | None = Field(
        None,
        description="Display condition for the section, supports multiple arithmetic operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, ...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations (TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. Example: {field_name} <> 'value' or {field_name} > 10",
    )
    allow_copy: bool = Field(False, description="Allow copying of the section")
    allow_edit_copy_after_submission: bool = Field(
        True, description="Allow editing and copying of the section after submission"
    )
    allow_edit_copy_after_submission_condition: str | None = Field(
        None,
        description="Display condition for the allow edit copy after submission, supports multiple arithmetic operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, ...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations (TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. Example: {field_name} <> 'value' or {field_name} > 10",
    )
    max_number_of_copies: str | None = Field(
        None,
        description="Maximum number of copies allowed, can be a number or '{numberOfCopies}'",
    )
    child_section_indices: list[int] = Field(
        default_factory=list, description="Array of child section indices"
    )
    unique_field_names: list[str] = Field(
        default_factory=list,
        description="Array of unique field names, only when the copy is allowed, Example: ['field1', 'field2']",
    )
    retain_values: bool = Field(False, description="Retain values when hidden")
    keep_section_collapsed: bool = Field(False, description="Keep section collapsed")
    section_type: Literal["section", "table"] = Field(
        "section", description="Type of the section"
    )
    initial_rows: int = Field(5, description="Initial number of rows")


class ExternalSectionDefinition(BaseFieldComponent):
    section_details: ExternalSectionDetails = Field(
        description="Section details of the section"
    )
    # field_definitions: List[Any] = Field([], description="Field definitions of the section") # TODO: Handle the fields adding in the future, current issue is that its client wont able to generated payload for fields


class ExternalPageMetadata(BaseFieldComponent):
    show_submit_button: bool = Field(
        default=True, description="Show submit button of the page"
    )
    prev_button_text: str = Field(
        default="Previous", description="Previous button text of the page"
    )
    next_button_text: str = Field(
        default="Next", description="Next button text of the page"
    )


class ExternalPageDefinition(BaseFieldComponent):
    page_details: ExternalPageMetadata = Field(description="Page details of the page")
    sections: list[ExternalSectionDefinition] = Field(
        [], description="Sections of the page"
    )


class BaseActionDetails(BaseFieldComponent):
    action_type: Literal["timer", "openClappiaApp", "openLink", "code"] = Field(
        default="openClappiaApp", description="Type of action"
    )


class TimerActionDetails(BaseActionDetails):
    action_type: Literal["timer"] = Field(default="timer", description="Type of action")
    wait_for_seconds: int | None = Field(
        None,
        description="Duration to wait for in seconds. Can include field references. Example: '5000', '7200', '86400' or '{no_of_seconds}'",
    )
    post_stop_action: Literal["autoSubmit", "invalidateForm", "none"] | None = Field(
        None, alias="postStopAction", description="Action to perform after timer stops"
    )
    wait_till_date: str | None = Field(
        None,
        description="Date to wait until (when using wait_till_date and wait_till_time)."
        "Can include field references. Example: '2024-12-31' or '{targetDateField}'",
    )
    wait_till_time: str | None = Field(
        None,
        alias="waitTillTime",
        description="Time to wait until (when using wait_till_date and wait_till_time)."
        "Can include field references. Example: '14:30' or '{targetTimeField}'",
    )

    @model_validator(mode="after")
    def validate_wait_requirements(self) -> "TimerActionDetails":
        if not self.wait_for_seconds and (
            not self.wait_till_time or not self.wait_till_date
        ):
            raise ValueError(
                "Either wait_for_seconds or both wait_till_date and wait_till_time are required"
            )
        return self


class OpenClappiaAppActionDetails(BaseActionDetails):
    action_type: Literal["openClappiaApp"] = Field(
        default="openClappiaApp", description="Type of action"
    )
    app_id: str = Field(description="ID of the app to open")
    view_type: Literal["home", "submissions", "analytics"] = Field(
        default="home",
        description="Type of view which should be opened when the action is triggered",
    )
    navigation_field_name: str | None = Field(
        default=None,
        description="Field name to navigate to, Example: 'field_name'",
    )


class OpenLinkActionDetails(BaseActionDetails):
    action_type: Literal["openLink"] = Field(
        default="openLink", description="Type of action"
    )
    redirect_link: str = Field(description="URL to redirect to")


class CodeActionDetails(BaseActionDetails):
    action_type: Literal["code"] = Field(default="code", description="Type of action")
    code: str = Field(description="Code to execute")
    output_fields: list[str] | None = Field(
        default=None, description="List of output field names"
    )


ActionDetails = (
    TimerActionDetails
    | OpenClappiaAppActionDetails
    | OpenLinkActionDetails
    | CodeActionDetails
)


class ExternalTemplateDefinition(BaseFieldComponent):
    template_name: str = Field(description="Template name, Example: 'Template 1'")
    pdf_name: str | None = Field(
        default="{$app_id}_{$submission_id}.pdf",
        description="PDF name, can contain field references. Example: '{$app_id}_{$submission_id}.pdf'",
    )
    print_mode: Literal["portrait", "landscape"] = Field(
        default="portrait", description="Print mode"
    )
    file_type: Literal["pdf", "xlsx"] = Field(
        default="pdf", description="File type, allowed values: pdf, xlsx"
    )
