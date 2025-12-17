from typing import Literal

from pydantic import Field, field_validator

from ..utils import Utils
from .base_model import BaseFieldComponent


class SortField(BaseFieldComponent):
    sort_by: str = Field(min_length=1, description="Field name to sort by")
    sort_direction: Literal["asc", "desc"] = Field(description="Sort direction")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str | None:
        return Utils.non_empty_string_validator(v, "Sort by field name")
