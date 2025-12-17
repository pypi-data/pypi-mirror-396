import re
from typing import Any

from pydantic import (
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from ...utils import Utils
from ..base_model import BaseFieldComponent
from ..workplace import Permission


class BaseWorkplaceRequest(BaseFieldComponent):
    """Base class for workplace request models with common fields"""

    email_address: EmailStr | None = Field(
        default=None,
        description="Email address of the user, only one of email or phone number is required",
    )
    phone_number: str | None = Field(
        default=None,
        description="Phone number of the user, only one of email or phone number is required",
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        if v is not None:
            utils = Utils()
            return utils.validate_phone_number(v)
        return v

    @model_validator(mode="after")
    def validate_contact_method(self) -> "BaseWorkplaceRequest":
        """Ensure exactly one contact method is provided"""
        email_address = self.email_address
        phone_number = self.phone_number

        if not email_address and not phone_number:
            raise ValueError(
                "One of parameter 'emailAddress' or 'phoneNumber' must be present in the input."
            )
        if email_address and phone_number:
            raise ValueError(
                "Only one of parameter 'emailAddress' or 'phoneNumber' must be present in the input."
            )
        return self


class AddUserToWorkplaceRequest(BaseWorkplaceRequest):
    """Request model for adding a user to workplace"""

    first_name: str = Field(default="", description="First name of the user")
    last_name: str = Field(default="", description="Last name of the user")
    group_names: list[str] = Field(
        default_factory=list, description="List of group names"
    )
    attributes: dict[str, str] = Field(
        default_factory=dict, description="User attributes"
    )

    @field_validator("group_names")
    @classmethod
    def validate_group_names(cls, v: list[str]) -> list[str]:
        if v:
            unique_groups = list(
                {
                    group_name.strip()
                    for group_name in v
                    if group_name and group_name.strip()
                }
            )
            return unique_groups
        return []

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, v: dict[str, str]) -> dict[str, str]:
        if v:
            return {
                key: str(value) if value is not None else "" for key, value in v.items()
            }
        return {}


class UpdateWorkplaceUserDetailsRequest(BaseWorkplaceRequest):
    """Request model for updating workplace user details"""

    updated_details: dict[str, Any] = Field(description="Updated user details")

    @field_validator("updated_details")
    @classmethod
    def validate_updated_details(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not v or not isinstance(v, dict):
            raise ValueError("Parameter 'updatedDetails' must be present in the input.")

        allowed_keys = {"first_name", "last_name", "email_address", "phone_number"}
        invalid_keys = [key for key in v.keys() if key not in allowed_keys]
        if invalid_keys:
            raise ValueError(
                "Only first_name, last_name, email_address, phone_number can be updated"
            )

        has_any_field = any(key in v and v[key] is not None for key in allowed_keys)
        if not has_any_field:
            raise ValueError("updatedDetails must contain at least one valid field")

        return v


class UpdateWorkplaceUserAttributesRequest(BaseWorkplaceRequest):
    """Request model for updating workplace user attributes"""

    attributes: dict[str, str] = Field(description="User attributes to update")

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, v: dict[str, str]) -> dict[str, str]:
        if not v or not isinstance(v, dict):
            raise ValueError(
                "Parameter 'attributes' must be a dictionary and must be present in the input."
            )
        return {
            key: str(value) if value is not None else "" for key, value in v.items()
        }


class AddUserToAppRequest(BaseWorkplaceRequest):
    """Request model for adding a user to an app"""

    app_id: str = Field(description="App Id")
    permissions: Permission = Field(
        description="User permissions, possible keys are: can_submit_data, can_edit_data, can_view_data, can_change_status, can_edit_app, can_bulk_upload, can_view_analytics and can_delete_data. Value must be boolean true/false."
    )

    @field_validator("app_id")
    @classmethod
    def validate_app_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("App ID is required and cannot be empty")
        if not re.match(r"^[A-Z0-9]+$", v.strip()):
            raise ValueError("App ID must contain only uppercase letters and numbers")
        return v.strip()
