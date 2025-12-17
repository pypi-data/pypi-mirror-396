from abc import ABC
from typing import Any

from pydantic import BaseModel

from clappia_api_tools.enums import ChartType
from clappia_api_tools.models.request import (
    UpsertBarChartDefinitionRequest,
    UpsertDataTableChartDefinitionRequest,
    UpsertDoughnutChartDefinitionRequest,
    UpsertGanttChartDefinitionRequest,
    UpsertLineChartDefinitionRequest,
    UpsertMapChartDefinitionRequest,
    UpsertPieChartDefinitionRequest,
    UpsertSummaryChartDefinitionRequest,
)

from .base_client import BaseAPIKeyClient, BaseAuthTokenClient, BaseClappiaClient


class ClientResponse(BaseModel):
    success: bool
    data: Any | None = None
    error: str | None = None


ChartDefinitionRequestUnion = (
    UpsertSummaryChartDefinitionRequest
    | UpsertBarChartDefinitionRequest
    | UpsertPieChartDefinitionRequest
    | UpsertDoughnutChartDefinitionRequest
    | UpsertLineChartDefinitionRequest
    | UpsertDataTableChartDefinitionRequest
    | UpsertMapChartDefinitionRequest
    | UpsertGanttChartDefinitionRequest
)


class AnalyticsClient(BaseClappiaClient, ABC):
    """Abstract client for managing Clappia analytics and charts.

    This client handles retrieving and managing analytics configurations, including
    adding charts, removing charts, updating charts, and reordering charts.
    """

    async def add(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: ChartDefinitionRequestUnion,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a chart to an app."""
        if isinstance(request, UpsertSummaryChartDefinitionRequest):
            return await self._add_summary_chart(
                app_id,
                chart_index,
                chart_title,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertBarChartDefinitionRequest):
            return await self._add_bar_chart(
                app_id,
                chart_index,
                chart_title,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertPieChartDefinitionRequest):
            return await self._add_pie_chart(
                app_id,
                chart_index,
                chart_title,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertDoughnutChartDefinitionRequest):
            return await self._add_doughnut_chart(
                app_id,
                chart_index,
                chart_title,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertLineChartDefinitionRequest):
            return await self._add_line_chart(
                app_id,
                chart_index,
                chart_title,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertDataTableChartDefinitionRequest):
            return await self._add_data_table_chart(
                app_id,
                chart_index,
                chart_title,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertMapChartDefinitionRequest):
            return await self._add_map_chart(
                app_id,
                chart_index,
                chart_title,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertGanttChartDefinitionRequest):
            return await self._add_gantt_chart(
                app_id,
                chart_index,
                chart_title,
                request,
                version_variable_name,
            )

    async def update(
        self,
        app_id: str,
        chart_index: int,
        request: ChartDefinitionRequestUnion,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a chart in an app."""
        if isinstance(request, UpsertSummaryChartDefinitionRequest):
            return await self._update_summary_chart(
                app_id, chart_index, request, version_variable_name
            )
        elif isinstance(request, UpsertBarChartDefinitionRequest):
            return await self._update_bar_chart(
                app_id, chart_index, request, version_variable_name
            )
        elif isinstance(request, UpsertPieChartDefinitionRequest):
            return await self._update_pie_chart(
                app_id, chart_index, request, version_variable_name
            )
        elif isinstance(request, UpsertDoughnutChartDefinitionRequest):
            return await self._update_doughnut_chart(
                app_id, chart_index, request, version_variable_name
            )
        elif isinstance(request, UpsertLineChartDefinitionRequest):
            return await self._update_line_chart(
                app_id, chart_index, request, version_variable_name
            )
        elif isinstance(request, UpsertDataTableChartDefinitionRequest):
            return await self._update_data_table_chart(
                app_id, chart_index, request, version_variable_name
            )
        elif isinstance(request, UpsertMapChartDefinitionRequest):
            return await self._update_map_chart(
                app_id, chart_index, request, version_variable_name
            )
        elif isinstance(request, UpsertGanttChartDefinitionRequest):
            return await self._update_gantt_chart(
                app_id, chart_index, request, version_variable_name
            )

    async def _add_summary_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertSummaryChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a summary chart to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.SUMMARY_CARD.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/addChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_summary_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertSummaryChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a summary chart in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.SUMMARY_CARD.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/updateChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_bar_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertBarChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a bar chart to an app."""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.BAR_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/addChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_bar_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertBarChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a bar chart in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.BAR_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/updateChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_pie_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertPieChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a pie chart to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.PIE_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/addChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_pie_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertPieChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a pie chart in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.PIE_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/updateChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_doughnut_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertDoughnutChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a doughnut chart to an app."""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.DOUGHNUT_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/addChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_doughnut_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertDoughnutChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a doughnut chart in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.DOUGHNUT_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/updateChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_line_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertLineChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a line chart to an app."""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.LINE_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/addChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_line_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertLineChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a line chart in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.LINE_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/updateChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_data_table_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertDataTableChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a data table chart to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.DATA_TABLE.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/addChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_data_table_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertDataTableChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a data table chart in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.DATA_TABLE.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/updateChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_map_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertMapChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a map chart to an app."""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.MAP_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/addChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_map_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertMapChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a map chart in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.MAP_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/updateChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_gantt_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertGanttChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a Gantt chart to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.GANTT_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/addChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_gantt_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertGanttChartDefinitionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a Gantt chart in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.GANTT_CHART.value,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/updateChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def reorder_chart(
        self,
        app_id: str,
        source_index: int,
        target_index: int,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sourceIndex": source_index,
            "targetIndex": target_index,
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST", endpoint="/reorderChart", data=payload
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def get_charts(
        self, app_id: str, version_variable_name: str | None = None
    ) -> ClientResponse:
        """Get all charts for a specific app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)
        params = {
            "appId": app_id,
        }
        if version_variable_name is not None:
            params["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="GET", endpoint="/getAppCharts", params=params
        )

        if not success:
            return ClientResponse(success=False, error=error_message)
        return ClientResponse(success=True, data=response_data)

    async def close(self) -> None:
        """Close the underlying HTTP client and clean up resources."""
        await self.api_utils.close()


class AnalyticsAPIKeyClient(BaseAPIKeyClient, AnalyticsClient):
    """Client for managing Clappia analytics and charts with API key authentication."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize analytics client with API key.

        Args:
            api_key: Clappia API key.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAPIKeyClient.__init__(self, api_key, base_url, timeout)


class AnalyticsAuthTokenClient(BaseAuthTokenClient, AnalyticsClient):
    """Client for managing Clappia analytics and charts with auth token authentication."""

    def __init__(
        self,
        auth_token: str,
        workplace_id: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize analytics client with auth token.

        Args:
            auth_token: Clappia Auth token.
            workplace_id: Clappia Workplace ID.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAuthTokenClient.__init__(self, auth_token, workplace_id, base_url, timeout)
