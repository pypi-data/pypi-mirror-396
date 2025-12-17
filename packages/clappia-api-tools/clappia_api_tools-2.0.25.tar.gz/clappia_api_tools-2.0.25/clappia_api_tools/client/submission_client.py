from abc import ABC
from typing import Any

from pydantic import BaseModel

from clappia_api_tools.models.request import (
    CreateSubmissionRequest,
    EditSubmissionRequest,
    GetSubmissionRequest,
    GetSubmissionsAggregationRequest,
    GetSubmissionsCountRequest,
    GetSubmissionsInExcelRequest,
    GetSubmissionsRequest,
    UpdateSubmissionOwnersRequest,
    UpdateSubmissionStatusRequest,
)

from .base_client import BaseAPIKeyClient, BaseAuthTokenClient, BaseClappiaClient


class ClientResponse(BaseModel):
    success: bool
    data: Any | None = None
    error: str | None = None


class SubmissionClient(BaseClappiaClient, ABC):
    """Client for managing Clappia submissions.

    This client handles retrieving and managing submissions, including
    getting a submission, getting submissions, getting submissions aggregation,
    creating submissions, editing submissions, updating submission status,
    updating submission owners.
    """

    async def get_submissions(
        self,
        app_id: str,
        request: GetSubmissionsRequest,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload: dict[str, Any] = {
            "appId": app_id,
            "pageSize": request.page_size,
            "forward": request.forward,
        }

        if request.filters:
            payload["filters"] = request.filters.to_dict()

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/getSubmissions", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)
        return ClientResponse(success=True, data=response_data)

    async def get_submissions_aggregation(
        self,
        app_id: str,
        request: GetSubmissionsAggregationRequest,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if not request.dimensions and not request.aggregation_dimensions:
            return ClientResponse(
                success=False,
                error="At least one dimension or aggregation dimension must be provided",
            )

        payload: dict[str, Any] = {
            "appId": app_id,
            "forward": request.forward,
            "pageSize": request.page_size,
            "xAxisLabels": request.x_axis_labels or [],
        }

        if request.dimensions:
            payload["dimensions"] = [dim.to_dict() for dim in request.dimensions]
        if request.aggregation_dimensions:
            payload["aggregationDimensions"] = [
                agg.to_dict() for agg in request.aggregation_dimensions
            ]
        if request.filters:
            payload["filters"] = request.filters.to_dict()

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/getSubmissionsAggregation",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def create_submission(
        self,
        app_id: str,
        request: CreateSubmissionRequest,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload: dict[str, Any] = {
            "appId": app_id,
            "data": request.data,
            "requestingUserEmailAddress": str(request.requesting_user_email_address),
        }

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/create", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def edit_submission(
        self,
        app_id: str,
        request: EditSubmissionRequest,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload: dict[str, Any] = {
            "appId": app_id,
            "submissionId": request.submission_id,
            "data": request.data,
        }

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/edit", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def update_status(
        self,
        app_id: str,
        request: UpdateSubmissionStatusRequest,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        status: dict[str, Any] = {
            "name": request.status_name.strip(),
            "comments": request.comments.strip() if request.comments else None,
        }

        payload: dict[str, Any] = {
            "appId": app_id,
            "submissionId": request.submission_id,
            "status": status,
        }

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/updateStatus", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def update_owners(
        self,
        app_id: str,
        request: UpdateSubmissionOwnersRequest,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload: dict[str, Any] = {
            "appId": app_id,
            "submissionId": request.submission_id,
            "emailIds": [str(email) for email in request.email_ids],
            "phoneNumbers": request.phone_numbers,
        }

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/updateSubmissionOwners", data=payload
        )
        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def get_submissions_in_excel(
        self,
        app_id: str,
        request: GetSubmissionsInExcelRequest,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload: dict[str, Any] = {
            "appId": app_id,
            "requestingUserEmailAddress": str(request.requesting_user_email_address),
            "format": request.format,
        }

        if request.filters:
            payload["filters"] = request.filters.to_dict()
        if request.field_names:
            payload["fieldNames"] = request.field_names

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/getSubmissionsExcel", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        if response_data and response_data.get("statusCode") == 202:
            return ClientResponse(success=True, data=response_data)
        else:
            return ClientResponse(success=True, data=response_data)

    async def get_submissions_count(
        self,
        app_id: str,
        request: GetSubmissionsCountRequest,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload: dict[str, Any] = {
            "appId": app_id,
        }

        if request.filters:
            payload["filters"] = request.filters.to_dict()

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/getSubmissionsCount", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def get_submission(
        self,
        app_id: str,
        request: GetSubmissionRequest,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        params: dict[str, Any] = {
            "appId": app_id,
            "submissionId": request.submission_id,
        }

        success, error_message, response_data = await self.api_utils.make_request(
            method="GET", endpoint="/getSubmission", params=params
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def close(self) -> None:
        """Close the underlying HTTP client and clean up resources."""
        await self.api_utils.close()


class SubmissionAPIKeyClient(BaseAPIKeyClient, SubmissionClient):
    """Client for managing Clappia submissions with API key authentication."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize submission client with API key.

        Args:
            api_key: Clappia API key.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAPIKeyClient.__init__(self, api_key, base_url, timeout)


class SubmissionAuthTokenClient(BaseAuthTokenClient, SubmissionClient):
    """Client for managing Clappia submissions with auth token authentication."""

    def __init__(
        self,
        auth_token: str,
        workplace_id: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize submission client with auth token.

        Args:
            auth_token: Clappia Auth token.
            workplace_id: Clappia Workplace ID.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAuthTokenClient.__init__(self, auth_token, workplace_id, base_url, timeout)
