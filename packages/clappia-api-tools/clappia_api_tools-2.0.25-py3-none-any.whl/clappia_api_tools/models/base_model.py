from pydantic import BaseModel, ConfigDict

from .json_serialized import JsonSerializableMixin


class BaseFieldComponent(BaseModel, JsonSerializableMixin):
    """Base component for field-related models"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
