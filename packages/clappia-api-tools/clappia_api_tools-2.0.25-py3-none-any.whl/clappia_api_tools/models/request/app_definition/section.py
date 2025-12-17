from typing import Literal

from pydantic import Field

from ...base_model import BaseFieldComponent


class UpsertSectionRequest(BaseFieldComponent):
    name: str = Field(description="Name of the section")
    description: str | None = Field(None, description="Description of the section")
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
        description="Array of unique field names, only when the copy is allowed",
    )
    retain_values: bool = Field(False, description="Retain values when hidden")
    keep_section_collapsed: bool = Field(False, description="Keep section collapsed")
    section_type: Literal["section", "table"] = Field(
        "section", description="Type of the section"
    )
    initial_rows: int = Field(5, description="Initial number of rows")
