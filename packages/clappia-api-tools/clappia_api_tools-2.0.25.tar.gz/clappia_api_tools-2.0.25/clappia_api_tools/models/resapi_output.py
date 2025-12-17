from typing import Literal

from pydantic import Field, field_validator

from ..utils import Utils
from .base_model import BaseFieldComponent


class RestApiOutputField(BaseFieldComponent):
    name: str = Field(min_length=1, description="Name of the output field")
    data_type: Literal["textInput", "file", "textArea"] = Field(
        description="Data type of the output field"
    )
    json_path_query: str = Field(description="JSON path query for extracting data")
    x_path_query: str = Field(description="XPath query for extracting data")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str | None:
        return Utils.non_empty_string_validator(v, "Name")
