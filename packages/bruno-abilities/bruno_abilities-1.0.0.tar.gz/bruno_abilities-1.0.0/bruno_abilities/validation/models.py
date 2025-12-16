"""
Pydantic models for parameter validation.

This module provides Pydantic models for common parameter types
that can be used in ability implementations.
"""

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StringParameter(BaseModel):
    """String parameter model."""

    value: str = Field(..., description="String value")
    min_length: int | None = Field(default=None, description="Minimum length")
    max_length: int | None = Field(default=None, description="Maximum length")

    @field_validator("value")
    @classmethod
    def validate_length(cls, v: str, info) -> str:
        min_len = info.data.get("min_length")
        max_len = info.data.get("max_length")

        if min_len is not None and len(v) < min_len:
            raise ValueError(f"String must be at least {min_len} characters")

        if max_len is not None and len(v) > max_len:
            raise ValueError(f"String must be at most {max_len} characters")

        return v


class IntegerParameter(BaseModel):
    """Integer parameter model."""

    value: int = Field(..., description="Integer value")
    min_value: int | None = Field(default=None, description="Minimum value")
    max_value: int | None = Field(default=None, description="Maximum value")

    @field_validator("value")
    @classmethod
    def validate_range(cls, v: int, info) -> int:
        min_val = info.data.get("min_value")
        max_val = info.data.get("max_value")

        if min_val is not None and v < min_val:
            raise ValueError(f"Value must be at least {min_val}")

        if max_val is not None and v > max_val:
            raise ValueError(f"Value must be at most {max_val}")

        return v


class FloatParameter(BaseModel):
    """Float parameter model."""

    value: float = Field(..., description="Float value")
    min_value: float | None = Field(default=None, description="Minimum value")
    max_value: float | None = Field(default=None, description="Maximum value")

    @field_validator("value")
    @classmethod
    def validate_range(cls, v: float, info) -> float:
        min_val = info.data.get("min_value")
        max_val = info.data.get("max_value")

        if min_val is not None and v < min_val:
            raise ValueError(f"Value must be at least {min_val}")

        if max_val is not None and v > max_val:
            raise ValueError(f"Value must be at most {max_val}")

        return v


class BooleanParameter(BaseModel):
    """Boolean parameter model."""

    value: bool = Field(..., description="Boolean value")


class DateTimeParameter(BaseModel):
    """DateTime parameter model."""

    value: datetime = Field(..., description="DateTime value")
    allow_past: bool = Field(default=True, description="Allow past dates")
    allow_future: bool = Field(default=True, description="Allow future dates")

    @field_validator("value")
    @classmethod
    def validate_time_constraints(cls, v: datetime, info) -> datetime:
        allow_past = info.data.get("allow_past", True)
        allow_future = info.data.get("allow_future", True)

        now = datetime.now()

        if not allow_past and v < now:
            raise ValueError("Past dates are not allowed")

        if not allow_future and v > now:
            raise ValueError("Future dates are not allowed")

        return v


class DurationParameter(BaseModel):
    """Duration parameter model."""

    value: timedelta = Field(..., description="Duration value")
    min_seconds: float | None = Field(default=None, description="Minimum duration in seconds")
    max_seconds: float | None = Field(default=None, description="Maximum duration in seconds")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("value")
    @classmethod
    def validate_duration_range(cls, v: timedelta, info) -> timedelta:
        min_sec = info.data.get("min_seconds")
        max_sec = info.data.get("max_seconds")

        total_sec = v.total_seconds()

        if min_sec is not None and total_sec < min_sec:
            raise ValueError(f"Duration must be at least {min_sec} seconds")

        if max_sec is not None and total_sec > max_sec:
            raise ValueError(f"Duration must be at most {max_sec} seconds")

        return v


class ArrayParameter(BaseModel):
    """Array parameter model."""

    value: list[Any] = Field(..., description="Array value")
    min_items: int | None = Field(default=None, description="Minimum number of items")
    max_items: int | None = Field(default=None, description="Maximum number of items")

    @field_validator("value")
    @classmethod
    def validate_size(cls, v: list, info) -> list:
        min_items = info.data.get("min_items")
        max_items = info.data.get("max_items")

        if min_items is not None and len(v) < min_items:
            raise ValueError(f"Array must have at least {min_items} items")

        if max_items is not None and len(v) > max_items:
            raise ValueError(f"Array must have at most {max_items} items")

        return v


class ObjectParameter(BaseModel):
    """Object parameter model."""

    value: dict[str, Any] = Field(..., description="Object value")
    required_keys: list[str] | None = Field(default=None, description="Required keys")

    @field_validator("value")
    @classmethod
    def validate_required_keys(cls, v: dict, info) -> dict:
        required = info.data.get("required_keys", [])

        missing_keys = [key for key in required if key not in v]

        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")

        return v
