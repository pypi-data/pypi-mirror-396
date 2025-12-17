"""
Error types for rettxidentity library.

All custom exceptions inherit from IdentityError base class.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .enums import Script


class IdentityError(Exception):
    """Base exception for all rettxidentity library errors."""

    pass


class InvalidDateFormatError(IdentityError):
    """Raised when date_of_birth is not valid ISO 8601 format."""

    def __init__(self, value: str, message: str | None = None):
        self.value = value
        self.message = message or f"Invalid date format: {value}. Expected ISO 8601 (YYYY-MM-DD)"
        super().__init__(self.message)


class MissingRequiredFieldError(IdentityError):
    """Raised when a required field is missing."""

    def __init__(self, field_name: str, message: str | None = None):
        self.field_name = field_name
        self.message = message or f"Missing required field: {field_name}"
        super().__init__(self.message)


class UnsupportedScriptError(IdentityError):
    """Raised when script cannot be handled (informational, not fatal)."""

    def __init__(self, text: str, detected: "Script") -> None:
        self.text = text
        self.detected = detected
        self.message = f"Unsupported script: {detected.value}"
        super().__init__(self.message)


# Backward compatibility aliases
InvalidDateFormat = InvalidDateFormatError
MissingRequiredField = MissingRequiredFieldError
UnsupportedScript = UnsupportedScriptError
