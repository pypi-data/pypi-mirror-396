from typing import Literal

from pydantic import Field, field_validator

from ...models.analytics import (
    ExternalAggregation,
    ExternalChartDimension,
    ExternalFilter,
)
from ...utils.utils import Utils
from ..base_model import BaseFieldComponent


class BaseUpsertChartRequest(BaseFieldComponent):
    """Base class for all chart definition requests with common fields."""

    width: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Width of the chart, 1-100 allowed and divisible by 25",
    )
    filters: list[ExternalFilter] | None = Field(
        default=None, description="Filters for the chart"
    )


class UpsertBarChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Bar Chart definition.

    Mirrors the ExternalBarChartDefinition from the TS code. Supports:
    - Aggregation dimensions (required, at least one)
    - Grouping dimensions (required, at least one)
    - Stacked configuration (optional)
    - Direction configuration (optional, Horizontal/Vertical)
    """

    aggregation_dimensions: list[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the bar chart. Defines what data to aggregate and how to display it."
    )
    dimensions: list[ExternalChartDimension] = Field(
        description="Array of dimensions for the bar chart. Defines how to group and categorize the data."
    )
    is_stacked: bool | None = Field(
        default=None,
        description="Whether to display bars as stacked or grouped. Default: false. Example: true for stacked bars, false for grouped bars",
    )
    direction: Literal["Horizontal", "Vertical"] | None = Field(
        default=None,
        description="Direction of the bar chart. Example: 'Horizontal' for horizontal bars, 'Vertical' for vertical bars",
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_aggregation_dimensions(
        cls, v: list[ExternalAggregation]
    ) -> list[ExternalAggregation]:
        result = Utils.validate_non_empty_list(v, field_name="aggregation_dimensions")
        assert result is not None
        return result

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions(
        cls, v: list[ExternalChartDimension]
    ) -> list[ExternalChartDimension]:
        result = Utils.validate_non_empty_list(v, field_name="dimensions")
        assert result is not None
        return result

    @field_validator("is_stacked")
    @classmethod
    def validate_is_stacked(cls, v: bool | None) -> bool | None:
        return Utils.validate_boolean(v, field_name="is_stacked")


class UpsertDataTableChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Data Table chart definition.

    Mirrors the ExternalDataTableChartDefinition from the TS code. Supports:
    - Aggregation dimensions (required, at least one, maximum 4)
    - Grouping dimensions (required, at least one)
    """

    aggregation_dimensions: list[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the data table. Defines what data to aggregate and display in columns. Maximum 4 aggregations allowed."
    )
    dimensions: list[ExternalChartDimension] = Field(
        description="Array of dimensions for the data table. Defines how to group and categorize the data in rows."
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_aggregation_dimensions_dt(
        cls, v: list[ExternalAggregation]
    ) -> list[ExternalAggregation]:
        result = Utils.validate_non_empty_list(v, field_name="aggregation_dimensions")
        assert result is not None
        result = Utils.validate_max_count(
            result, max_count=4, field_name="aggregation_dimensions"
        )
        assert result is not None
        return result


class UpsertDoughnutChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Doughnut chart definition.

    Mirrors the ExternalDoughnutChartDefinition from the TS code. Supports:
    - Exactly one aggregation dimension
    - Exactly one grouping dimension
    - Optional legend visibility flag
    """

    aggregation_dimensions: list[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the doughnut chart. Only one aggregation dimension is allowed."
    )
    dimensions: list[ExternalChartDimension] = Field(
        description="Array of dimensions for the doughnut chart. Only one dimension is allowed."
    )
    show_legend: bool | None = Field(
        default=None,
        description="Whether to display the legend for the doughnut chart. Default: true. Example: true to show legend, false to hide legend",
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_aggregation_dimensions_doughnut(
        cls, v: list[ExternalAggregation]
    ) -> list[ExternalAggregation]:
        result = Utils.validate_exact_count(
            v, count=1, field_name="aggregation_dimensions"
        )
        assert result is not None
        return result

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions_doughnut(
        cls, v: list[ExternalChartDimension]
    ) -> list[ExternalChartDimension]:
        result = Utils.validate_exact_count(v, count=1, field_name="dimensions")
        assert result is not None
        return result

    @field_validator("show_legend")
    @classmethod
    def validate_show_legend(cls, v: bool | None) -> bool | None:
        return Utils.validate_boolean(v, field_name="show_legend")


class UpsertGanttChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Gantt chart definition.

    Mirrors the ExternalGanttChartDefinition from the TS code. Supports:
    - Exactly 5 dimensions in order: task Id, resource, task name, start date, end date
    - Optional dependency, completion, milestone dimensions
    - Optional additional dimensions
    """

    dimensions: list[ExternalChartDimension] = Field(
        description=(
            "Array of 5 dimensions for the gantt chart in order of task Id, "
            "resource, task name, start date and end date."
        )
    )
    dependencies_dimension: ExternalChartDimension | None = Field(
        default=None, description="Dimension for task dependencies."
    )
    completion_dimension: ExternalChartDimension | None = Field(
        default=None, description="Dimension for task completion status."
    )
    milestone_dimension: ExternalChartDimension | None = Field(
        default=None, description="Dimension for milestone information."
    )
    additional_dimensions: list[ExternalChartDimension] | None = Field(
        default=None, description="Additional dimensions for the gantt chart."
    )

    @field_validator("dimensions")
    @classmethod
    def validate_gantt_dimensions(
        cls, v: list[ExternalChartDimension]
    ) -> list[ExternalChartDimension]:
        result = Utils.validate_exact_count(
            v,
            count=5,
            field_name="dimensions",
        )
        assert result is not None
        return result


class UpsertLineChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Line chart definition.

    Mirrors the ExternalLineChartDefinition from the TS code. Supports:
    - Aggregation dimensions (required, at least one; first used for Y axis)
    - Grouping dimensions (required, at least one; first used for X axis)
    - Optional fill area flag
    """

    aggregation_dimensions: list[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the line chart."
    )
    dimensions: list[ExternalChartDimension] = Field(
        description="Array of dimensions for the line chart."
    )
    fill: bool | None = Field(
        default=None,
        description="Whether to fill the area under the line. Default: false.",
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_line_aggregation_dimensions(
        cls, v: list[ExternalAggregation]
    ) -> list[ExternalAggregation]:
        result = Utils.validate_non_empty_list(v, field_name="aggregation_dimensions")
        assert result is not None
        return result


class UpsertMapChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Map chart definition.

    Mirrors the ExternalMapChartDefinition from the TS code. Supports:
    - Exactly two dimensions: gps location and label (in this order)
    """

    dimensions: list[ExternalChartDimension] = Field(
        description=(
            "Array of 2 dimensions for the map chart in order of gps location and label."
        )
    )

    @field_validator("dimensions")
    @classmethod
    def validate_map_dimensions(
        cls, v: list[ExternalChartDimension]
    ) -> list[ExternalChartDimension]:
        result = Utils.validate_exact_count(v, count=2, field_name="dimensions")
        assert result is not None
        return result


class UpsertPieChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Pie chart definition.

    Mirrors the ExternalPieChartDefinition from the TS code. Supports:
    - Exactly one aggregation dimension
    - Exactly one grouping dimension
    - Optional legend visibility flag
    """

    aggregation_dimensions: list[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the pie chart. Only one aggregation dimension is allowed."
    )
    dimensions: list[ExternalChartDimension] = Field(
        description="Array of dimensions for the pie chart. Only one dimension is allowed."
    )
    show_legend: bool | None = Field(
        default=None,
        description="Whether to display the legend for the pie chart. Default: true.",
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_pie_aggregation_dimensions(
        cls, v: list[ExternalAggregation]
    ) -> list[ExternalAggregation]:
        result = Utils.validate_exact_count(
            v, count=1, field_name="aggregation_dimensions"
        )
        assert result is not None
        return result

    @field_validator("dimensions")
    @classmethod
    def validate_pie_dimensions(
        cls, v: list[ExternalChartDimension]
    ) -> list[ExternalChartDimension]:
        result = Utils.validate_exact_count(v, count=1, field_name="dimensions")
        assert result is not None
        return result

    @field_validator("show_legend")
    @classmethod
    def validate_pie_show_legend(cls, v: bool | None) -> bool | None:
        return Utils.validate_boolean(v, field_name="show_legend")


class UpsertSummaryChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Summary Card chart definition.

    Mirrors the ExternalSummaryChartDefinition from the TS code. Supports:
    - Exactly one aggregation dimension
    """

    aggregation_dimensions: list[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the summary chart. Only one aggregation dimension is allowed."
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_summary_aggregation_dimensions(
        cls, v: list[ExternalAggregation]
    ) -> list[ExternalAggregation]:
        result = Utils.validate_exact_count(
            v, count=1, field_name="aggregation_dimensions"
        )
        assert result is not None
        return result
