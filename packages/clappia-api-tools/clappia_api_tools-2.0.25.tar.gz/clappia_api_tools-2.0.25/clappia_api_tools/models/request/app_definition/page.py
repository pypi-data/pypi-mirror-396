from pydantic import Field

from ...base_model import BaseFieldComponent
from ...definition import PageMetadata


class AddPageBreakRequest(BaseFieldComponent):
    page_index: int = Field(ge=0, description="Page index where to add page break")
    section_index: int = Field(
        ge=0, description="Section index where to add page break"
    )
    page_metadata: PageMetadata = Field(
        default=PageMetadata(), description="Page metadata"
    )


class UpdatePageBreakRequest(BaseFieldComponent):
    page_index: int = Field(ge=0, description="Page index to update")
    page_metadata: PageMetadata = Field(
        default=PageMetadata(), description="Page metadata"
    )
