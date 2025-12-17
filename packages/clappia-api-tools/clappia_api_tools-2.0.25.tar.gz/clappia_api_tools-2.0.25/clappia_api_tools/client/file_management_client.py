from abc import ABC
from pathlib import Path

import httpx

from clappia_api_tools.client.base_client import (
    BaseAPIKeyClient,
    BaseAuthTokenClient,
    BaseClappiaClient,
)
from clappia_api_tools.utils import FileUtils


class FileManagementClient(BaseClappiaClient, ABC):
    """Client for managing Clappia file management."""

    async def upload_file_via_bytes(
        self,
        app_id: str,
        file_bytes: bytes,
        file_name: str,
        mime_type: str,
        upload_category: str,
    ) -> tuple[str, str]:
        payload: dict[str, str] = {
            "appId": app_id,
            "fileName": file_name,
            "mimeType": mime_type,
            "uploadCategory": upload_category,
        }

        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/generateFileUploadUrl",
            data=payload,
        )

        if not success:
            raise Exception(error_message)

        if response_data is None or not isinstance(response_data, dict):
            raise Exception("Invalid response data from API")

        file_upload_url = response_data["fileUploadUrl"]
        file_id = response_data["fileId"]
        public_file_url = response_data.get("publicFileUrl")

        if not file_upload_url or not file_id:
            raise Exception(f"Failed to generate {file_name} file upload URL")

        async with httpx.AsyncClient() as client:
            response = await client.put(
                file_upload_url, 
                content=file_bytes,
                headers={"Content-Type": mime_type}
            )
            if response.status_code != 200:
                raise Exception(f"Failed to upload {file_name} file")

        return file_id, public_file_url

    async def upload_app_icon(
        self,
        app_id: str,
        file_url: str,
        file_name: str,
        upload_category: str = "appIcon",
    ) -> tuple[str, str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)
            if response.status_code != 200:
                raise Exception(
                    f"Failed to download file from URL: {response.status_code}"
                )

            file_bytes = response.content
            content_type: str | None = response.headers.get("Content-Type")
            if not content_type:
                raise Exception("Content type not found in response headers")

            if not content_type.startswith("image/"):
                raise Exception(f"Content type is not an image: {content_type}")

        file_id, public_file_url = await self.upload_file_via_bytes(
            app_id=app_id,
            file_bytes=file_bytes,
            file_name=file_name,
            mime_type=content_type,
            upload_category=upload_category,
        )

        return file_id, public_file_url

    async def upload_html_file(
        self,
        app_id: str,
        html_content: str,
        file_name: str,
        upload_category: str = "printTemplateHtml",
    ) -> tuple[Path, str, str]:
        file_path, detected_mime_type = FileUtils.save_text_file(
            text_content=html_content, file_name=file_name, mime_type="text/html"
        )

        file_id, public_file_url = await self.upload_file_via_bytes(
            app_id=app_id,
            file_bytes=file_path.read_bytes(),
            file_name=file_name,
            mime_type=detected_mime_type,
            upload_category=upload_category,
        )

        return file_path, file_id, public_file_url

    async def upload_attached_file(
        self,
        app_id: str,
        file_url: str,
        file_name: str,
        upload_category: str = "attachedFile",
    ) -> tuple[str, str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)
            if response.status_code != 200:
                raise Exception(
                    f"Failed to download file from URL: {response.status_code}"
                )

            file_bytes = response.content
            content_type = response.headers.get(
                "Content-Type", "application/octet-stream"
            )

        file_id, public_file_url = await self.upload_file_via_bytes(
            app_id=app_id,
            file_bytes=file_bytes,
            file_name=file_name,
            mime_type=content_type,
            upload_category=upload_category,
        )

        return file_id, public_file_url

    async def upload_video_viewer_file(
        self,
        app_id: str,
        file_url: str,
        file_name: str,
        upload_category: str = "videoAttachedFile",
    ) -> tuple[str, str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)
            if response.status_code != 200:
                raise Exception(
                    f"Failed to download file from URL: {response.status_code}"
                )

            file_bytes = response.content
            content_type: str | None = response.headers.get("Content-Type")
            if not content_type:
                raise Exception("Content type not found in response headers")
            if not content_type.startswith("video/"):
                raise Exception(f"Content type is not a video: {content_type}")

        file_id, public_file_url = await self.upload_file_via_bytes(
            app_id=app_id,
            file_bytes=file_bytes,
            file_name=file_name,
            mime_type=content_type,
            upload_category=upload_category,
        )

        return file_id, public_file_url

    async def upload_pdf_viewer_file(
        self,
        app_id: str,
        file_url: str,
        file_name: str,
        upload_category: str = "pdfAttachedFile",
    ) -> tuple[str, str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)
            if response.status_code != 200:
                raise Exception(
                    f"Failed to download file from URL: {response.status_code}"
                )

            file_bytes = response.content
            content_type: str | None = response.headers.get("Content-Type")
            if not content_type:
                raise Exception("Content type not found in response headers")
            if not content_type.startswith("application/pdf"):
                raise Exception(f"Content type is not a PDF: {content_type}")

        file_id, public_file_url = await self.upload_file_via_bytes(
            app_id=app_id,
            file_bytes=file_bytes,
            file_name=file_name,
            mime_type=content_type,
            upload_category=upload_category,
        )

        return file_id, public_file_url

    async def upload_image_viewer_file(
        self,
        app_id: str,
        file_url: str,
        file_name: str,
        upload_category: str = "imageAttachedFile",
    ) -> tuple[str, str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)
            if response.status_code != 200:
                raise Exception(
                    f"Failed to download file from URL: {response.status_code}"
                )

            file_bytes = response.content
            content_type: str | None = response.headers.get("Content-Type")
            if not content_type:
                raise Exception("Content type not found in response headers")

            if not content_type.startswith("image/"):
                raise Exception(f"Content type is not an image: {content_type}")

        file_id, public_file_url = await self.upload_file_via_bytes(
            app_id=app_id,
            file_bytes=file_bytes,
            file_name=file_name,
            mime_type=content_type,
            upload_category=upload_category,
        )

        return file_id, public_file_url

    async def download_file_via_file_id(
        self, app_id: str, file_id: str, upload_category: str
    ) -> str:
        payload: dict[str, str] = {
            "appId": app_id,
            "fileId": file_id,
            "uploadCategory": upload_category,
        }
        success, error_message, response_data = await self.api_utils.make_request(
            method="POST",
            endpoint="/generateFileDownloadUrl",
            data=payload,
        )
        if not success:
            raise Exception(error_message)

        if response_data is None or not isinstance(response_data, dict):
            raise Exception("Invalid response data from API")
        url: str = response_data["url"]
        return url

    async def get_app_icon__file_url(self, app_id: str, file_id: str) -> str:
        return await self.download_file_via_file_id(app_id, file_id, "appIcon")

    async def get_print_template_file_url(self, app_id: str, file_id: str) -> str:
        return await self.download_file_via_file_id(
            app_id, file_id, "printTemplateHtml"
        )

    async def get_attached_file_file_url(self, app_id: str, file_id: str) -> str:
        return await self.download_file_via_file_id(app_id, file_id, "attachedFile")

    async def get_video_viewer_file_url(self, app_id: str, file_id: str) -> str:
        return await self.download_file_via_file_id(
            app_id, file_id, "videoAttachedFile"
        )

    async def get_pdf_viewer_file_url(self, app_id: str, file_id: str) -> str:
        return await self.download_file_via_file_id(app_id, file_id, "pdfAttachedFile")

    async def get_image_viewer_file_url(self, app_id: str, file_id: str) -> str:
        return await self.download_file_via_file_id(
            app_id, file_id, "imageAttachedFile"
        )

    async def close(self) -> None:
        await self.api_utils.close()


class FileManagementAPIKeyClient(BaseAPIKeyClient, FileManagementClient):
    """Client for managing Clappia file management with API key authentication."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize file management client with API key.

        Args:
            api_key: Clappia API key.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAPIKeyClient.__init__(self, api_key, base_url, timeout)


class FileManagementAuthTokenClient(BaseAuthTokenClient, FileManagementClient):
    def __init__(
        self,
        auth_token: str,
        workplace_id: str,
        base_url: str,
        timeout: int = 30,
    ):
        """Initialize file management client with auth token.

        Args:
            auth_token: Clappia Auth token.
            workplace_id: Clappia Workplace ID.
            base_url: API base URL.
            timeout: Request timeout in seconds.
        """
        BaseAuthTokenClient.__init__(self, auth_token, workplace_id, base_url, timeout)
