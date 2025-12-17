from clappia_api_tools.utils.api_utils import (
    ClappiaAPIKeyUtils,
    ClappiaAPIUtils,
    ClappiaAuthTokenUtils,
)


class BaseClappiaClient:
    """Base client with shared functionality for all Clappia clients."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.api_utils = ClappiaAPIUtils(base_url, timeout)


class BaseAPIKeyClient(BaseClappiaClient):
    """Base client for API key authentication."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize base API key client.

        Args:
            api_key: Clappia API key.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        super().__init__(base_url, timeout)
        self.api_utils = ClappiaAPIKeyUtils(api_key, base_url, timeout)


class BaseAuthTokenClient(BaseClappiaClient):
    """Base client for auth token authentication."""

    def __init__(
        self,
        auth_token: str,
        workplace_id: str,
        base_url: str,
        timeout: int = 30,
    ):
        super().__init__(base_url, timeout)
        self.api_utils = ClappiaAuthTokenUtils(
            auth_token, workplace_id, base_url, timeout
        )
