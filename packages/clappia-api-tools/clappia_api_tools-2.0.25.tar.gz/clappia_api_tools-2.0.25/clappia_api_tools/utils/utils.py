import json
import re
from urllib.parse import urlparse

import phonenumbers
from phonenumbers import (
    NumberParseException,
    PhoneNumberFormat,
    format_number,
    is_valid_number,
)


class Utils:
    def __init__(self) -> None:
        pass

    def validate_phone_number(
        self, phone: str, default_region: str = "IN"
    ) -> str | None:
        """
        Validate and format a phone number.

        :param phone: Phone number string input
        :param default_region: Default region code (e.g., 'IN', 'US')
        :return: E.164 formatted number if valid, None otherwise
        """
        try:
            parsed = phonenumbers.parse(phone, default_region)
            if is_valid_number(parsed):
                # Return in E.164 format: +[country code][number]
                return format_number(parsed, PhoneNumberFormat.E164)
            return None
        except NumberParseException:
            return None

    @staticmethod
    def field_name_validator(v: str | None) -> str | None:
        """Validate field name format: must start with letter/underscore and contain only lowercase letters, numbers, underscore."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Field name cannot be empty")
            v = v.strip()
            if not re.match(r"^[_a-z][\d_a-z]*$", v):
                raise ValueError(
                    "Field name must start with letter/underscore and contain only lowercase letters, numbers, underscore"
                )
        return v

    @staticmethod
    def non_empty_string_validator(
        v: str | None, field_name: str = "Field"
    ) -> str | None:
        """Validate that a string is not empty when provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError(f"{field_name} cannot be empty")
        return v.strip() if v else v

    @staticmethod
    def url_validator(v: str) -> str:
        """Validate that a string is a valid URL."""
        if not v or not v.strip():
            raise ValueError("URL is required")
        v = v.strip()
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Must be a valid URL")
        except Exception as err:
            raise ValueError("Must be a valid URL") from err
        return v

    @staticmethod
    def json_string_validator(v: str | None) -> str | None:
        """Validate that a string is valid JSON when provided."""
        if v is not None:
            try:
                json.loads(v)
            except json.JSONDecodeError as err:
                raise ValueError("Must be valid JSON string") from err
        return v

    @staticmethod
    def number_validator(v: int | None, field_name: str = "Field") -> int | None:
        """Validate number field. Note: Current implementation may need review."""
        if v is not None:
            raise ValueError(f"{field_name} cannot be empty")
        return v

    @staticmethod
    def validate_unique_strings(
        v: list[str] | None, field_name: str = "Items"
    ) -> list[str] | None:
        """Validate that all strings in a list are unique and non-empty."""
        if v is not None:
            if len(set(v)) != len(v):
                raise ValueError(f"{field_name} must be unique")
            for item in v:
                if not item or not item.strip():
                    raise ValueError(f"{field_name} cannot contain empty values")
        return v

    @staticmethod
    def validate_country_code(v: str | None) -> str | None:
        """Validate that a country code is a 2-letter uppercase code."""
        if v is not None:
            if not v.strip():
                raise ValueError("Country code cannot be empty")
            if not re.match(r"^[A-Z]{2}$", v.strip()):
                raise ValueError("Country code must be a 2-letter uppercase code")
        return v.strip() if v else v

    @staticmethod
    def validate_countries_list(v: list[str] | None) -> list[str] | None:
        """Validate that a list contains unique, valid 2-letter uppercase country codes."""
        if v is not None:
            if len(set(v)) != len(v):
                raise ValueError("Countries list must contain unique country codes")
            for country_code in v:
                if not country_code or not country_code.strip():
                    raise ValueError("Country codes cannot be empty")
                if not re.match(r"^[A-Z]{2}$", country_code.strip()):
                    raise ValueError("Country codes must be 2-letter uppercase codes")
        return v

    @staticmethod
    def validate_database_port(v: str) -> str:
        """Validate that a string is a valid database port number (1-65535)."""
        if not v.isdigit() or not (1 <= int(v) <= 65535):
            raise ValueError(
                "Database port must be a valid port number between 1 and 65535"
            )
        return v

    @staticmethod
    def validate_database_host(v: str) -> str:
        """Validate that a string is a valid database hostname or IP address."""
        if not re.match(r"^[a-zA-Z0-9.-]+$", v):
            raise ValueError("Database host must be a valid hostname or IP address")
        return v

    @staticmethod
    def validate_non_empty_list(
        v: list | None, field_name: str = "List"
    ) -> list | None:
        """Validate that a list is not empty when provided."""
        if v is not None and (not v or len(v) == 0):
            raise ValueError(f"{field_name} must contain at least one item")
        return v

    @staticmethod
    def validate_exact_count(
        v: list | None, count: int, field_name: str = "List"
    ) -> list | None:
        """Validate that a list has exactly the specified count."""
        if v is not None:
            if not v or len(v) != count:
                raise ValueError(f"{field_name} must contain exactly {count} item(s)")
        return v

    @staticmethod
    def validate_max_count(
        v: list | None, max_count: int, field_name: str = "List"
    ) -> list | None:
        """Validate that a list does not exceed the maximum count."""
        if v is not None and len(v) > max_count:
            raise ValueError(f"{field_name} cannot exceed {max_count} item(s)")
        return v

    @staticmethod
    def validate_boolean(v: bool | None, field_name: str = "Field") -> bool | None:
        """Validate that a value is a boolean when provided."""
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"{field_name} should be a boolean if provided")
        return v

    @staticmethod
    def validate_email_or_field_reference(v: str, field_name: str = "Field") -> str:
        """Validate that a value is either a valid email address or a field reference."""
        email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

        trimmed = v.strip()
        is_valid_email = email_regex.match(trimmed)
        is_valid_field = field_name_regex.match(trimmed)

        if not (is_valid_email or is_valid_field):
            raise ValueError(
                f"{field_name} '{v}' must be a valid email address or field reference. "
                f"Example: 'user@example.com' or '{{fieldName}}'"
            )

        return trimmed

    @staticmethod
    def validate_email_or_field_reference_list(
        v: list[str], field_name: str = "Field"
    ) -> list[str]:
        """Validate that all items in a list are either valid email addresses or field references."""
        for item in v:
            Utils.validate_email_or_field_reference(item, field_name)
        return v

    @staticmethod
    def validate_phone_or_field_reference(v: str, field_name: str = "Field") -> str:
        """Validate that a value is either a valid phone number (E.164) or a field reference."""
        phone_regex = re.compile(r"^\+?[1-9]\d{1,14}$")  # E.164 format
        field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

        trimmed = v.strip()
        is_valid_phone = phone_regex.match(trimmed)
        is_valid_field = field_name_regex.match(trimmed)

        if not (is_valid_phone or is_valid_field):
            raise ValueError(
                f"{field_name} '{v}' must be a valid phone number or field reference. "
                f"Example: '+911234567890' or '{{phoneField}}'"
            )

        return trimmed

    @staticmethod
    def validate_phone_or_field_reference_list(
        v: list[str], field_name: str = "Field"
    ) -> list[str]:
        """Validate that all items in a list are either valid phone numbers or field references."""
        for item in v:
            Utils.validate_phone_or_field_reference(item, field_name)
        return v

    @staticmethod
    def validate_email_phone_or_field_reference(
        v: str, field_name: str = "Field"
    ) -> str:
        """Validate that a value is either a valid email, phone number, or field reference."""
        email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        phone_regex = re.compile(r"^\+?[1-9]\d{1,14}$")  # E.164 format
        field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

        trimmed = v.strip()
        is_valid_email = email_regex.match(trimmed)
        is_valid_phone = phone_regex.match(trimmed)
        is_valid_field = field_name_regex.match(trimmed)

        if not (is_valid_email or is_valid_phone or is_valid_field):
            raise ValueError(
                f"{field_name} '{v}' must be a valid email address, phone number, or field reference. "
                f"Example: 'user@example.com', '+911234567890', or '{{fieldName}}'"
            )

        return trimmed

    @staticmethod
    def validate_email_phone_or_field_reference_list(
        v: list[str], field_name: str = "Field"
    ) -> list[str]:
        """Validate that all items in a list are either valid emails, phone numbers, or field references."""
        for item in v:
            Utils.validate_email_phone_or_field_reference(item, field_name)
        return v

    @staticmethod
    def validate_field_reference(v: str, field_name: str = "Field") -> str:
        """Validate that a value is a valid field reference."""
        field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")
        trimmed = v.strip()

        if not field_name_regex.match(trimmed):
            raise ValueError(
                f"{field_name} '{v}' must be a valid field reference. "
                f"Example: '{{fieldName}}'"
            )

        return trimmed

    @staticmethod
    def validate_unique_list(v: list | None, field_name: str = "List") -> list | None:
        """Validate that all items in a list are unique."""
        if v is not None:
            if len(set(v)) != len(v):
                raise ValueError(f"{field_name} must contain unique items")
        return v
