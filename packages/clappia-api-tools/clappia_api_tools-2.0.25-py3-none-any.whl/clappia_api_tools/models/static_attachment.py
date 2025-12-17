from pydantic import Field

from .base_model import BaseFieldComponent


class StaticAttachment(BaseFieldComponent):
    """Model for static file attachments"""


class Base64StaticAttachment(StaticAttachment):
    base64: str = Field(
        description="Base64 encoded file data. Example: 'data:image/jpeg;base64,/9j/4AAQ...'"
    )
    content_type: str = Field(
        description="MIME type of the file. Example: 'image/jpeg', 'application/pdf'"
    )
    file_name: str = Field(
        description="Name of the file. Example: 'document.pdf', 'image.jpg'"
    )
