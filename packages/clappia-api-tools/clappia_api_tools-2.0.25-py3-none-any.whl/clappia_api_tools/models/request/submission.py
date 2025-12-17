from typing import Any, Literal

from pydantic import EmailStr, Field

from ..base_model import BaseFieldComponent
from ..submission import (
    AggregationDimension,
    AggregationMetric,
    SubmissionQuery,
)


class GetSubmissionsRequest(BaseFieldComponent):
    page_size: int = Field(
        default=10, ge=1, le=1000, description="Number of submissions per page"
    )
    forward: bool = Field(default=True, description="Direction for pagination")
    filters: SubmissionQuery | None = Field(
        default=None, description="Optional filters"
    )
    last_submission_id: str | None = Field(
        default=None,
        description="Last submission ID, next page will be fetched after this submission ID",
    )
    fields: list[str] | None = Field(
        default=None,
        description="List of fields to include in the response, both standard and custom fields. Example: ['employee_name', 'department', 'salary', 'start_date', 'location', 'image_field_name']",
    )


class GetSubmissionsAggregationRequest(BaseFieldComponent):
    forward: bool = Field(default=True, description="Direction for pagination")
    dimensions: list[AggregationDimension] | None = Field(
        None, description="Fields to group by"
    )
    aggregation_dimensions: list[AggregationMetric] | None = Field(
        None, description="Aggregation calculations"
    )
    x_axis_labels: list[str] | None = Field(
        None, description="X-axis labels for charts"
    )
    page_size: int = Field(
        default=1000, ge=1, le=1000, description="Number of results per page"
    )
    filters: SubmissionQuery | None = Field(
        default=None, description="Optional filters"
    )


class CreateSubmissionRequest(BaseFieldComponent):
    data: dict[str, Any] = Field(
        description="Submission data, in the format of a dictionary. "
        "Example: {'employee_name': 'Jane Doe', 'department': 'HR', 'salary': 60000, 'start_date': '10-02-2024', "
        "'location':'23.456789, 45.678901', 'image_field_name': "
        '[{"s3Path": {"bucket": "my-files-bucket", "key": "images/photo.jpg", "makePublic": false}}]}'
    )
    # TODO: Remove requesting_user_email_address field once the API is updated
    requesting_user_email_address: EmailStr = Field(
        description="Email of requesting user. Example: 'support@clappia.com'"
    )


class EditSubmissionRequest(BaseFieldComponent):
    submission_id: str = Field(description="Submission ID to edit")
    data: dict[str, Any] = Field(
        description="Updated submission data, in the format of a dictionary. "
        "Example: {'employee_name': 'Jane Doe', 'department': 'HR', 'salary': 60000, 'start_date': '10-02-2024', "
        "'location':'23.456789, 45.678901', 'image_field_name': "
        '[{"s3Path": {"bucket": "my-files-bucket", "key": "images/photo.jpg", "makePublic": false}}]}'
    )


class UpdateSubmissionStatusRequest(BaseFieldComponent):
    submission_id: str = Field(description="Submission ID")
    status_name: str = Field(description="New status name")
    comments: str | None = Field(default=None, description="Optional comments")


class UpdateSubmissionOwnersRequest(BaseFieldComponent):
    submission_id: str = Field(description="Submission ID")
    email_ids: list[EmailStr] = Field(
        min_length=1,
        description="List of email addresses, cannot pass both email_ids and phone_numbers",
    )
    phone_numbers: list[str] | None = Field(
        None,
        description="List of phone numbers, cannot pass both email_ids and phone_numbers",
    )


class GetSubmissionsInExcelRequest(BaseFieldComponent):
    filters: SubmissionQuery | None = Field(
        default=None, description="Optional filters"
    )
    requesting_user_email_address: EmailStr = Field(
        description="Email of requesting user. Example: 'john.doe@example.com'"
    )
    field_names: list[str] | None = Field(
        None,
        description="List of field names to include in export, both standard and custom fields. "
        "Example: ['employee_name', 'department', 'salary', 'start_date', 'location', 'image_field_name', "
        "'$submissionId', '$owner', '$status']",
    )
    format: Literal["Excel", "Csv"] = Field(
        default="Excel", description="Export format, allowed values: Excel, Csv"
    )


class GetSubmissionsCountRequest(BaseFieldComponent):
    filters: SubmissionQuery | None = Field(
        default=None, description="Optional filters"
    )


class GetSubmissionRequest(BaseFieldComponent):
    submission_id: str = Field(description="Submission ID to retrieve")
