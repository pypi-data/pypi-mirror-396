from typing import Any

from pydantic import Field

from .base_model import BaseFieldComponent


class WorkplaceUser(BaseFieldComponent):
    name: str | None = Field(default=None, description="Name of the user")
    status: str = Field(description="Status of the user")
    email_address: str = Field(description="Email address of the user")
    phone_number: str | None = Field(
        default=None, description="Phone number of the user"
    )
    is_admin: bool = Field(description="Whether the user is an admin")
    can_create_apps: bool = Field(description="Whether the user can create apps")
    role: str = Field(description="Role of the user")


class Permission(BaseFieldComponent):
    can_submit_data: bool = Field(default=False, description="Can submit data")
    can_edit_data: bool = Field(default=False, description="Can edit data")
    can_view_data: bool = Field(default=False, description="Can view data")
    can_change_status: bool = Field(default=False, description="Can change status")
    can_edit_app: bool = Field(default=False, description="Can edit app")
    can_bulk_upload: bool = Field(default=False, description="Can bulk upload")
    can_view_analytics: bool = Field(default=False, description="Can view analytics")
    can_delete_data: bool = Field(default=False, description="Can delete data")

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> "Permission":
        return cls(**json_data)

    def to_dict(self) -> dict[str, bool]:
        return {
            "canSubmitData": self.can_submit_data,
            "canEditData": self.can_edit_data,
            "canViewData": self.can_view_data,
            "canChangeStatus": self.can_change_status,
            "canEditApp": self.can_edit_app,
            "canBulkUpload": self.can_bulk_upload,
            "canViewAnalytics": self.can_view_analytics,
            "canDeleteData": self.can_delete_data,
        }


class AppMetaData(BaseFieldComponent):
    """Response model for app metadata"""

    app_id: str = Field(description="App ID")
    name: str = Field(description="App name")
    created_at: int = Field(description="App created at")
    created_by: dict[str, Any] = Field(description="App created by")
    updated_at: int = Field(description="App updated at")
    updated_by: dict[str, Any] = Field(description="App updated by")

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> "AppMetaData":
        """Create AppMetaData instance from JSON data with proper field mapping"""
        mapped_data = {
            "app_id": json_data.get("appId", ""),
            "name": json_data.get("name", ""),
            "created_at": json_data.get("createdAt", 0),
            "created_by": json_data.get("createdBy", {}),
            "updated_at": json_data.get("lastUpdatedAt", 0),
            "updated_by": json_data.get("lastUpdatedBy", {}),
        }
        return cls(**mapped_data)


class AppUserMetaData(BaseFieldComponent):
    """Response model for app metadata"""

    app_id: str = Field(description="App ID")
    name: str = Field(description="App name")

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> "AppUserMetaData":
        """Create AppUserMetaData instance from JSON data with proper field mapping"""
        mapped_data = {
            "app_id": json_data.get("appId", ""),
            "name": json_data.get("name", ""),
        }
        return cls(**mapped_data)
