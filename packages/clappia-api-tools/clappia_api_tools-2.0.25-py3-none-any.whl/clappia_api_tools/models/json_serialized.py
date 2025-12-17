from datetime import date, datetime
from enum import Enum
from typing import Any


class JsonSerializableMixin:
    """Mixin to provide robust JSON serialization functionality."""

    def to_json(self) -> dict[str, Any]:
        """Convert the object to a JSON-serializable dictionary."""

        def _serialize(value: Any) -> Any:
            if hasattr(value, "to_json"):
                return value.to_json()
            elif isinstance(value, dict):
                return {k: _serialize(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_serialize(v) for v in value]
            elif isinstance(value, tuple) or isinstance(value, set):
                return [_serialize(v) for v in value]
            elif isinstance(value, Enum):
                return value.value
            elif isinstance(value, (datetime, date)):
                return value.isoformat()
            else:
                return value

        data = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                camel_case_key = self._to_camel_case(field_name)
                data[camel_case_key] = _serialize(field_value)

        return data

    @staticmethod
    def _to_camel_case(snake_str: str) -> str:
        components = snake_str.split("_")
        return components[0] + "".join(word.capitalize() for word in components[1:])
