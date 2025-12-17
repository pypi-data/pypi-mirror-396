from abc import ABC
from typing import Any, Literal

from pydantic import BaseModel, EmailStr

from clappia_api_tools.models.request import (
    AddUserToWorkplaceRequest,
    UpdateWorkplaceUserAttributesRequest,
    UpdateWorkplaceUserDetailsRequest,
)

from ..models.workplace import AppMetaData, AppUserMetaData, Permission, WorkplaceUser
from .base_client import BaseAPIKeyClient, BaseAuthTokenClient, BaseClappiaClient


class ClientResponse(BaseModel):
    success: bool
    data: Any | None = None
    error: str | None = None


class WorkplaceClient(BaseClappiaClient, ABC):
    """Client for managing Clappia workplace users.

    This client handles workplace user management operations including
    adding users to workplace, updating user details, attributes, roles,
    groups, and adding users to apps.
    """

    def _validate_email_phone_requirements(
        self,
        email_address: EmailStr | None,
        phone_number: str | None,
    ) -> ClientResponse | None:
        """Validate email/phone number requirements."""
        if email_address is None and phone_number is None:
            return ClientResponse(
                success=False, error="One of email address or phone number is required"
            )

        if email_address is not None and phone_number is not None:
            return ClientResponse(
                success=False,
                error="Only one of email address or phone number is required",
            )

        return None

    async def add_user_to_workplace(
        self,
        request: AddUserToWorkplaceRequest,
    ) -> ClientResponse:
        """Add a user to the workplace."""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload: dict[str, Any] = {
            "firstName": request.first_name,
            "lastName": request.last_name,
            "groupNames": request.group_names,
            "attributes": request.attributes,
        }

        if request.email_address is not None:
            payload["emailAddress"] = request.email_address
        if request.phone_number is not None:
            payload["phoneNumber"] = request.phone_number

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="workplace/addUserToWorkplace",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def update_workplace_user_details(
        self,
        request: UpdateWorkplaceUserDetailsRequest,
    ) -> ClientResponse:
        """Update workplace user details."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        updated_details: dict[str, Any] = {}
        if "first_name" in request.updated_details:
            updated_details["firstName"] = request.updated_details["first_name"]
        if "last_name" in request.updated_details:
            updated_details["lastName"] = request.updated_details["last_name"]
        if "email_address" in request.updated_details:
            updated_details["emailAddress"] = request.updated_details["email_address"]
        if "phone_number" in request.updated_details:
            updated_details["phoneNumber"] = request.updated_details["phone_number"]

        payload: dict[str, Any] = {
            "updatedDetails": updated_details,
        }

        if request.email_address is not None:
            payload["emailAddress"] = str(request.email_address)
        if request.phone_number is not None:
            payload["phoneNumber"] = request.phone_number

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="workplace/updateWorkplaceUserDetails",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def update_workplace_user_attributes(
        self,
        request: UpdateWorkplaceUserAttributesRequest,
    ) -> ClientResponse:
        """Update workplace user attributes."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload: dict[str, Any] = {
            "attributes": request.attributes,
        }

        if request.email_address is not None:
            payload["emailAddress"] = str(request.email_address)
        if request.phone_number is not None:
            payload["phoneNumber"] = request.phone_number

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="workplace/updateWorkplaceUserAttributes",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def update_workplace_user_role(
        self,
        email_address: EmailStr | None = None,
        phone_number: str | None = None,
        role: Literal["Workplace Manager", "App Builder", "User"] = "User",
    ) -> ClientResponse:
        """Update workplace user role."""
        validation_error = self._validate_email_phone_requirements(
            email_address, phone_number
        )
        if validation_error:
            return validation_error

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload: dict[str, Any] = {"role": role}
        if email_address is not None:
            payload["emailAddress"] = email_address
        if phone_number is not None:
            payload["phoneNumber"] = phone_number

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="workplace/updateWorkplaceUserRole",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def update_workplace_user_groups(
        self,
        email_address: EmailStr | None = None,
        phone_number: str | None = None,
        group_names: list[str] | None = None,
    ) -> ClientResponse:
        """Update workplace user groups."""
        validation_error = self._validate_email_phone_requirements(
            email_address, phone_number
        )
        if validation_error:
            return validation_error

        if not group_names or len(group_names) == 0:
            return ClientResponse(success=False, error="Validation failed")

        unique_groups = list(
            {name.strip() for name in group_names if name and name.strip()}
        )

        if unique_groups != group_names:
            return ClientResponse(success=False, error="Validation failed")

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload: dict[str, Any] = {
            "groupNames": unique_groups,
        }
        if email_address is not None:
            payload["emailAddress"] = email_address
        if phone_number is not None:
            payload["phoneNumber"] = phone_number

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="workplace/updateWorkplaceUserGroups",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def add_user_to_app(
        self,
        app_id: str,
        permissions: Permission,
        email_address: EmailStr | None = None,
        phone_number: str | None = None,
    ) -> ClientResponse:
        """Add a user to an app."""
        validation_error = self._validate_email_phone_requirements(
            email_address, phone_number
        )
        if validation_error:
            return validation_error

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        dict_permissions = permissions.to_dict()

        payload: dict[str, Any] = {
            "appId": app_id,
            "permissions": dict_permissions,
        }
        if email_address is not None:
            payload["emailAddress"] = email_address
        if phone_number is not None:
            payload["phoneNumber"] = phone_number

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="app/addUserToApp",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def get_workplace_apps(self) -> ClientResponse:
        """Get all apps in the workplace."""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)
        success, error_message, response_data = await self.api_utils.make_request(
            method="GET",
            endpoint="workplace/getApps",
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        apps: list[AppMetaData] = []
        if response_data:
            for app_data in response_data:
                    json_data: dict[str, Any] = (
                        app_data if isinstance(app_data, dict) else {}
                    )
                    app = AppMetaData.from_json(json_data)
                    apps.append(app)
            return ClientResponse(success=True, data=apps)
        return ClientResponse(success=False, error="Failed to retrieve workplace apps")

    async def get_workplace_user_apps(
        self,
        email_address: EmailStr | None = None,
        phone_number: str | None = None,
    ) -> ClientResponse:
        """Get apps for a specific workplace user."""
        validation_error = self._validate_email_phone_requirements(
            email_address, phone_number
        )
        if validation_error:
            return validation_error

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        params: dict[str, Any] = {}
        if email_address is not None:
            params["emailAddress"] = email_address
        if phone_number is not None:
            params["phoneNumber"] = phone_number

        success, error_message, response_data = await self.api_utils.make_request(
            method="GET",
            endpoint="workplace/getUserApps",
            params=params if params else None,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        apps: list[AppUserMetaData] = []
        if response_data:
            for app_data in response_data:
                    json_data: dict[str, Any] = (
                        app_data if isinstance(app_data, dict) else {}
                    )
                    app = AppUserMetaData.from_json(json_data)
                    apps.append(app)
            return ClientResponse(success=True, data=apps)
        return ClientResponse(
            success=False, error="Failed to retrieve workplace user apps"
        )

    async def get_workplace_users(
        self,
        page_size: int = 50,
        token: str | None = None,
    ) -> ClientResponse:
        """Get workplace users with pagination."""
        env_valid, env_error = self.api_utils.validate_environment()

        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload: dict[str, Any] = {
            "pageSize": page_size,
        }

        if token is not None:
            payload["token"] = token

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="workplace/getWorkplaceUsers",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        users = []
        next_token = None

        if response_data and isinstance(response_data, dict):
            users_data = response_data.get("users", [])
            next_token = response_data.get("token")

            if isinstance(users_data, list):
                for user_data in users_data:
                    user = WorkplaceUser(**user_data)
                    users.append(user)

        return ClientResponse(success=True, data={"users": users, "token": next_token})

    async def close(self) -> None:
        """Close the underlying HTTP client and clean up resources."""
        await self.api_utils.close()


class WorkplaceAPIKeyClient(BaseAPIKeyClient, WorkplaceClient):
    """Client for managing Clappia workplace users with API key authentication."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize workplace client with API key.

        Args:
            api_key: Clappia API key.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAPIKeyClient.__init__(self, api_key, base_url, timeout)


class WorkplaceAuthTokenClient(BaseAuthTokenClient, WorkplaceClient):
    """Client for managing Clappia workplace users with auth token authentication."""

    def __init__(
        self,
        auth_token: str,
        workplace_id: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize workplace client with auth token.

        Args:
            auth_token: Clappia Auth token.
            workplace_id: Clappia Workplace ID.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAuthTokenClient.__init__(self, auth_token, workplace_id, base_url, timeout)
