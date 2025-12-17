from abc import ABC
from typing import Any

from pydantic import BaseModel

from clappia_api_tools.enums import NodeType, TriggerType
from clappia_api_tools.models.request import (
    UpsertAiWorkflowStepRequest,
    UpsertApprovalWorkflowStepRequest,
    UpsertCodeWorkflowStepRequest,
    UpsertConditionWorkflowStepRequest,
    UpsertCreateSubmissionWorkflowStepRequest,
    UpsertDatabaseWorkflowStepRequest,
    UpsertDeleteSubmissionWorkflowStepRequest,
    UpsertEditSubmissionWorkflowStepRequest,
    UpsertEmailWorkflowStepRequest,
    UpsertFindSubmissionWorkflowStepRequest,
    UpsertLoopWorkflowStepRequest,
    UpsertMobileNotificationWorkflowStepRequest,
    UpsertRestApiWorkflowStepRequest,
    UpsertSlackWorkflowStepRequest,
    UpsertSmsWorkflowStepRequest,
    UpsertWaitWorkflowStepRequest,
    UpsertWhatsAppWorkflowStepRequest,
)

from .base_client import BaseAPIKeyClient, BaseAuthTokenClient, BaseClappiaClient


class ClientResponse(BaseModel):
    success: bool
    data: Any | None = None
    error: str | None = None


WorkflowStepRequestUnion = (
    UpsertAiWorkflowStepRequest
    | UpsertApprovalWorkflowStepRequest
    | UpsertCodeWorkflowStepRequest
    | UpsertConditionWorkflowStepRequest
    | UpsertDatabaseWorkflowStepRequest
    | UpsertEmailWorkflowStepRequest
    | UpsertLoopWorkflowStepRequest
    | UpsertMobileNotificationWorkflowStepRequest
    | UpsertRestApiWorkflowStepRequest
    | UpsertSlackWorkflowStepRequest
    | UpsertSmsWorkflowStepRequest
    | UpsertWaitWorkflowStepRequest
    | UpsertWhatsAppWorkflowStepRequest
    | UpsertCreateSubmissionWorkflowStepRequest
    | UpsertDeleteSubmissionWorkflowStepRequest
    | UpsertFindSubmissionWorkflowStepRequest
    | UpsertEditSubmissionWorkflowStepRequest
)


