import asyncio
from abc import ABC
from typing import Any

import httpx
from pydantic import BaseModel, EmailStr

from clappia_api_tools.client.file_management_client import FileManagementClient
from clappia_api_tools.enums import FieldType
from clappia_api_tools.models.definition import (
    ExternalPageDefinition,
    ExternalTemplateDefinition,
)
from clappia_api_tools.models.request import (
    AddPageBreakRequest,
    UpdateAppMetadataRequest,
    UpdatePageBreakRequest,
    UpsertFieldAddressRequest,
    UpsertFieldAIRequest,
    UpsertFieldButtonRequest,
    UpsertFieldCheckboxRequest,
    UpsertFieldCodeReaderRequest,
    UpsertFieldCodeRequest,
    UpsertFieldCounterRequest,
    UpsertFieldDatabaseRequest,
    UpsertFieldDateRequest,
    UpsertFieldDependencyAppRequest,
    UpsertFieldDropdownRequest,
    UpsertFieldEazypayPaymentGatewayRequest,
    UpsertFieldEmailInputRequest,
    UpsertFieldEmojiRequest,
    UpsertFieldFileRequest,
    UpsertFieldFormulaRequest,
    UpsertFieldGpsLocationRequest,
    UpsertFieldImageViewerRequest,
    UpsertFieldLiveTrackingRequest,
    UpsertFieldManualAddressRequest,
    UpsertFieldNfcReaderRequest,
    UpsertFieldNumberInputRequest,
    UpsertFieldPaypalPaymentGatewayRequest,
    UpsertFieldPdfViewerRequest,
    UpsertFieldPhoneNumberRequest,
    UpsertFieldProgressBarRequest,
    UpsertFieldRadioRequest,
    UpsertFieldRazorpayPaymentGatewayRequest,
    UpsertFieldReadOnlyFileRequest,
    UpsertFieldReadOnlyTextRequest,
    UpsertFieldRestApiRequest,
    UpsertFieldRichTextEditorRequest,
    UpsertFieldSignatureRequest,
    UpsertFieldSliderRequest,
    UpsertFieldStripePaymentGatewayRequest,
    UpsertFieldTagsRequest,
    UpsertFieldTextAreaRequest,
    UpsertFieldTextRequest,
    UpsertFieldTimeRequest,
    UpsertFieldToggleRequest,
    UpsertFieldUniqueSequentialRequest,
    UpsertFieldUrlInputRequest,
    UpsertFieldValidationRequest,
    UpsertFieldVideoViewerRequest,
    UpsertFieldVoiceRequest,
    UpsertSectionRequest,
)
from clappia_api_tools.utils import FileUtils

from .base_client import BaseAPIKeyClient, BaseAuthTokenClient, BaseClappiaClient


class ClientResponse(BaseModel):
    success: bool
    data: Any | None = None
    error: str | None = None


FieldRequestUnion = (
    UpsertFieldTextRequest
    | UpsertFieldTextAreaRequest
    | UpsertFieldDependencyAppRequest
    | UpsertFieldRestApiRequest
    | UpsertFieldAddressRequest
    | UpsertFieldDatabaseRequest
    | UpsertFieldDateRequest
    | UpsertFieldAIRequest
    | UpsertFieldCodeRequest
    | UpsertFieldCodeReaderRequest
    | UpsertFieldEmailInputRequest
    | UpsertFieldEmojiRequest
    | UpsertFieldFileRequest
    | UpsertFieldGpsLocationRequest
    | UpsertFieldLiveTrackingRequest
    | UpsertFieldManualAddressRequest
    | UpsertFieldPhoneNumberRequest
    | UpsertFieldProgressBarRequest
    | UpsertFieldSignatureRequest
    | UpsertFieldCounterRequest
    | UpsertFieldSliderRequest
    | UpsertFieldTimeRequest
    | UpsertFieldToggleRequest
    | UpsertFieldValidationRequest
    | UpsertFieldVideoViewerRequest
    | UpsertFieldVoiceRequest
    | UpsertFieldFormulaRequest
    | UpsertFieldImageViewerRequest
    | UpsertFieldRichTextEditorRequest
    | UpsertFieldNfcReaderRequest
    | UpsertFieldNumberInputRequest
    | UpsertFieldPdfViewerRequest
    | UpsertFieldReadOnlyFileRequest
    | UpsertFieldReadOnlyTextRequest
    | UpsertFieldTagsRequest
    | UpsertFieldUniqueSequentialRequest
    | UpsertFieldDropdownRequest
    | UpsertFieldRadioRequest
    | UpsertFieldUrlInputRequest
    | UpsertFieldCheckboxRequest
    | UpsertFieldRazorpayPaymentGatewayRequest
    | UpsertFieldEazypayPaymentGatewayRequest
    | UpsertFieldPaypalPaymentGatewayRequest
    | UpsertFieldStripePaymentGatewayRequest
    | UpsertFieldButtonRequest
)


