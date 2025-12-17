import json
import re
from typing import Literal

from pydantic import (
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from ....utils import Utils
from ...base_model import BaseFieldComponent
from ...definition import (
    ActionDetails,
    FilterField,
)
from ...resapi_output import RestApiOutputField
from ...sort_field import SortField


class BaseUpsertFieldRequest(BaseFieldComponent):
    label: str = Field(description="Display label for the field")
    new_field_name: str | None = Field(
        None,
        description="New field variable name for the field, mandatory if field name needs to be changed",
    )
    description: str | None = Field(
        None,
        description="Field description, Example: This is a description for the field",
    )
    placeholder: str | None = Field(default=None, description="Field placeholder")
    dependency_app_id: str | None = Field(
        None, description="Dependency app ID, must be a valid Clappia app ID"
    )
    server_url: str | None = Field(
        None, description="Server URL, mandatory if field type is getDataFromRestApis"
    )
    display_condition: str | None = Field(
        None,
        description=(
            "Display condition Example: {field_name} == 'value'. Clappia supports multiple "
            "arithmetic operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, "
            "AND, OR, XOR, ...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME "
            "operations (TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. "
            "Example: '=SUM({field_name1,field_name2}) + IF({field_name3}>10, 'Yes', 'No')'"
        ),
    )
    required: bool = Field(default=False, description="Whether field is required")
    hidden: bool = Field(default=False, description="Whether field is hidden")
    is_editable: bool = Field(default=True, description="Whether field is editable")
    editability_condition: str | None = Field(
        None,
        description=(
            "Editability condition, Example: {field_name} == 'value'. Clappia supports multiple "
            "arithmetic operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, "
            "AND, OR, XOR, ...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME "
            "operations (TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. "
            "Example: '=SUM({field_name1,field_name2}) + IF({field_name3}>10, 'Yes', 'No')'"
        ),
    )
    default_value: str | None = Field(
        None, description="Default value, Example: 'value'"
    )
    block_width_percentage_desktop: int = Field(default=50, description="Desktop width")
    block_width_percentage_mobile: int = Field(default=100, description="Mobile width")
    retain_values: bool = Field(default=True, description="Retain values when hidden")

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str | None:
        return Utils.non_empty_string_validator(v, "Label")


VALID_EMOJIS = [
    "⭐",
    "🌟",
    "😀",
    "😛",
    "😡",
    "☹",
    "🤐",
    "🤩",
    "😐",
    "👏",
    "👍",
    "👎",
    "🙏",
    "💥",
    "🔥",
    "♥",
    "💘",
    "💙",
    "💚",
    "💛",
    "💜",
    "🧡",
    "❎",
    "🆒",
    "0️⃣",
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
    "🔟",
    "✔",
    "☑",
    "✅",
    "🔵",
    "🟠",
    "🟡",
    "🟢",
    "◾",
    "◽",
    "⬛",
    "⬜",
    "🟥",
    "🟧",
    "🟨",
    "🟩",
    "🟪",
    "🟦",
    "🟫",
    "🔔",
    "🔕",
]


class UpsertFieldTextRequest(BaseUpsertFieldRequest):
    validation: Literal["none", "number", "email", "url", "custom"] | None = Field(
        None, description="Validation type"
    )
    custom_validation_condition: str | None = Field(
        None,
        description=(
            "Custom validation condition, supports multiple arithmetic operations (SUM, DIFF, "
            "PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, ...), string operations "
            "(CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations (TODAY, NOW, DATEDIF, FORMAT) "
            "that are supported by Microsoft Excel. Example: {field_name} <> 'value' or "
            "{field_name} > 10"
        ),
    )
    custom_validation_error_message: str | None = Field(
        None, description="Custom validation error message"
    )

    @model_validator(mode="after")
    def validate_custom_validation_requirements(self) -> "UpsertFieldTextRequest":
        if self.validation == "custom" and (
            not self.custom_validation_condition
            or not self.custom_validation_condition.strip()
        ):
            raise ValueError(
                "Custom validation condition is required when validation type is 'custom'"
            )
        return self


class UpsertFieldTextAreaRequest(BaseUpsertFieldRequest):
    pass


class UpsertFieldDependencyAppRequest(BaseUpsertFieldRequest):
    dependency_app_id: str = Field(
        min_length=1,
        description="ID of the dependency app, the app from which the data will be fetched, mandatory",
    )
    skip_permission_check: bool | None = Field(
        False,
        description="Whether to allow users to see all data of the dependency app",
    )
    key_field_names: list[str] = Field(
        min_length=1,
        description="Array of key field names for dependency app, Example: ['field_name'], These are the fields that you need to show to the end users so that they can identify the item to be selected",
    )
    other_field_names: list[str] | None = Field(
        None,
        description="Array of other field names for dependency app, Example: ['field_name'], you can select the items that will be pulled against the main selection made by the user. For example, if the user selects a Customer from the dropdown, all the details selected below will be fetched against that customer.",
    )
    sort_fields: list[SortField] | None = Field(
        None,
        max_length=3,
        description="Array of sort field configurations, Example: [{'sort_by': 'field_name', 'sort_direction': 'asc'}]",
    )
    no_submission_message: str | None = Field(
        "No submissions found.", description="Message when no submissions found"
    )
    filters: list[FilterField] | None = Field(
        default=None, description="Search filters"
    )
    min_chars_to_query: int | None = Field(
        0, ge=0, le=15, description="Minimum characters to trigger query"
    )
    max_search_options: int | None = Field(
        10, ge=1, le=50, description="Maximum search options to display"
    )
    show_create_submission_option: bool | None = Field(
        True,
        description="Whether to show create submission option, if no submission exists for the selected item, the user can create a new submission for that item",
    )
    enable_broad_search: bool | None = Field(
        False,
        description="Whether to enable broad search, if enabled, the user can search for the item by typing the item name",
    )

    @field_validator("key_field_names")
    @classmethod
    def validate_unique_key_fields(cls, v: list[str]) -> list[str] | None:
        return Utils.validate_unique_strings(v, "Key field names")

    @field_validator("other_field_names")
    @classmethod
    def validate_unique_other_fields(cls, v: list[str] | None) -> list[str] | None:
        return Utils.validate_unique_strings(v, "Other field names")

    @field_validator("sort_fields")
    @classmethod
    def validate_unique_sort_fields(
        cls, v: list[SortField] | None
    ) -> list[SortField] | None:
        if v is not None:
            sort_by_fields = [field.sort_by for field in v]
            if len(set(sort_by_fields)) != len(sort_by_fields):
                raise ValueError("Sort fields must have unique sortBy values")
        return v


class UpsertFieldRestApiRequest(BaseUpsertFieldRequest):
    server_url: str = Field(
        min_length=1,
        description="URL of the REST API endpoint, mandatory. Example: 'https://api.example.com/data' or 'https://api.example.com/data/{id} or {server_url}'",
    )
    method_type: Literal["GET", "POST", "PATCH", "DELETE"] = Field(
        description="HTTP method type"
    )
    body_type: Literal["JSON", "XML", "FORM-DATA"] | None = Field(
        None, description="Type of request body"
    )
    headers: str | None = Field(
        "{}",
        description="HTTP headers as JSON string, Example: {'Content-Type': 'application/json'}",
    )
    body: str | None = Field(
        "{}",
        description="Request body as JSON string, Example: {'{field_name}': 'value'} or {'{field_name}': '{field_name}'}",
    )
    query_string: str | None = Field(
        None,
        description="URL query parameters, Example: '?field_name=value' or '?field_name={field_name}'",
    )
    response_mapping: list[RestApiOutputField] = Field(
        min_length=1, description="Array of output field mappings for API response"
    )

    @field_validator("headers", "body")
    @classmethod
    def validate_json_strings(cls, v: str | None) -> str | None:
        return Utils.json_string_validator(v)

    @field_validator("response_mapping")
    @classmethod
    def validate_unique_response_mapping_names(
        cls, v: list[RestApiOutputField]
    ) -> list[RestApiOutputField]:
        names = [field.name for field in v]
        if len(set(names)) != len(names):
            raise ValueError("Response mapping field names must be unique")
        return v

    @field_validator("query_string")
    @classmethod
    def validate_query_string(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^[\s\w%&.=[\]{}\-]*$", v):
            raise ValueError("Invalid query string format")
        return v

    @model_validator(mode="after")
    def validate_body_requirements(self) -> "UpsertFieldRestApiRequest":
        if self.method_type in ["POST", "PATCH"]:
            if not self.body_type:
                raise ValueError("Body type is required for POST and PATCH requests")
            if not self.body or self.body.strip() in ["{}", ""]:
                raise ValueError("Body is required for POST and PATCH requests")

            if self.body_type == "JSON":
                try:
                    json.loads(self.body)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        "Body must be valid JSON when bodyType is JSON"
                    ) from e
            elif self.body_type == "FORM-DATA":
                try:
                    form_data = json.loads(self.body)
                    if not isinstance(form_data, dict) or len(form_data) == 0:
                        raise ValueError("Form data must be a non-empty JSON object")
                except json.JSONDecodeError as e:
                    raise ValueError("Form data must be valid JSON") from e
        return self


class UpsertFieldAddressRequest(BaseUpsertFieldRequest):
    countries_list: list[str] | None = Field(
        None,
        max_length=5,
        description="List of country codes to restrict address selection",
    )

    @field_validator("countries_list")
    @classmethod
    def validate_countries_list(cls, v: list[str] | None) -> list[str] | None:
        return Utils.validate_countries_list(v)


class UpsertFieldDatabaseRequest(BaseUpsertFieldRequest):
    database_type: Literal["MySql", "PostgreSql", "AzureSql"] = Field(
        description="Type of database to connect to"
    )
    database_port: str = Field(min_length=1, description="Database port number")
    database_host: str = Field(min_length=1, description="Database host address")
    database_username: str = Field(
        min_length=1, description="Database username for authentication"
    )
    database_password: str = Field(
        min_length=1, description="Database password for authentication"
    )
    database_name: str = Field(min_length=1, description="Name of the database")
    database_query: str = Field(
        min_length=1,
        description="SQL query to execute, Example: 'SELECT * FROM users' where id = {number_inp}",
    )
    database_output_fields: list[str] = Field(
        default_factory=list,
        description="Array of output field names from the database query",
    )
    no_records_message: str = Field(
        "No records found", description="Message to display when no records are found"
    )

    @field_validator("database_port")
    @classmethod
    def validate_database_port(cls, v: str) -> str:
        return Utils.validate_database_port(v)

    @field_validator("database_host")
    @classmethod
    def validate_database_host(cls, v: str) -> str:
        return Utils.validate_database_host(v)

    @field_validator("database_output_fields")
    @classmethod
    def validate_unique_output_fields(cls, v: list[str]) -> list[str] | None:
        return Utils.validate_unique_strings(v, "Database output fields")


class UpsertFieldDateRequest(BaseUpsertFieldRequest):
    allow_manual_input: bool = Field(
        True, description="Whether to allow users to manually type dates"
    )
    default_to_current_date: bool = Field(
        False, description="Whether to default the field to the current date"
    )
    current_date_button_visible: bool = Field(
        True, description="Whether to show a button to set current date"
    )
    start_date: str | None = Field(
        None,
        description=(
            "Start date for date range restriction (YYYY-MM-DD format) or {start_date}, "
            "Example: '2021-01-01' or {start_date}"
        ),
    )
    end_date: str | None = Field(
        None,
        description=(
            "End date for date range restriction (YYYY-MM-DD format) or {end_date}, "
            "Example: '2021-01-01' or {end_date}"
        ),
    )


class UpsertFieldAIRequest(BaseUpsertFieldRequest):
    instructions: str = Field(
        description=(
            "Instructions for the AI model, Example: 'Analyze the sentiment of "
            "{customerFeedback} and provide a summary'"
        ),
    )
    model: str = Field(description="Specific AI model to use")
    llm: Literal["OpenAI", "Claude", "Gemini"] = Field(
        description="Large Language Model provider"
    )

    @model_validator(mode="after")
    def validate_ai_configuration(self) -> "UpsertFieldAIRequest":
        if self.llm and self.model:
            model_options_map = {
                "OpenAI": [
                    "gpt-4",
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo-preview",
                    "o1-mini",
                    "o1-preview",
                    "gpt-3.5-turbo",
                ],
                "Claude": [
                    "claude-2",
                    "claude-2.1",
                    "claude-3-haiku-20240307",
                    "claude-3-sonnet-20240229",
                    "claude-3-opus-latest",
                    "claude-3-5-sonnet-latest",
                    "claude-3-5-haiku-latest",
                    "claude-3-7-sonnet-latest",
                ],
                "Gemini": [
                    "gemini-2.0-flash",
                    "gemini-2.0-flash-lite",
                    "gemini-1.5-flash",
                    "gemini-1.5-flash-8b",
                    "gemini-1.5-pro",
                ],
            }

            if self.llm in model_options_map:
                if self.model not in model_options_map[self.llm]:
                    raise ValueError(
                        f"Model '{self.model}' is not supported for LLM provider '{self.llm}'"
                    )

        if not self.instructions and not self.llm:
            raise ValueError(
                "Either instructions or LLM provider must be specified for AI field"
            )

        return self


class UpsertFieldCodeRequest(BaseUpsertFieldRequest):
    code: str = Field(
        default="""function main() {
    // Your code here
    output = {};
    var num1 = Math.round(Math.random()*10);
    var num2 = Math.round(Math.random()*10);
    output['sum'] = num1 + num2;
    output['prod'] = num1 * num2;
    return output;
}""",
        description="JavaScript code to execute",
    )
    output_fields: list[str] = Field(
        default=["sum", "prod"],
        description="Array of output field names that the code will generate",
    )

    @field_validator("output_fields")
    @classmethod
    def validate_unique_output_fields(cls, v: list[str]) -> list[str] | None:
        return Utils.validate_unique_strings(v, "Code output fields")


class UpsertFieldGpsLocationRequest(BaseUpsertFieldRequest):
    allow_manual_input: bool = Field(
        False, description="Whether to allow manual location input"
    )
    default_to_current_location: bool = Field(
        True, description="Whether to default to current GPS location"
    )
    target_locations: list[str] = Field(
        default_factory=list,
        description="Array of target location coordinates for geofencing, Example: ['22.66, 77.5946', {target_location}]",
    )
    radius: float = Field(
        1.0, description="Geofencing radius in kilometers (also called boundary)"
    )
    show_map_view: bool = Field(
        True, description="Whether to show map view for location selection"
    )
    enable_geo_fencing: bool | None = Field(
        None, description="Whether to enable geofencing functionality"
    )
    enable_reverse_geocoding: bool | None = Field(
        None, description="Whether to enable reverse geocoding functionality"
    )

    @field_validator("radius")
    @classmethod
    def validate_radius(cls, v: float) -> float:
        if not (1 <= v <= 20000000):
            raise ValueError("Radius must be between 1 and 20,000,000")
        return v

    @model_validator(mode="after")
    def validate_geo_fencing_requirements(self) -> "UpsertFieldGpsLocationRequest":
        if self.enable_geo_fencing:
            if not self.target_locations:
                raise ValueError(
                    "Target locations are required when geofencing is enabled"
                )
        return self


class UpsertFieldLiveTrackingRequest(BaseUpsertFieldRequest):
    auto_complete_duration_in_hours: int = Field(
        8, description="Duration in hours after which location tracking auto-completes"
    )

    @field_validator("auto_complete_duration_in_hours")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if not (1 <= v <= 12):
            raise ValueError("Auto complete duration must be between 1 and 12 hours")
        return v


class UpsertFieldManualAddressRequest(BaseUpsertFieldRequest):
    countries_list: list[str] | None = Field(
        None,
        max_length=5,
        description="Array of country codes to restrict address input",
    )
    default_country: str | None = Field(
        None, description="Default country code for address input"
    )

    @field_validator("countries_list")
    @classmethod
    def validate_countries_list(cls, v: list[str] | None) -> list[str] | None:
        return Utils.validate_countries_list(v)

    @field_validator("default_country")
    @classmethod
    def validate_default_country(cls, v: str | None) -> str | None:
        return Utils.validate_country_code(v)


class UpsertFieldPhoneNumberRequest(BaseUpsertFieldRequest):
    default_country_code: str | None = Field(
        None, description="Default country code (ISO format)"
    )
    is_country_code_editable: bool | None = Field(
        None, description="Whether the country code can be edited"
    )
    allow_manual_input: bool | None = Field(
        None, description="Whether to allow manual phone number input"
    )

    @field_validator("default_country_code")
    @classmethod
    def validate_country_code(cls, v: str | None) -> str | None:
        return Utils.validate_country_code(v)


class UpsertFieldProgressBarRequest(BaseUpsertFieldRequest):
    progress_formula: str | None = Field(
        None,
        description=(
            "Formula to calculate progress percentage, Example: {progress_field_name} / "
            "{total_field_name} * 100"
        ),
    )
    progress_text: str | None = Field(
        None, description="Text to display with progress, Example: 'Progress'"
    )


class UpsertFieldSignatureRequest(BaseUpsertFieldRequest):
    allow_manual_input: bool = Field(
        True, description="Whether to allow manual signature input"
    )
    file_display_name: str = Field(
        "",
        description="Display name for the signature file, Example: 'Signature' or {field_name}",
    )


class UpsertFieldRangeRequest(BaseUpsertFieldRequest):
    minimum_value: float = Field(1.0, description="Minimum value for the range slider")
    maximum_value: float = Field(5.0, description="Maximum value for the range slider")
    step_size: float = Field(1.0, description="Step size for the range slider")
    default_counter_slider: float = Field(
        1.0, description="Default value for the range slider"
    )
    allow_manual_input: bool = Field(False, description="Allow manual input of values")

    @field_validator("minimum_value")
    @classmethod
    def validate_minimum_value(cls, v: float) -> float:
        if v < 0 or v > 9007199254740991:  # Number.MAX_SAFE_INTEGER
            raise ValueError(
                "Minimum value must be greater than 0 and less than 9007199254740991"
            )
        return v

    @field_validator("maximum_value")
    @classmethod
    def validate_maximum_value(cls, v: float) -> float:
        if v < 0 or v > 9007199254740991:  # Number.MAX_SAFE_INTEGER
            raise ValueError(
                "Maximum value must be greater than 0 and less than 9007199254740991"
            )
        return v

    @field_validator("step_size")
    @classmethod
    def validate_step_size(cls, v: float) -> float:
        if v <= 0 or v > 9007199254740991:  # Number.MAX_SAFE_INTEGER
            raise ValueError(
                "Step size must be greater than 0 and less than 9007199254740991"
            )
        return v

    @model_validator(mode="after")
    def validate_range_consistency(self) -> "UpsertFieldRangeRequest":
        if self.minimum_value >= self.maximum_value:
            raise ValueError("Minimum value must be less than maximum value")

        if (
            self.default_counter_slider < self.minimum_value
            or self.default_counter_slider > self.maximum_value
        ):
            raise ValueError("Default value must be between minimum and maximum values")

        if self.step_size > (self.maximum_value - self.minimum_value):
            raise ValueError(
                "Step size cannot exceed the range between minimum and maximum values"
            )

        return self


class UpsertFieldCounterRequest(UpsertFieldRangeRequest):
    pass


class UpsertFieldSliderRequest(UpsertFieldRangeRequest):
    pass


class UpsertFieldTimeRequest(BaseUpsertFieldRequest):
    allow_manual_input: bool = Field(
        True, description="Whether to allow manual time input"
    )
    default_to_current_time: bool = Field(
        False, description="Whether to default to current time"
    )
    start_time: str | None = Field(
        None,
        description="Minimum allowed time (HH:mm format) or {start_time} Example: '09:00' or {start_time}",
    )
    end_time: str | None = Field(
        None,
        description="Maximum allowed time (HH:mm format) or {end_time} Example: '18:00' or {end_time}",
    )


class UpsertFieldToggleRequest(BaseUpsertFieldRequest):
    default_toggle_value: bool = Field(False, description="Default state of the toggle")
    true_value: str = Field(description="Value to store when toggle is ON")
    false_value: str = Field(description="Value to store when toggle is OFF")


class UpsertFieldValidationRequest(BaseUpsertFieldRequest):
    validation_type: Literal["duplicate", "custom"] = Field(
        "duplicate", description="Type of validation to perform"
    )
    validation_message: str = Field(
        "Validation message", description="Message to display for validation result"
    )
    unique_field_names: list[str] | None = Field(
        None, description="Array of field names to check for duplicates"
    )
    validation_condition: str | None = Field(
        None,
        description=(
            "Custom validation condition, supports multiple arithmetic operations (SUM, DIFF, "
            "PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, ...), string operations "
            "(CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations (TODAY, NOW, DATEDIF, FORMAT) "
            "that are supported by Microsoft Excel. Example: {field_name} <> 'value' or "
            "{field_name} > 10"
        ),
    )
    validation_level: Literal["success", "warning", "error"] = Field(
        "success", description="Level of validation result"
    )

    @field_validator("unique_field_names")
    @classmethod
    def validate_unique_field_names(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            return Utils.validate_unique_strings(v, "Unique field names")
        return v

    @model_validator(mode="after")
    def validate_validation_configuration(self) -> "UpsertFieldValidationRequest":
        if self.validation_type == "duplicate":
            if not self.unique_field_names or len(self.unique_field_names) == 0:
                raise ValueError(
                    "Unique field names are required for duplicate validation type"
                )
            if self.validation_condition:
                raise ValueError(
                    "Validation condition cannot be used with duplicate validation type"
                )
        elif self.validation_type == "custom":
            if not self.validation_condition or not self.validation_condition.strip():
                raise ValueError(
                    "Validation condition is required for custom validation type"
                )
            if self.unique_field_names:
                raise ValueError(
                    "Unique field names cannot be used with custom validation type"
                )

        return self


class UpsertFieldReadOnlyFileRequest(BaseUpsertFieldRequest):
    public_file_url: str = Field(
        description="Public file URL, Example: 'https://example.com/file.pdf'"
    )
    file_name: str = Field(
        description="File name of the file, Example: 'file.pdf' or {file_name}"
    )


class UpsertFieldVideoViewerRequest(UpsertFieldReadOnlyFileRequest):
    pass


class UpsertFieldImageViewerRequest(UpsertFieldReadOnlyFileRequest):
    pass


class UpsertFieldPdfViewerRequest(UpsertFieldReadOnlyFileRequest):
    pass


class UpsertFieldVoiceRequest(BaseUpsertFieldRequest):
    max_length: int = Field(
        60, description="Maximum length of voice recording in seconds (1-300)"
    )
    file_upload_limit: int = Field(
        10, description="Maximum number of voice files that can be uploaded (1-10)"
    )
    file_display_name: str = Field(
        "",
        description="Display name for the voice file, Example: 'Voice' or {field_name}",
    )

    @field_validator("max_length")
    @classmethod
    def validate_max_length(cls, v: int) -> int:
        if not (1 <= v <= 300):
            raise ValueError("Max length must be between 1 and 300 seconds")
        return v

    @field_validator("file_upload_limit")
    @classmethod
    def validate_file_upload_limit(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError("File upload limit must be between 1 and 10")
        return v


class UpsertFieldFormulaRequest(BaseUpsertFieldRequest):
    formula: str = Field(
        "",
        description=(
            "Formula expression with field references. Clappia supports multiple arithmetic "
            "operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, "
            "...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations "
            "(TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. Example: "
            "'=SUM({field_name1,field_name2}) + IF({field_name3}>10, 'Yes', 'No')'"
        ),
    )

    @field_validator("formula")
    @classmethod
    def validate_formula(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Formula cannot be empty")
        return v


class UpsertFieldRichTextEditorRequest(BaseUpsertFieldRequest):
    pass


class UpsertFieldCodeReaderRequest(BaseUpsertFieldRequest):
    field_type: Literal["codeScanner"] = Field(default="codeScanner")
    allow_manual_input: bool = Field(
        False, description="Whether to allow manual input of codes"
    )
    key_field_name: str | None = Field(
        None,
        description="Name of the key field for dependency app integration, Example: 'field_name', mandatory if the dependency app ID is provided",
    )
    other_field_names: list[str] | None = Field(
        None,
        description="Array of other field names for dependency app integration, Example: ['field_name']",
    )
    skip_permission_check: bool = Field(
        True, description="Whether to allow users to see all data of the dependency app"
    )
    open_camera_automatically: bool = Field(
        False,
        description="Whether to open camera automatically when app home screen is opened",
    )
    dependency_app_id: str | None = Field(
        None, description="ID of the dependency app for code scanning integration"
    )

    @field_validator("other_field_names")
    @classmethod
    def validate_unique_other_fields(cls, v: list[str] | None) -> list[str] | None:
        return Utils.validate_unique_strings(v, "Other field names")

    @field_validator("other_field_names")
    @classmethod
    def validate_other_field_names_not_empty(
        cls, v: list[str] | None
    ) -> list[str] | None:
        if v and len(v) == 0:
            raise ValueError(
                "Other field names should be an array of at least one field name"
            )
        return v

    @model_validator(mode="after")
    def validate_dependency_app_requirements(self) -> "UpsertFieldCodeReaderRequest":
        if self.dependency_app_id:
            if not self.key_field_name:
                raise ValueError(
                    "Key field name is required when dependency app ID is provided"
                )
        return self


class UpsertFieldNfcReaderRequest(UpsertFieldCodeReaderRequest):
    pass


class UpsertFieldNumberInputRequest(BaseUpsertFieldRequest):
    min_value: float | None = Field(None, description="Minimum allowed value")
    max_value: float | None = Field(None, description="Maximum allowed value")
    default_input_value: float | None = Field(
        None, description="Default value for the number input"
    )

    @model_validator(mode="after")
    def validate_number_range(self) -> "UpsertFieldNumberInputRequest":
        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                raise ValueError("Minimum value cannot be greater than maximum value")

        if self.default_input_value is not None:
            if self.min_value is not None and self.default_input_value < self.min_value:
                raise ValueError("Default value cannot be less than the minimum value")
            if self.max_value is not None and self.default_input_value > self.max_value:
                raise ValueError(
                    "Default value cannot be greater than the maximum value"
                )

        return self


class UpsertFieldReadOnlyTextRequest(BaseUpsertFieldRequest):
    rich_text: str = Field(
        description="Rich text content for display, can include field references. Example: 'Hello {field_name}'",
    )


class UpsertFieldTagsRequest(BaseUpsertFieldRequest):
    tag_names: list[str] = Field(description="Array of tag names", min_length=1)

    @field_validator("tag_names")
    @classmethod
    def validate_unique_tag_names(cls, v: list[str]) -> list[str]:
        result = Utils.validate_unique_strings(v, "Tag names")
        assert result is not None
        return result


class UpsertFieldDropdownRequest(BaseUpsertFieldRequest):
    options: list[str] = Field(
        default_factory=list,
        description=(
            "List of dropdown options. For dependent dropdowns, use '||' to separate hierarchy levels.\n\n"
            "Examples:\n"
            "• Simple dropdown: ['Red', 'Blue', 'Green']\n"
            "• Dependent dropdown: ['Shirt||Formal', 'Shirt||Casual', 'T-Shirt||Round Neck']\n"
            "• Three-level: ['Shirt||Formal||S', 'Shirt||Formal||M', 'T-Shirt||V-Neck||L']"
        ),
    )

    dependency_field_names: list[str] | None = Field(
        None,
        description=(
            "Names of parent dropdown fields that control which options are shown in this dropdown.\n"
            "Must be listed in dependency order (root parent first).\n\n"
            "How filtering works:\n"
            "• User selects 'Shirt' in Category field\n"
            "• Only options starting with 'Shirt||' are shown in dependent Type field\n"
            "• User selects 'Formal' in Type field\n"
            "• Only options starting with 'Shirt||Formal||' are shown in dependent Size field\n\n"
            "Examples:\n"
            "• Two-level: ['category_field'] - depends on one parent\n"
            "• Three-level: ['category_field', 'type_field'] - depends on two parents in order"
        ),
    )
    selecting_multiple_options_allowed: bool = Field(
        False, description="Whether multiple selections are allowed"
    )

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: list[str]) -> list[str]:
        if not v or len(v) == 0:
            raise ValueError("Options are required and should be an array of strings")
        if not all(isinstance(option, str) and option.strip() for option in v):
            raise ValueError("All options must be non-empty strings")
        return v

    @field_validator("dependency_field_names")
    @classmethod
    def validate_dependency_fields(cls, v: list[str] | None) -> list[str] | None:
        if v:
            if not all(isinstance(field, str) and field.strip() for field in v):
                raise ValueError("All dependency field names must be non-empty strings")
        return v


class UpsertFieldRadioRequest(BaseUpsertFieldRequest):
    options: list[str] = Field(
        default_factory=lambda: ["value one", "value two"],
        description=(
            "List of radio button options. For dependent radio buttons, use '||' to separate hierarchy levels.\n\n"
            "Examples:\n"
            "• Simple radio: ['Yes', 'No', 'Maybe']\n"
            "• Dependent radio: ['Shirt||Small', 'Shirt||Medium', 'T-Shirt||Large']\n"
            "• Three-level: ['Clothing||Shirt||Cotton', 'Clothing||Pants||Denim']"
        ),
    )

    number_of_cols: int = Field(
        default=1,
        description="Number of columns to display radio buttons in (1-3).",
        ge=1,
        le=3,
    )

    style: Literal["Standard", "Chips"] = Field(
        "Chips",
        description="Visual style for radio buttons (CHIPS for modern chip-style, or other ChipType values)",
    )

    dependency_field_names: list[str] | None = Field(
        None,
        description=(
            "Names of parent fields that control which radio options are shown.\n"
            "Must be listed in dependency order (root parent first).\n\n"
            "How filtering works:\n"
            "• User selects 'Clothing' in Category field\n"
            "• Only radio options starting with 'Clothing||' become available\n"
            "• User selects 'Shirt' in Type field\n"
            "• Only options starting with 'Clothing||Shirt||' are shown\n\n"
            "Examples:\n"
            "• Single dependency: ['category_field']\n"
            "• Multi-level: ['category_field', 'subcategory_field']"
        ),
    )

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: list[str]) -> list[str]:
        if not v or len(v) == 0:
            raise ValueError("Options are required and should be an array of strings")
        if not all(isinstance(option, str) and option.strip() for option in v):
            raise ValueError("All options must be non-empty strings")
        return v

    @field_validator("number_of_cols")
    @classmethod
    def validate_number_of_cols(cls, v: int | None) -> int | None:
        if v is not None and (v < 1 or v > 3):
            raise ValueError("Number of columns must be between 1 and 3")
        return v

    @field_validator("dependency_field_names")
    @classmethod
    def validate_dependency_fields(cls, v: list[str] | None) -> list[str] | None:
        if v:
            if not all(isinstance(field, str) and field.strip() for field in v):
                raise ValueError("All dependency field names must be non-empty strings")
        return v


class UpsertFieldUrlInputRequest(BaseUpsertFieldRequest):
    default_value: str | None = Field(
        None, description="Default URL value. Must be a valid URL format"
    )


class UpsertFieldCheckboxRequest(BaseUpsertFieldRequest):
    options: list[str] = Field(
        default_factory=lambda: ["value one", "value two"],
        description="Array of checkbox options, Example: ['value one', 'value two']",
    )
    number_of_cols: int = Field(
        default=1,
        description="Number of columns for checkbox layout (1-3), Example: 1 or 2 or 3",
        ge=1,
        le=3,
    )
    style: Literal["Standard", "Chips"] = Field(
        "Chips",
        description="Display style for checkboxes, Example: 'Standard' or 'Chips'",
    )
    show_not_applicable_option: bool = Field(
        True, description="Whether to show 'Not Applicable' option"
    )
    name_of_not_applicable_option: str = Field(
        "Not Applicable", description="Text for 'Not Applicable' option"
    )

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: list[str]) -> list[str]:
        if not v or len(v) == 0:
            raise ValueError("Options are required and should be an array of strings")
        if not all(isinstance(option, str) and option.strip() for option in v):
            raise ValueError("All options must be non-empty strings")
        return v


class UpsertFieldPaymentGatewayRequest(BaseUpsertFieldRequest):
    payment_gateway: Literal["Razorpay", "Stripe", "Paypal", "Eazypay"] = Field(
        description="Payment gateway provider"
    )
    currency: str = Field(
        description="Currency code, Example: 'INR' or 'USD' or {currency}"
    )
    amount: str = Field(
        description="Payment amount. Can include field references, Example: '100' or {amount}"
    )


class UpsertFieldRazorpayPaymentGatewayRequest(UpsertFieldPaymentGatewayRequest):
    key_id: str = Field(description="Razorpay API key ID")
    key_secret: str = Field(description="Razorpay API key secret")
    company_name: str | None = Field(
        None, description="Company name for payment display"
    )
    image_link: str | None = Field(
        None, description="Company logo image link for payment display"
    )
    metadata: list[dict[str, str]] | None = Field(
        None, description="Array of key-value pairs for Upsertitional metadata"
    )

    @field_validator("metadata")
    @classmethod
    def validate_metadata(
        cls, v: list[dict[str, str]] | None
    ) -> list[dict[str, str]] | None:
        if v is not None:
            keys = [item.get("key") for item in v if item.get("key")]
            if len(keys) != len(set(keys)):
                raise ValueError("Metadata must have unique keys")
            for item in v:
                if not item.get("key") or not item.get("value"):
                    raise ValueError(
                        "All metadata entries must have non-empty key and value"
                    )
        return v


class UpsertFieldEazypayPaymentGatewayRequest(UpsertFieldPaymentGatewayRequest):
    merchant_id: str = Field(description="Eazypay merchant ID")
    submerchant_id: str = Field(description="Eazypay submerchant ID")
    reference_no: str = Field(
        description="Reference number for payment. Can include field references"
    )
    optional_fields: list[str] = Field(
        description="Array of optional field names, Example: ['{field_name1}', '{field_name2}']"
    )
    mandatory_fields: list[str] = Field(
        description="Array of mandatory field names, Example: ['{field_name1}', '{field_name2}']"
    )
    encryption_key: str = Field(description="Encryption key for secure payments")

    @field_validator("optional_fields")
    @classmethod
    def validate_optional_fields(cls, v: list[str]) -> list[str]:
        if not v or len(v) == 0:
            raise ValueError("At least one optional field is required")
        if not all(isinstance(field, str) and field.strip() for field in v):
            raise ValueError("All optional fields must be strings")
        return v

    @field_validator("mandatory_fields")
    @classmethod
    def validate_mandatory_fields(cls, v: list[str]) -> list[str]:
        if not v or len(v) == 0:
            raise ValueError("At least one mandatory field is required")
        if not all(isinstance(field, str) and field.strip() for field in v):
            raise ValueError("All mandatory fields must be strings")
        return v


class UpsertFieldPaypalPaymentGatewayRequest(UpsertFieldPaymentGatewayRequest):
    paypal_client_id: str = Field(description="PayPal client ID for API authentication")
    paypal_client_secret: str = Field(
        description="PayPal client secret for API authentication"
    )


class UpsertFieldStripePaymentGatewayRequest(UpsertFieldPaymentGatewayRequest):
    publishable_key: str = Field(
        description="Stripe publishable key for client-side integration"
    )
    secret_key: str = Field(description="Stripe secret key for server-side integration")
    metadata: list[dict[str, str]] | None = Field(
        None, description="Array of key-value pairs for Upsertitional metadata"
    )

    @field_validator("metadata")
    @classmethod
    def validate_metadata(
        cls, v: list[dict[str, str]] | None
    ) -> list[dict[str, str]] | None:
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("Metadata must be an array")
            keys = [item.get("key") for item in v if item.get("key")]
            if len(keys) != len(set(keys)):
                raise ValueError("Metadata must have unique keys")
            for item in v:
                if not item.get("key") or not item.get("value"):
                    raise ValueError(
                        "All metadata entries must have non-empty key and value"
                    )
        return v


class UpsertFieldButtonRequest(BaseUpsertFieldRequest):
    button_position: Literal["left", "center", "right"] = Field(
        "left", description="Position of the button"
    )
    open_link: Literal["sameTab", "newTab", "modalTab"] = Field(
        description="How to open links"
    )
    action_details: ActionDetails = Field(
        description="Action details for button click behavior",
        discriminator="action_type",
    )


class UpsertFieldUniqueSequentialRequest(BaseUpsertFieldRequest):
    prefix: str | None = Field(
        None,
        description="Prefix for the sequential number. Can include field references, Example: 'INV' or {prefix}",
    )
    minimum_length: int = Field(
        1, description="Minimum length of the sequential number part"
    )
    starting_sequence_number: int = Field(
        1, description="Starting number for the sequence"
    )


class UpsertFieldEmailInputRequest(BaseUpsertFieldRequest):
    default_value: EmailStr | None = Field(
        None, description="Default email value for the field"
    )


class UpsertFieldEmojiRequest(BaseUpsertFieldRequest):
    emojis: list[dict[str, str]] = Field(
        default_factory=lambda: [
            {"value": "⭐", "score": "1"},
            {"value": "⭐", "score": "2"},
            {"value": "⭐", "score": "3"},
            {"value": "⭐", "score": "4"},
            {"value": "⭐", "score": "5"},
        ],
        description="Array of emoji objects with value and score",
    )
    show_not_applicable_option: bool = Field(
        True, description="Whether to show 'Not applicable' option"
    )
    not_applicable_string: str = Field(
        "Not applicable", description="Text for the not applicable option"
    )
    not_applicable_value: str = Field(
        "0", description="Value for the not applicable option"
    )
    emoji_size: int = Field(
        1, le=3, ge=1, description="Size multiplier for emoji display (1-3)"
    )

    @field_validator("emojis")
    @classmethod
    def validate_emojis(cls, v: list[dict[str, str]]) -> list[dict[str, str]]:
        if not v:
            raise ValueError("Emojis list cannot be empty")

        for emoji in v:
            if "value" not in emoji or "score" not in emoji:
                raise ValueError("Each emoji must have 'value' and 'score' properties")
            if not emoji["value"] or not emoji["score"]:
                raise ValueError("Emoji value and score cannot be empty")

            if emoji["value"] not in VALID_EMOJIS:
                raise ValueError(
                    f"Emoji '{emoji['value']}' is not in the allowed list. Allowed emojis: {', '.join(VALID_EMOJIS)}"
                )

            try:
                score_num = float(emoji["score"])
                if score_num < 0:
                    raise ValueError(
                        f"Score '{emoji['score']}' must be a non-negative number"
                    )
            except ValueError as err:
                raise ValueError(
                    f"Score '{emoji['score']}' must be a valid number"
                ) from err

        return v


class UpsertFieldFileRequest(BaseUpsertFieldRequest):
    allowed_file_types: list[
        Literal["images_camera_upload", "images_gallery_upload", "videos", "documents"]
    ] = Field(default_factory=list, description="Array of allowed file types")
    file_upload_limit: int = Field(
        10, description="Maximum number of files allowed (1-10)"
    )
    image_quality: Literal["high", "medium", "low"] = Field(
        "medium", description="Image quality for camera captures"
    )
    image_text: str | None = Field(
        None,
        description="Text watermark on captured images, Example: 'Watermark' or {field_name}",
    )
    image_text_position: Literal["TR", "BR", "BL", "TL"] | None = Field(
        None, description="Position of text watermark"
    )
    logo: str | None = Field(None, description="Logo watermark on captured images")
    logo_position: Literal["TR", "BR", "BL", "TL"] | None = Field(
        None, description="Position of logo watermark"
    )
    file_name_prefix: str = Field(
        "", description="Prefix for uploaded file names, Example: 'IMG' or {prefix}"
    )
    save_to_gallery: bool = Field(
        False, description="Whether to save captured images to device gallery"
    )
    allow_editing_camera_image: bool = Field(
        False, description="Whether to allow editing captured images"
    )

    @field_validator("file_upload_limit")
    @classmethod
    def validate_file_upload_limit(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError("File upload limit must be between 1 and 10")
        return v

    @model_validator(mode="after")
    def validate_watermark_positions(self) -> "UpsertFieldFileRequest":
        if self.image_text_position and self.logo_position:
            if self.image_text_position == self.logo_position:
                raise ValueError("Logo and Image text position cannot be the same")
        return self

    @model_validator(mode="after")
    def validate_image_related_fields(self) -> "UpsertFieldFileRequest":
        has_image_upload = (
            not self.allowed_file_types
            or "images_camera_upload" in self.allowed_file_types
            or "images_gallery_upload" in self.allowed_file_types
        )

        if not has_image_upload:
            if self.image_text or self.image_text_position:
                raise ValueError(
                    "Image text fields are only applicable when image upload is allowed"
                )
            if self.logo or self.logo_position:
                raise ValueError(
                    "Logo fields are only applicable when image upload is allowed"
                )
            if self.save_to_gallery or self.allow_editing_camera_image:
                raise ValueError(
                    "Gallery and editing options are only applicable when image upload is allowed"
                )

        return self
