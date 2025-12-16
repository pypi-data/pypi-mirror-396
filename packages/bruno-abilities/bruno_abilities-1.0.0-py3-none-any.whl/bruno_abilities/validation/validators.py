"""
Validators for ability parameters.

This module provides validation functions for common parameter types
with user-friendly error messages.
"""

import re
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlparse

import structlog

logger = structlog.get_logger(__name__)


class ValidationError(Exception):
    """Exception raised when parameter validation fails."""

    def __init__(self, message: str, parameter: str | None = None, value: Any = None):
        self.message = message
        self.parameter = parameter
        self.value = value
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.parameter:
            return f"Validation error for '{self.parameter}': {self.message}"
        return f"Validation error: {self.message}"


def validate_string(
    value: Any,
    min_length: int | None = None,
    max_length: int | None = None,
    pattern: str | None = None,
    allowed_values: list | None = None,
) -> str:
    """
    Validate string parameter.

    Args:
        value: Value to validate
        min_length: Minimum string length
        max_length: Maximum string length
        pattern: Regex pattern to match
        allowed_values: List of allowed values

    Returns:
        Validated string

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"Expected string, got {type(value).__name__}")

    if min_length is not None and len(value) < min_length:
        raise ValidationError(
            f"String must be at least {min_length} characters long, got {len(value)}"
        )

    if max_length is not None and len(value) > max_length:
        raise ValidationError(
            f"String must be at most {max_length} characters long, got {len(value)}"
        )

    if pattern is not None and not re.match(pattern, value):
        raise ValidationError(f"String does not match required pattern: {pattern}")

    if allowed_values is not None and value not in allowed_values:
        raise ValidationError(f"Value must be one of {allowed_values}, got '{value}'")

    return value


def validate_integer(
    value: Any,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """
    Validate integer parameter.

    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Validated integer

    Raises:
        ValidationError: If validation fails
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"Cannot convert to integer: {value}") from None

    if min_value is not None and int_value < min_value:
        raise ValidationError(f"Value must be at least {min_value}, got {int_value}")

    if max_value is not None and int_value > max_value:
        raise ValidationError(f"Value must be at most {max_value}, got {int_value}")

    return int_value


def validate_float(
    value: Any,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float:
    """
    Validate float parameter.

    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Validated float

    Raises:
        ValidationError: If validation fails
    """
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"Cannot convert to float: {value}") from None

    if min_value is not None and float_value < min_value:
        raise ValidationError(f"Value must be at least {min_value}, got {float_value}")

    if max_value is not None and float_value > max_value:
        raise ValidationError(f"Value must be at most {max_value}, got {float_value}")

    return float_value


def validate_boolean(value: Any) -> bool:
    """
    Validate boolean parameter.

    Args:
        value: Value to validate

    Returns:
        Validated boolean

    Raises:
        ValidationError: If validation fails
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        lower_value = value.lower()
        if lower_value in ("true", "yes", "1", "on"):
            return True
        if lower_value in ("false", "no", "0", "off"):
            return False

    if isinstance(value, (int, float)):
        return bool(value)

    raise ValidationError(f"Cannot convert to boolean: {value}")


def validate_datetime(value: Any, allow_past: bool = True, allow_future: bool = True) -> datetime:
    """
    Validate datetime parameter.

    Args:
        value: Value to validate (datetime object or ISO string)
        allow_past: Whether past dates are allowed
        allow_future: Whether future dates are allowed

    Returns:
        Validated datetime

    Raises:
        ValidationError: If validation fails
    """
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            raise ValidationError(f"Invalid datetime format: {value}. Use ISO format.") from None
    else:
        raise ValidationError(f"Cannot convert to datetime: {value}")

    now = datetime.now()

    if not allow_past and dt < now:
        raise ValidationError("Past dates are not allowed")

    if not allow_future and dt > now:
        raise ValidationError("Future dates are not allowed")

    return dt


def validate_duration(
    value: Any, min_seconds: float | None = None, max_seconds: float | None = None
) -> timedelta:
    """
    Validate duration parameter.

    Args:
        value: Value to validate (timedelta or seconds)
        min_seconds: Minimum duration in seconds
        max_seconds: Maximum duration in seconds

    Returns:
        Validated timedelta

    Raises:
        ValidationError: If validation fails
    """
    if isinstance(value, timedelta):
        duration = value
    elif isinstance(value, (int, float)):
        duration = timedelta(seconds=value)
    else:
        raise ValidationError(f"Cannot convert to duration: {value}")

    total_seconds = duration.total_seconds()

    if min_seconds is not None and total_seconds < min_seconds:
        raise ValidationError(
            f"Duration must be at least {min_seconds} seconds, got {total_seconds}"
        )

    if max_seconds is not None and total_seconds > max_seconds:
        raise ValidationError(
            f"Duration must be at most {max_seconds} seconds, got {total_seconds}"
        )

    return duration


def validate_email(value: Any) -> str:
    """
    Validate email parameter.

    Args:
        value: Value to validate

    Returns:
        Validated email string

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"Email must be a string, got {type(value).__name__}")

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, value):
        raise ValidationError(f"Invalid email format: {value}")

    return value


def validate_url(value: Any, allowed_schemes: list | None = None) -> str:
    """
    Validate URL parameter.

    Args:
        value: Value to validate
        allowed_schemes: List of allowed URL schemes (e.g., ['http', 'https'])

    Returns:
        Validated URL string

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"URL must be a string, got {type(value).__name__}")

    try:
        parsed = urlparse(value)
    except Exception as e:
        raise ValidationError(f"Invalid URL: {value} ({str(e)})") from e

    if not parsed.scheme or not parsed.netloc:
        raise ValidationError(f"Invalid URL format: {value}")

    if allowed_schemes and parsed.scheme not in allowed_schemes:
        raise ValidationError(f"URL scheme must be one of {allowed_schemes}, got '{parsed.scheme}'")

    return value


def validate_range(value: Any, min_value: Any, max_value: Any) -> Any:
    """
    Validate that value is within a range.

    Args:
        value: Value to validate
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Returns:
        Validated value

    Raises:
        ValidationError: If validation fails
    """
    if not (min_value <= value <= max_value):
        raise ValidationError(f"Value must be between {min_value} and {max_value}, got {value}")

    return value


def validate_pattern(value: str, pattern: str, flags: int = 0) -> str:
    """
    Validate string against a regex pattern.

    Args:
        value: Value to validate
        pattern: Regex pattern to match
        flags: Regex flags

    Returns:
        Validated string

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"Value must be a string, got {type(value).__name__}")

    if not re.match(pattern, value, flags):
        raise ValidationError(f"Value does not match pattern: {pattern}")

    return value