class AppDefinitionClient(BaseClappiaClient, ABC):
    """Abstract client for managing Clappia app definitions.

    This client handles retrieving and managing app definitions, including
    getting app definitions, creating apps, adding fields, and updating fields.

    Note: This is an abstract base class that contains business logic but no authentication.
    Use AppDefinitionAPIKeyClient or AppDefinitionAuthTokenClient for actual usage.
    """

    def __init__(
        self,
        base_url: str,
        file_management_client: FileManagementClient,
        timeout: int = 30,
    ):
        super().__init__(base_url, timeout)
        self.file_management_client = file_management_client

    async def create_app(
        self,
        name: str,
        requesting_user_email_address: EmailStr,
        pages: list[ExternalPageDefinition],
        description: str | None = None,
    ) -> ClientResponse:
        """Create a new app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/createApp",
            data={
                "name": name,
                "requestingUserEmailAddress": requesting_user_email_address,
                "pages": [page.to_json() for page in pages],
                "description": description,
            },
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def get_definition(
        self, app_id: str, version_variable_name: str | None = None
    ) -> ClientResponse:
        """Retrieve the complete definition for a specific app."""

        params = {"appId": app_id}
        if version_variable_name:
            params["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="GET", endpoint="/getAppDefinition", params=params
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def add_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: FieldRequestUnion,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a field to a Clappia app."""
        if isinstance(request, UpsertFieldTextRequest):
            return await self._add_text_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldTextAreaRequest):
            return await self._add_textarea_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldDependencyAppRequest):
            return await self._add_dependency_app_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldRestApiRequest):
            return await self._add_rest_api_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldAddressRequest):
            return await self._add_address_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldDatabaseRequest):
            return await self._add_database_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldDateRequest):
            return await self._add_date_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldAIRequest):
            return await self._add_ai_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldCodeRequest):
            return await self._add_code_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldCodeReaderRequest):
            return await self._add_code_reader_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldEmailInputRequest):
            return await self._add_email_input_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldEmojiRequest):
            return await self._add_emoji_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldFileRequest):
            return await self._add_file_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldGpsLocationRequest):
            return await self._add_gps_location_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldLiveTrackingRequest):
            return await self._add_live_tracking_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldManualAddressRequest):
            return await self._add_manual_address_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldPhoneNumberRequest):
            return await self._add_phone_number_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldProgressBarRequest):
            return await self._add_progress_bar_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldSignatureRequest):
            return await self._add_signature_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldCounterRequest):
            return await self._add_counter_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldSliderRequest):
            return await self._add_slider_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldTimeRequest):
            return await self._add_time_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldToggleRequest):
            return await self._add_toggle_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldValidationRequest):
            return await self._add_validation_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldVideoViewerRequest):
            return await self._add_video_viewer_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldVoiceRequest):
            return await self._add_voice_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldFormulaRequest):
            return await self._add_formula_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldImageViewerRequest):
            return await self._add_image_viewer_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldRichTextEditorRequest):
            return await self._add_rich_text_editor_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldNfcReaderRequest):
            return await self._add_nfc_reader_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldNumberInputRequest):
            return await self._add_number_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldPdfViewerRequest):
            return await self._add_pdf_viewer_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldReadOnlyFileRequest):
            return await self._add_read_only_file_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldReadOnlyTextRequest):
            return await self._add_read_only_text_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldTagsRequest):
            return await self._add_tag_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldUniqueSequentialRequest):
            return await self._add_unique_sequential_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldDropdownRequest):
            return await self._add_drop_down_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldRadioRequest):
            return await self._add_radio_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldUrlInputRequest):
            return await self._add_url_input_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldCheckboxRequest):
            return await self._add_checkbox_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldRazorpayPaymentGatewayRequest):
            return await self._add_razorpay_payment_gateway_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldEazypayPaymentGatewayRequest):
            return await self._add_eazypay_payment_gateway_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldPaypalPaymentGatewayRequest):
            return await self._add_paypal_payment_gateway_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldStripePaymentGatewayRequest):
            return await self._add_stripe_payment_gateway_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        elif isinstance(request, UpsertFieldButtonRequest):
            return await self._add_button_field(
                app_id,
                section_index,
                field_index,
                page_index,
                field_name,
                request,
                version_variable_name,
            )
        else:
            raise ValueError(f"Unsupported field request type: {type(request)}")

    async def update_field(
        self,
        app_id: str,
        field_name: str,
        request: FieldRequestUnion,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a field in a Clappia app."""
        if isinstance(request, UpsertFieldTextRequest):
            return await self._update_text_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldTextAreaRequest):
            return await self._update_textarea_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldDependencyAppRequest):
            return await self._update_dependency_app_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldRestApiRequest):
            return await self._update_rest_api_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldAddressRequest):
            return await self._update_address_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldDatabaseRequest):
            return await self._update_database_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldDateRequest):
            return await self._update_date_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldAIRequest):
            return await self._update_ai_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldCodeRequest):
            return await self._update_code_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldCodeReaderRequest):
            return await self._update_code_reader_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldEmailInputRequest):
            return await self._update_email_input_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldEmojiRequest):
            return await self._update_emoji_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldFileRequest):
            return await self._update_file_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldGpsLocationRequest):
            return await self._update_gps_location_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldLiveTrackingRequest):
            return await self._update_live_tracking_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldManualAddressRequest):
            return await self._update_manual_address_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldPhoneNumberRequest):
            return await self._update_phone_number_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldProgressBarRequest):
            return await self._update_progress_bar_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldSignatureRequest):
            return await self._update_signature_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldCounterRequest):
            return await self._update_counter_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldSliderRequest):
            return await self._update_slider_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldTimeRequest):
            return await self._update_time_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldToggleRequest):
            return await self._update_toggle_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldValidationRequest):
            return await self._update_validation_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldVideoViewerRequest):
            return await self._update_video_viewer_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldVoiceRequest):
            return await self._update_voice_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldFormulaRequest):
            return await self._update_formula_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldImageViewerRequest):
            return await self._update_image_viewer_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldRichTextEditorRequest):
            return await self._update_rich_text_editor_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldNfcReaderRequest):
            return await self._update_nfc_reader_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldNumberInputRequest):
            return await self._update_number_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldPdfViewerRequest):
            return await self._update_pdf_viewer_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldReadOnlyFileRequest):
            return await self._update_read_only_file_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldReadOnlyTextRequest):
            return await self._update_read_only_text_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldTagsRequest):
            return await self._update_tag_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldUniqueSequentialRequest):
            return await self._update_unique_sequential_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldDropdownRequest):
            return await self._update_drop_down_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldRadioRequest):
            return await self._update_radio_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldUrlInputRequest):
            return await self._update_url_input_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldCheckboxRequest):
            return await self._update_checkbox_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldRazorpayPaymentGatewayRequest):
            return await self._update_razorpay_payment_gateway_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldEazypayPaymentGatewayRequest):
            return await self._update_eazypay_payment_gateway_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldPaypalPaymentGatewayRequest):
            return await self._update_paypal_payment_gateway_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldStripePaymentGatewayRequest):
            return await self._update_stripe_payment_gateway_field(
                app_id, field_name, request, version_variable_name
            )
        elif isinstance(request, UpsertFieldButtonRequest):
            return await self._update_button_field(
                app_id, field_name, request, version_variable_name
            )
        else:
            raise ValueError(f"Unsupported field request type: {type(request)}")

    async def reorder_field(
        self,
        app_id: str,
        source_page_index: int,
        target_page_index: int,
        source_section_index: int,
        target_section_index: int,
        index_in_target_section: int,
        field_name: str,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Reorder a field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sourcePageIndex": source_page_index,
            "targetPageIndex": target_page_index,
            "sourceSectionIndex": source_section_index,
            "targetSectionIndex": target_section_index,
            "indexInTargetSection": index_in_target_section,
            "fieldName": field_name,
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/reorderField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_text_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldTextRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a text field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.SINGLE_LINE_TEXT.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_text_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldTextRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a text field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # TextArea Field Methods
    async def _add_textarea_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldTextAreaRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a textarea field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.MULTI_LINE_TEXT.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_textarea_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldTextAreaRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a textarea field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Dependency App Field Methods
    async def _add_dependency_app_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldDependencyAppRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a dependency app field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.GET_DATA_FROM_OTHER_APPS.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_dependency_app_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldDependencyAppRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a dependency app field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Rest API Field Methods
    async def _add_rest_api_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldRestApiRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a REST API field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.GET_DATA_FROM_REST_APIS.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_rest_api_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldRestApiRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a REST API field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Address Field Methods
    async def _add_address_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldAddressRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an address field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.GEO_ADDRESS.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_address_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldAddressRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an address field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Database Field Methods
    async def _add_database_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldDatabaseRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a database field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.DATABASE.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_database_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldDatabaseRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a database field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Date Field Methods
    async def _add_date_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldDateRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a date field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.DATE_SELECTOR.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_date_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldDateRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a date field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # AI Field Methods
    async def _add_ai_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldAIRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an AI field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.AI.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_ai_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldAIRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an AI field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Code Field Methods
    async def _add_code_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldCodeRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a code field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.CODE.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_code_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldCodeRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a code field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Code Reader Field Methods
    async def _add_code_reader_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldCodeReaderRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a code reader field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.CODE_SCANNER.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_code_reader_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldCodeReaderRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a code reader field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Email Input Field Methods
    async def _add_email_input_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldEmailInputRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an email input field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.EMAIL_INPUT.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_email_input_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldEmailInputRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an email input field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Emoji Field Methods
    async def _add_emoji_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldEmojiRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an emoji field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.RATINGS.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_emoji_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldEmojiRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an emoji field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # File Field Methods
    async def _add_file_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldFileRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a file field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.FILE.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_file_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldFileRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a file field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # GPS Location Field Methods
    async def _add_gps_location_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldGpsLocationRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a GPS location field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.GPS_LOCATION.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_gps_location_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldGpsLocationRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a GPS location field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Live Tracking Field Methods
    async def _add_live_tracking_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldLiveTrackingRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a live tracking field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.LIVE_TRACKING.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_live_tracking_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldLiveTrackingRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a live tracking field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Manual Address Field Methods
    async def _add_manual_address_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldManualAddressRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a manual address field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.ADDRESS.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_manual_address_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldManualAddressRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a manual address field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Phone Number Field Methods
    async def _add_phone_number_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldPhoneNumberRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a phone number field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PHONE_NUMBER.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_phone_number_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldPhoneNumberRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a phone number field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Progress Bar Field Methods
    async def _add_progress_bar_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldProgressBarRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a progress bar field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PROGRESS_BAR.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_progress_bar_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldProgressBarRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a progress bar field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Signature Field Methods
    async def _add_signature_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldSignatureRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a signature field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.SIGNATURE.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_signature_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldSignatureRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a signature field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Counter Field Methods
    async def _add_counter_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldCounterRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a counter field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.COUNTER.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_counter_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldCounterRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a counter field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Slider Field Methods
    async def _add_slider_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldSliderRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a slider field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.SLIDER.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_slider_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldSliderRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a slider field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Time Field Methods
    async def _add_time_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldTimeRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a time field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.TIME_SELECTOR.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_time_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldTimeRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a time field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Toggle Field Methods
    async def _add_toggle_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldToggleRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a toggle field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.TOGGLE.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_toggle_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldToggleRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a toggle field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Validation Field Methods
    async def _add_validation_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldValidationRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a validation field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.VALIDATION.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_validation_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldValidationRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a validation field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Video Viewer Field Methods
    async def _add_video_viewer_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldVideoViewerRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a video viewer field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        file_id, _ = await self.file_management_client.upload_video_viewer_file(
            app_id=app_id,
            file_url=request.public_file_url,
            file_name=request.file_name,
        )
        if not file_id:
            return ClientResponse(success=False, error="Failed to upload file")

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.VIDEO_VIEWER.value,
            "fieldName": field_name,
            "staticAttachment": {
                "fileId": file_id,
            },
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_video_viewer_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldVideoViewerRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a video viewer field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        file_id, _ = await self.file_management_client.upload_video_viewer_file(
            app_id=app_id,
            file_url=request.public_file_url,
            file_name=request.file_name,
        )
        if not file_id:
            return ClientResponse(success=False, error="Failed to upload file")

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            "staticAttachment": {
                "fileId": file_id,
            },
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Voice Field Methods
    async def _add_voice_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldVoiceRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a voice field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.AUDIO.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_voice_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldVoiceRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a voice field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    # Formula Field Methods
    async def _add_formula_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldFormulaRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a formula field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.CALCULATIONS_AND_LOGIC.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_formula_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldFormulaRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a formula field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_image_viewer_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldImageViewerRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an image field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        file_id, _ = await self.file_management_client.upload_image_viewer_file(
            app_id=app_id,
            file_url=request.public_file_url,
            file_name=request.file_name,
        )
        if not file_id:
            return ClientResponse(success=False, error="Failed to upload file")

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.IMAGE_VIEWER.value,
            "fieldName": field_name,
            "staticAttachment": {
                "fileId": file_id,
            },
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_image_viewer_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldImageViewerRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an image field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        file_id, _ = await self.file_management_client.upload_image_viewer_file(
            app_id=app_id,
            file_url=request.public_file_url,
            file_name=request.file_name,
        )
        if not file_id:
            return ClientResponse(success=False, error="Failed to upload file")

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            "staticAttachment": {
                "fileId": file_id,
            },
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_rich_text_editor_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldRichTextEditorRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a rich text editor field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.RICH_TEXT_EDITOR.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_rich_text_editor_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldRichTextEditorRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a rich text editor field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_nfc_reader_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldNfcReaderRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an NFC reader field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.NFC_READER.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_nfc_reader_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldNfcReaderRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an NFC reader field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_number_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldNumberInputRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a number field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.NUMBER_INPUT.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_number_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldNumberInputRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a number field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_pdf_viewer_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldPdfViewerRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a PDF viewer field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        file_id, _ = await self.file_management_client.upload_pdf_viewer_file(
            app_id=app_id,
            file_url=request.public_file_url,
            file_name=request.file_name,
        )
        if not file_id:
            return ClientResponse(success=False, error="Failed to upload file")

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PDF_VIEWER.value,
            "fieldName": field_name,
            "staticAttachment": {
                "fileId": file_id,
            },
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_pdf_viewer_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldPdfViewerRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a PDF viewer field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        file_id, _ = await self.file_management_client.upload_pdf_viewer_file(
            app_id=app_id,
            file_url=request.public_file_url,
            file_name=request.file_name,
        )
        if not file_id:
            return ClientResponse(success=False, error="Failed to upload file")

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            "staticAttachment": {
                "fileId": file_id,
            },
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_read_only_file_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldReadOnlyFileRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a read only field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        file_id, _ = await self.file_management_client.upload_attached_file(
            app_id=app_id,
            file_url=request.public_file_url,
            file_name=request.file_name,
        )
        if not file_id:
            return ClientResponse(success=False, error="Failed to upload file")

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.ATTACHED_FILES.value,
            "fieldName": field_name,
            "staticAttachment": {
                "fileId": file_id,
            },
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_read_only_file_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldReadOnlyFileRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a read only field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        file_id, _ = await self.file_management_client.upload_attached_file(
            app_id=app_id,
            file_url=request.public_file_url,
            file_name=request.file_name,
        )
        if not file_id:
            return ClientResponse(success=False, error="Failed to upload file")

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            "staticAttachment": {
                "fileId": file_id,
            },
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_read_only_text_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldReadOnlyTextRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a read only text field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.HTML.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_read_only_text_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldReadOnlyTextRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a read only text field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_tag_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldTagsRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a tag field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.TAGS.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_tag_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldTagsRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a tag field in an app."""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_unique_sequential_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldUniqueSequentialRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a unique sequential field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.UNIQUE_NUMBERING.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_unique_sequential_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldUniqueSequentialRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a unique sequential field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_drop_down_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldDropdownRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a drop down field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.DROP_DOWN.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_drop_down_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldDropdownRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a drop down field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_radio_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldRadioRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a radio field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.SINGLE_SELECTOR.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_radio_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldRadioRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a radio field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_url_input_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldUrlInputRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a URL input field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.URL_INPUT.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_url_input_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldUrlInputRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a URL input field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_checkbox_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldCheckboxRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a checkbox field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.MULTI_SELECTOR.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_checkbox_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldCheckboxRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a checkbox field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_razorpay_payment_gateway_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldRazorpayPaymentGatewayRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a razorpay payment gateway field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PAYMENT_GATEWAY.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_razorpay_payment_gateway_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldRazorpayPaymentGatewayRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a razorpay payment gateway field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message,
            )

        return ClientResponse(success=True, data=response_data)

    async def _add_eazypay_payment_gateway_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldEazypayPaymentGatewayRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add an eazypay payment gateway field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PAYMENT_GATEWAY.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message,
            )

        return ClientResponse(success=True, data=response_data)

    async def _update_eazypay_payment_gateway_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldEazypayPaymentGatewayRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update an eazypay payment gateway field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_paypal_payment_gateway_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldPaypalPaymentGatewayRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a paypal payment gateway field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PAYMENT_GATEWAY.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _update_paypal_payment_gateway_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldPaypalPaymentGatewayRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a paypal payment gateway field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message,
            )

        return ClientResponse(success=True, data=response_data)

    async def _add_stripe_payment_gateway_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldStripePaymentGatewayRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a stripe payment gateway field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PAYMENT_GATEWAY.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message,
            )

        return ClientResponse(success=True, data=response_data)

    async def _update_stripe_payment_gateway_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldStripePaymentGatewayRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a stripe payment gateway field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def _add_button_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldButtonRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a button field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.BUTTON.value,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addField",
            data=payload,
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message,
            )

        return ClientResponse(success=True, data=response_data)

    async def _update_button_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldButtonRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a button field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateField",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def add_page_break(
        self,
        app_id: str,
        request: AddPageBreakRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a page break to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "pageIndex": request.page_index,
            "sectionIndex": request.section_index,
            "pageMetadata": request.page_metadata.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addPageBreak",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def update_page(
        self,
        app_id: str,
        request: UpdatePageBreakRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update page break settings in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "pageIndex": request.page_index,
            "pageMetadata": request.page_metadata.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updatePageBreak",
            data=payload,
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message,
                data=response_data,
            )

        return ClientResponse(success=True, data=response_data)

    async def reorder_section(
        self,
        app_id: str,
        section_index: int,
        page_index: int,
        source_section_index: int,
        target_section_index: int,
        source_page_index: int,
        target_page_index: int,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Reorder a section within an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "pageIndex": page_index,
            "sourceSectionIndex": source_section_index,
            "targetSectionIndex": target_section_index,
            "sourcePageIndex": source_page_index,
            "targetPageIndex": target_page_index,
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/reorderSection",
            data=payload,
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message,
                data=response_data,
            )

        return ClientResponse(success=True, data=response_data)

    async def add_section(
        self,
        app_id: str,
        page_index: int,
        section_index: int,
        request: UpsertSectionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Add a section to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "pageIndex": page_index,
            "sectionIndex": section_index,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/addSection",
            data=payload,
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message,
                data=response_data,
            )

        return ClientResponse(success=True, data=response_data)

    async def update_section(
        self,
        app_id: str,
        section_index: int,
        page_index: int,
        request: UpsertSectionRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update a section in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "pageIndex": page_index,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateSection",
            data=payload,
        )

        if not success:
            return ClientResponse(
                success=False,
                error=error_message,
                data=response_data,
            )

        return ClientResponse(success=True, data=response_data)

    async def get_app_versions(self, app_id: str) -> ClientResponse:
        """Get an app version."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        params = {
            "appId": app_id,
        }

        success, error_message, response_data = await self.api_utils.make_request(
            method="GET",
            endpoint="/getAppVersions",
            params=params,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def create_new_app_version(
        self, app_id: str, version_name: str
    ) -> ClientResponse:
        """Create a new app version."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "versionName": version_name,
        }

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/createNewAppVersion",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def update_app_version(
        self, app_id: str, initial_version_name: str, new_version_name: str
    ) -> ClientResponse:
        """Update an app version."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "initialVersionName": initial_version_name,
            "newVersionName": new_version_name,
        }

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateAppVersion",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def update_live_version(
        self, app_id: str, version_variable_name: str
    ) -> ClientResponse:
        """Update the live app version."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            "versionVariableName": version_variable_name,
        }

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateLiveVersion",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def update_app_metadata(
        self,
        app_id: str,
        request: UpdateAppMetadataRequest,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        """Update app metadata."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        payload = {
            "appId": app_id,
            **request.to_json(),
        }
        if version_variable_name is not None:
            payload["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/updateAppMetadata",
            data=payload,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def update_app_icon(
        self,
        app_id: str,
        icon_public_url: str,
        file_name: str,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        try:
            if not icon_public_url:
                raise Exception("Icon public URL is required")

            _, public_file_url = await self.file_management_client.upload_app_icon(
                app_id=app_id,
                file_url=icon_public_url,
                file_name=file_name,
            )

            if not public_file_url:
                raise Exception("Failed to upload app icon")

            payload = {
                "appId": app_id,
                "appIconUrl": public_file_url,
            }
            if version_variable_name is not None:
                payload["versionVariableName"] = version_variable_name

            success, error_message, response_data = await self.api_utils.make_request(
                method="POST",
                endpoint="/updateAppMetadata",
                data=payload,
            )

            if not success:
                return ClientResponse(success=False, error=error_message)

            return ClientResponse(success=True, data=response_data)
        except Exception as e:
            return ClientResponse(success=False, error=str(e))

    async def get_print_templates(
        self, app_id: str, version_variable_name: str | None = None
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        params = {
            "appId": app_id,
        }
        if version_variable_name is not None:
            params["versionVariableName"] = version_variable_name

        success, error_message, response_data = await self.api_utils.make_request(
            method="GET",
            endpoint="/getPrintTemplates",
            params=params,
        )

        if not success:
            return ClientResponse(success=False, error=error_message)

        return ClientResponse(success=True, data=response_data)

    async def add_new_print_template(
        self,
        app_id: str,
        definition: ExternalTemplateDefinition,
        body_html_string: str,
        header_html_string: str | None = None,
        footer_html_string: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        try:
            upload_tasks = [
                ("body", body_html_string, "body.html"),
            ]
            if header_html_string is not None:
                upload_tasks.append(("header", header_html_string, "header.html"))
            if footer_html_string is not None:
                upload_tasks.append(("footer", footer_html_string, "footer.html"))

            upload_results = await asyncio.gather(
                *[
                    self.file_management_client.upload_html_file(
                        app_id=app_id,
                        html_content=html_content,
                        file_name=file_name,
                    )
                    for _, html_content, file_name in upload_tasks
                ]
            )

            file_paths = [result[0] for result in upload_results]
            with FileUtils.temporary_files(*file_paths):
                file_ids: dict[str, str] = {}
                for (file_type, _, _), (_, file_id, _) in zip(
                    upload_tasks, upload_results, strict=False
                ):
                    file_ids[file_type] = file_id

                definition_json = definition.to_json()
                template_definition: dict[str, Any] = {
                    **definition_json,
                    "bodyFileId": file_ids["body"],
                }
                payload: dict[str, Any] = {
                    "appId": app_id,
                    "templateDefinition": template_definition,
                }

                if "header" in file_ids:
                    template_definition["headerFileId"] = file_ids["header"]
                if "footer" in file_ids:
                    template_definition["footerFileId"] = file_ids["footer"]

                if version_variable_name is not None:
                    payload["versionVariableName"] = version_variable_name

                (
                    success,
                    error_message,
                    response_data,
                ) = await self.api_utils.make_request(
                    method="POST",
                    endpoint="/addNewPrintTemplate",
                    data=payload,
                )

                if not success:
                    return ClientResponse(success=False, error=error_message)

                return ClientResponse(success=True, data=response_data)

        except Exception as e:
            return ClientResponse(success=False, error=str(e))

    async def update_print_template(
        self,
        app_id: str,
        index: int,
        definition: ExternalTemplateDefinition,
        body_html_string: str | None = None,
        header_html_string: str | None = None,
        footer_html_string: str | None = None,
        version_variable_name: str | None = None,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        try:
            upload_tasks = []
            if body_html_string is not None:
                upload_tasks.append(("body", body_html_string, "body.html"))
            if header_html_string is not None:
                upload_tasks.append(("header", header_html_string, "header.html"))
            if footer_html_string is not None:
                upload_tasks.append(("footer", footer_html_string, "footer.html"))

            upload_results = await asyncio.gather(
                *[
                    self.file_management_client.upload_html_file(
                        app_id=app_id,
                        html_content=html_content,
                        file_name=file_name,
                    )
                    for _, html_content, file_name in upload_tasks
                ]
            )

            file_paths = [result[0] for result in upload_results]
            with FileUtils.temporary_files(*file_paths):
                file_ids: dict[str, str] = {}
                for (file_type, _, _), (_, file_id, _) in zip(
                    upload_tasks, upload_results, strict=False
                ):
                    file_ids[file_type] = file_id

                definition_json = definition.to_json()
                template_definition: dict[str, Any] = {
                    **definition_json,
                }
                payload: dict[str, Any] = {
                    "appId": app_id,
                    "index": index,
                    "templateDefinition": template_definition,
                }

                if "body" in file_ids:
                    template_definition["bodyFileId"] = file_ids["body"]
                if "header" in file_ids:
                    template_definition["headerFileId"] = file_ids["header"]
                if "footer" in file_ids:
                    template_definition["footerFileId"] = file_ids["footer"]

                if version_variable_name is not None:
                    payload["versionVariableName"] = version_variable_name

                (
                    success,
                    error_message,
                    response_data,
                ) = await self.api_utils.make_request(
                    method="POST",
                    endpoint="/updatePrintTemplate",
                    data=payload,
                )

                if not success:
                    return ClientResponse(success=False, error=error_message)

                return ClientResponse(success=True, data=response_data)

        except Exception as e:
            return ClientResponse(success=False, error=str(e))

    async def get_print_template_content(
        self,
        app_id: str,
        body_file_id: str,
        header_file_id: str | None = None,
        footer_file_id: str | None = None,
    ) -> ClientResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ClientResponse(success=False, error=env_error)

        async def fetch_content_from_file_id(file_id: str | None) -> str:
            if not file_id:
                return ""
            url = await self.file_management_client.get_print_template_file_url(app_id, file_id)
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text

        try:
            body_content, header_content, footer_content = await asyncio.gather(
                fetch_content_from_file_id(body_file_id),
                fetch_content_from_file_id(header_file_id),
                fetch_content_from_file_id(footer_file_id),
            )

            return ClientResponse(
                success=True,
                data={
                    "htmlHeaderContent": header_content,
                    "htmlBodyContent": body_content,
                    "htmlFooterContent": footer_content,
                },
            )
        except Exception as e:
            return ClientResponse(success=False, error=str(e))

    async def close(self) -> None:
        """Close the underlying HTTP client and clean up resources."""
        await self.api_utils.close()


class AppDefinitionAPIKeyClient(BaseAPIKeyClient, AppDefinitionClient):
    """Client for managing Clappia app definitions with API key authentication."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        file_management_client: FileManagementClient,
        timeout: int = 30,
    ):
        """Initialize app definition client with API key.

        Args:
            api_key: Clappia API key.
            base_url: API base URL.
            file_management_client: File management client.
            timeout: Request timeout in seconds.
        """
        BaseAPIKeyClient.__init__(self, api_key, base_url, timeout)
        self.file_management_client = file_management_client


class AppDefinitionAuthTokenClient(BaseAuthTokenClient, AppDefinitionClient):
    """Client for managing Clappia app definitions with auth token authentication."""

    def __init__(
        self,
        auth_token: str,
        workplace_id: str,
        base_url: str,
        file_management_client: FileManagementClient,
        timeout: int = 30,
    ):
        """Initialize app definition client with auth token.

        Args:
            auth_token: Clappia Auth token.
            workplace_id: Clappia Workplace ID.
            base_url: API base URL.
            file_management_client: File management client.
            timeout: Request timeout in seconds.
        """
        BaseAuthTokenClient.__init__(self, auth_token, workplace_id, base_url, timeout)
        self.file_management_client = file_management_client
