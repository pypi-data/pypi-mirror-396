from typing import Any, Literal

from pydantic import Field

from .base_model import BaseFieldComponent


class ExternalCondition(BaseFieldComponent):
    """
    Represents a filter condition for external filter validation and conversion.

    This class defines the structure for filter conditions that can be applied to
    Clappia app submissions. It supports various field types including text, numeric,
    date, and selection fields with appropriate operator validation.
    """

    condition_field_name: str = Field(
        description="Name of the field to filter on. Can be a custom field or reserved field. "
        "Reserved fields: $submissionId, $status, $createdAt, $updatedAt, $owners, $all_fields. "
        "Example: 'customerName', '$status', '$createdAt'"
    )
    condition_field_operator: Literal[
        "CONTAINS",
        "NOT_IN",
        "EQ",
        "NEQ",
        "EMPTY",
        "NON_EMPTY",
        "STARTS_WITH",
        "BETWEEN",
        "GT",
        "LT",
        "GTE",
        "LTE",
        "ENDS_WITH",
    ] = Field(
        description="Operator to apply to the field. Text fields support: CONTAINS, NOT_IN, STARTS_WITH, "
        "EQ, NEQ, EMPTY, NON_EMPTY. Numeric fields support: CONTAINS, NOT_IN, EQ, NEQ, GT, "
        "GTE, LT, LTE, EMPTY, NON_EMPTY, STARTS_WITH. Date fields support: BETWEEN, EMPTY, "
        "NON_EMPTY. Selection fields support: EQ, NEQ, EMPTY, NON_EMPTY. "
        "Example: 'CONTAINS', 'EQ', 'BETWEEN', 'EMPTY'"
    )
    condition_field_values: list[Any] = Field(
        description="Array of values to filter by. Not required for EMPTY/NON_EMPTY operators. "
        "For BETWEEN date operations, requires exactly 2 values (start and end date). "
        "For selection fields, values must match field options. For numeric fields, "
        "values must be valid numbers. For text fields, values must be non-empty strings. "
        "For app-related fields, values must be string IDs. "
        "Example: ['John', 'Jane'], [100, 200], ['2024-01-01', '2024-12-31']"
    )
    condition_field_date_token: (
        Literal[
            "CUS",
            "TOD",
            "YES",
            "TOM",
            "L_W",
            "L_M",
            "L_Y",
            "L_7",
            "L30",
            "L90",
            "C_W",
            "C_M",
            "C_Y",
            "N_W",
            "N_M",
            "N_Y",
            "N_7",
            "N30",
            "N90",
        ]
        | None
    ) = Field(
        default=None,
        description="Date token for date field filtering. Only valid for date fields with BETWEEN operator. "
        "Required for date BETWEEN operations. CUS = Custom date range, TOD = Today, YES = Yesterday. "
        "Example: 'CUS', 'TOD', 'YES'",
    )


class ExternalFilter(BaseFieldComponent):
    """
    Represents an external filter for Clappia app submissions with comprehensive validation.

    This class provides a complete filter structure that includes a condition and logical operator
    for combining multiple filters. It supports validation against field definitions and conversion
    to internal filter format.
    """

    condition: ExternalCondition = Field(
        description="Filter condition defining the field, operator, and values to filter by. "
        "Validation rules: Field must exist in app definition or be a reserved field. "
        "Field type must be searchable. Operator must be compatible with field type. "
        "Values must match field type requirements. Date BETWEEN operations require dateToken. "
        "Selection field values must match field options. Numeric field values must be valid numbers. "
        "Text field values must be non-empty strings. App-related field values must be string IDs. "
        "Reserved fields ($submissionId, $status, $createdAt, $updatedAt) have specific validation rules."
    )
    logical_operator: Literal["AND", "OR"] = Field(
        default="AND",
        description="Logical operator to combine with other filters. Default: 'AND'. "
        "Used when multiple filters are applied to the same chart. "
        "Example: 'AND', 'OR'",
    )


class ExternalChartDimension(BaseFieldComponent):
    """
    Represents an external chart dimension for analytics with comprehensive validation.

    This class provides the external interface for chart dimensions, allowing users
    to specify field names instead of field IDs. It supports validation and conversion
    to internal chart dimension format.
    """

    dimension_field_name: str = Field(
        description="Name of the field to use as dimension. Can be a custom field or standard field. "
        "Example: 'category', 'region', 'date', 'status'"
    )
    dimension_label: str | None = Field(
        default=None,
        description="Display label for the dimension. Example: 'Category', 'Region', 'Date Range'",
    )
    dimension_type: Literal["STANDARD", "CUSTOM"] | None = Field(
        default="CUSTOM",
        description="Type of dimension field. Example: 'STANDARD', 'CUSTOM'",
    )
    dimension_interval: Literal["day", "week", "month", "year"] | None = Field(
        default=None,
        description="Interval for date-based dimensions. Only applicable for date fields. "
        "Example: 'day', 'week', 'month', 'year'",
    )
    dimension_sort_direction: Literal["asc", "desc"] | None = Field(
        default="asc",
        description="Sort direction for the dimension values. Example: 'asc', 'desc'",
    )
    dimension_sort_type: Literal["number", "string"] | None = Field(
        default="string",
        description="Type of sorting to apply to dimension values. Example: 'number', 'string'",
    )
    dimension_missing_value: str | None = Field(
        default=None,
        description="Value to use when dimension field data is missing. Example: 'Unknown', 'N/A'",
    )


class ExternalAggregation(BaseFieldComponent):
    """
    Represents an external aggregation for analytics with comprehensive validation.

    This class provides the external interface for aggregation operations, allowing users
    to specify field names instead of field IDs. It supports validation and conversion
    to internal aggregation format.
    """

    aggregation_type: Literal[
        "count", "sum", "average", "minimum", "maximum", "unique"
    ] = Field(
        default="count",
        description="Type of aggregation to perform on the data. "
        "Example: 'count', 'sum', 'average', 'minimum', 'maximum', 'unique'",
    )
    aggregation_field: ExternalChartDimension = Field(
        description="Field to aggregate on. Defines which field the aggregation will be performed on."
    )
