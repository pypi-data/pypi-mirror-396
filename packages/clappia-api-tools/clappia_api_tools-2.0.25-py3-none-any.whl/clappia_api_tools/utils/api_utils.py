import json
from typing import Any

import httpx


class ClappiaAPIUtils:
    """Abstract base API utilities with common functionality for all Clappia API interactions"""

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
    ):
        self.base_url = base_url
        self.timeout = timeout

    async def get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
            ),
        )

    async def close(self) -> None:
        pass

    def validate_environment(self) -> tuple[bool, str]:
        if not self.base_url:
            return (
                False,
                "Base URL is not configured",
            )
        return True, ""

    def get_headers(
        self,
        data: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    def _handle_response(
        self, response: httpx.Response
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        if response.status_code == 200:
            try:
                return True, None, response.json()
            except json.JSONDecodeError:
                return True, None, {"raw_response": response.text}

        error_message = self._format_error_message(response)
        return False, error_message, None

    def _format_error_message(self, response: httpx.Response) -> str:
        if response.status_code in [400, 401, 403, 404]:
            try:
                error_data = response.json()
                return f"API Error ({response.status_code}): {json.dumps(error_data, indent=2)}"
            except json.JSONDecodeError:
                return f"API Error ({response.status_code}): {response.text}"
        else:
            return f"Unexpected API response ({response.status_code}): {response.text}"

    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> tuple[bool, str | None, Any | None]:
        env_valid, env_error = self.validate_environment()
        if not env_valid:
            return False, f"Configuration error: {env_error}", None

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self.get_headers(data, params)
        try:
            client = await self.get_client()
            try:
                print(f"Making API Call: URL: {url}, Method: {method}, Headers: {headers}, Data: {data}, Params: {params}")
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                )
                return self._handle_response(response)
            finally:
                await client.aclose()

        except httpx.TimeoutException:
            return False, f"Request timeout after {self.timeout} seconds", None
        except httpx.ConnectError:
            return False, "Connection error - unable to reach Clappia API", None
        except Exception as e:
            return False, f"Unexpected error: {e!s}", None


class ClappiaAPIKeyUtils(ClappiaAPIUtils):
    """API utilities for Clappia API key authentication"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 30,
    ):
        super().__init__(base_url, timeout)
        self.api_key = api_key

    def validate_environment(self) -> tuple[bool, str]:
        if not self.api_key:
            return (
                False,
                "API key is not configured",
            )
        return super().validate_environment()

    def get_headers(
        self,
        data: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        """Get standard headers for API requests"""
        headers = super().get_headers(data, params)
        headers["x-api-key"] = self.api_key
        return headers


class ClappiaAuthTokenUtils(ClappiaAPIUtils):
    """API utilities for Clappia auth token authentication with workplace ID support"""

    def __init__(
        self,
        auth_token: str,
        workplace_id: str,
        base_url: str,
        timeout: int = 30,
    ):
        super().__init__(base_url, timeout)
        self.auth_token = auth_token
        self.workplace_id = workplace_id

    def validate_environment(self) -> tuple[bool, str]:
        if not self.auth_token:
            return (
                False,
                "Auth token is not configured",
            )
        if not self.workplace_id:
            return (
                False,
                "Workplace ID is not configured",
            )
        return super().validate_environment()

    def get_headers(
        self,
        data: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        headers = super().get_headers(data, params)
        headers["Authorization"] = self.auth_token
        headers["workplaceId"] = self.workplace_id

        if params and "appId" in params:
            headers["appId"] = params["appId"]
        elif data and "appId" in data:
            headers["appId"] = data["appId"]

        return headers