class WorkflowDefinitionClient(BaseClappiaClient, ABC):
    """Abstract client for managing Clappia workflow definitions.

    This client handles retrieving and managing workflow definitions, including
    getting workflows, adding workflow steps, removing workflow steps,
    updating workflow steps, and reordering workflow steps.

    Note: This is an abstract base class that contains business logic but no authentication.
    Use WorkflowDefinitionAPIKeyClient or WorkflowDefinitionAuthTokenClient for actual usage.
    """

    async def get_workflow(
        self,
        app_id: str,
        trigger_type: str,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Get a workflow definition for a specific app and trigger type"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        params = {
            "appId": app_id,
            "triggerType": trigger_type,
        }
        if version_variable_name:
            params["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="GET", endpoint="/getWorkflow", params=params
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def add(
        self,
        app_id: str,
        trigger_type: str,
        request: WorkflowStepRequestUnion,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a workflow step to a Clappia app.

        Args:
            app_id: The ID of the app to add the step to
            trigger_type: The trigger type of the workflow
            request: The request object containing the step configuration
            step_variable_name: The variable name of the step, if not provided, a random variable name will be generated
            parent_step_variable_name: The variable name of the parent step, below which the new step will be added
            version_variable_name: The variable name of the version, if not provided, the live version is used
        Returns:
            dict: Simple response with success and data fields
        """
        if isinstance(request, UpsertAiWorkflowStepRequest):
            return await self._add_ai_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertApprovalWorkflowStepRequest):
            return await self._add_approval_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertCodeWorkflowStepRequest):
            return await self._add_code_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertConditionWorkflowStepRequest):
            return await self._add_condition_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertDatabaseWorkflowStepRequest):
            return await self._add_database_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertEmailWorkflowStepRequest):
            return await self._add_email_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertLoopWorkflowStepRequest):
            return await self._add_loop_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertMobileNotificationWorkflowStepRequest):
            return await self._add_mobile_notification_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertRestApiWorkflowStepRequest):
            return await self._add_rest_api_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertSlackWorkflowStepRequest):
            return await self._add_slack_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertSmsWorkflowStepRequest):
            return await self._add_sms_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertWaitWorkflowStepRequest):
            return await self._add_wait_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertWhatsAppWorkflowStepRequest):
            return await self._add_whatsapp_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertCreateSubmissionWorkflowStepRequest):
            return await self._add_create_submission_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertDeleteSubmissionWorkflowStepRequest):
            return await self._add_delete_submission_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertFindSubmissionWorkflowStepRequest):
            return await self._add_find_submission_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )
        elif isinstance(request, UpsertEditSubmissionWorkflowStepRequest):
            return await self._add_edit_submission_step(
                app_id,
                trigger_type,
                request,
                step_variable_name,
                parent_step_variable_name,
                version_variable_name,
            )

    async def update(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: WorkflowStepRequestUnion,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a workflow step in a Clappia app.

        Args:
            app_id: The ID of the app containing the step
            trigger_type: The trigger type of the workflow
            step_variable_name: The variable name of the step to update
            request: The request object containing the updated step configuration
            version_variable_name: The variable name of the version, if not provided, the live version is used
        Returns:
            dict: Simple response with success and data fields
        """
        if isinstance(request, UpsertAiWorkflowStepRequest):
            return await self._update_ai_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertApprovalWorkflowStepRequest):
            return await self._update_approval_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertCodeWorkflowStepRequest):
            return await self._update_code_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertConditionWorkflowStepRequest):
            return await self._update_condition_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertDatabaseWorkflowStepRequest):
            return await self._update_database_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertEmailWorkflowStepRequest):
            return await self._update_email_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertLoopWorkflowStepRequest):
            return await self._update_loop_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertMobileNotificationWorkflowStepRequest):
            return await self._update_mobile_notification_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertRestApiWorkflowStepRequest):
            return await self._update_rest_api_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertSlackWorkflowStepRequest):
            return await self._update_slack_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertSmsWorkflowStepRequest):
            return await self._update_sms_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertWaitWorkflowStepRequest):
            return await self._update_wait_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertWhatsAppWorkflowStepRequest):
            return await self._update_whatsapp_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertCreateSubmissionWorkflowStepRequest):
            return await self._update_create_submission_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertDeleteSubmissionWorkflowStepRequest):
            return await self._update_delete_submission_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFindSubmissionWorkflowStepRequest):
            return await self._update_find_submission_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )
        elif isinstance(request, UpsertEditSubmissionWorkflowStepRequest):
            return await self._update_edit_submission_step(
                app_id, trigger_type, step_variable_name, request, version_variable_name
            )

    async def reorder_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        parent_step_variable_name: str,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Reorder a workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            "parentVariableName": parent_step_variable_name,
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/reorderWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_ai_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertAiWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an AI workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.AI_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_ai_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertAiWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an AI workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_approval_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertApprovalWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an approval workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.APPROVAL_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_approval_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertApprovalWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an approval workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Code Workflow Step Methods
    async def _add_code_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertCodeWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a code workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.CODE_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_code_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertCodeWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a code workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Condition Workflow Step Methods
    async def _add_condition_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertConditionWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a condition workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.CONDITION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_condition_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertConditionWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a condition workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Database Workflow Step Methods
    async def _add_database_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertDatabaseWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a database workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.DATABASE_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_database_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertDatabaseWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a database workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Email Workflow Step Methods
    async def _add_email_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertEmailWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an email workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.EMAIL_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_email_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertEmailWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an email workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Loop Workflow Step Methods
    async def _add_loop_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertLoopWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a loop workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.LOOP_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_loop_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertLoopWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a loop workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Mobile Notification Workflow Step Methods
    async def _add_mobile_notification_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertMobileNotificationWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a mobile notification workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.MOBILE_NOTIFICATION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_mobile_notification_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertMobileNotificationWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a mobile notification workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # REST API Workflow Step Methods
    async def _add_rest_api_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertRestApiWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a REST API workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.REST_API_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_rest_api_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertRestApiWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a REST API workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Slack Workflow Step Methods
    async def _add_slack_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertSlackWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a Slack workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.SLACK_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_slack_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertSlackWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a Slack workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # SMS Workflow Step Methods
    async def _add_sms_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertSmsWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an SMS workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.SMS_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_sms_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertSmsWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an SMS workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Wait Workflow Step Methods
    async def _add_wait_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertWaitWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a wait workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.WAIT_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_wait_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertWaitWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a wait workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # WhatsApp Workflow Step Methods
    async def _add_whatsapp_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertWhatsAppWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a WhatsApp workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.WHATSAPP_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_whatsapp_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertWhatsAppWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a WhatsApp workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Create Submission Workflow Step Methods
    async def _add_create_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertCreateSubmissionWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a create submission workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.CREATE_SUBMISSION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_create_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertCreateSubmissionWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a create submission workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Delete Submission Workflow Step Methods
    async def _add_delete_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertDeleteSubmissionWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a delete submission workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.DELETE_SUBMISSION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_delete_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertDeleteSubmissionWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a delete submission workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Find Submission Workflow Step Methods
    async def _add_find_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertFindSubmissionWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a find submission workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.FIND_SUBMISSION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_find_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertFindSubmissionWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a find submission workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Edit Submission Workflow Step Methods
    async def _add_edit_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertEditSubmissionWorkflowStepRequest,
        step_variable_name: str | None = None,
        parent_step_variable_name: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an edit submission workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.EDIT_SUBMISSION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_edit_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertEditSubmissionWorkflowStepRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an edit submission workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        if trigger_type not in [t.value for t in TriggerType]:
            return ClientResponse(success=False, error="Invalid trigger type")

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateWorkflowStep",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def close(self) -> None:
        """Close the underlying HTTP client and clean up resources."""
        await self.api_utils.close()


class WorkflowDefinitionAPIKeyClient(BaseAPIKeyClient, WorkflowDefinitionClient):
    """Client for managing Clappia workflow definitions with API key authentication.

    This client combines API key authentication with all workflow definition business logic.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize workflow definition client with API key.

        Args:
            api_key: Clappia API key.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAPIKeyClient.__init__(self, api_key, base_url, timeout)


class WorkflowDefinitionAuthTokenClient(BaseAuthTokenClient, WorkflowDefinitionClient):
    """Client for managing Clappia workflow definitions with auth token authentication.

    This client combines auth token authentication with all workflow definition business logic.
    """

    def __init__(
        self,
        auth_token: str,
        workplace_id: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize workflow definition client with auth token.

        Args:
            auth_token: Clappia Auth token.
            workplace_id: Clappia Workplace ID.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAuthTokenClient.__init__(self, auth_token, workplace_id, base_url, timeout)
