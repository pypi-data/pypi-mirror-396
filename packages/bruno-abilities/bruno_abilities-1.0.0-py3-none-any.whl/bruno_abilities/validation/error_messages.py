"""
User-friendly error messages for validation failures.

This module provides utilities for generating helpful error messages
with suggestions for correcting validation errors.
"""

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ErrorMessage:
    """Generates user-friendly error messages."""

    @staticmethod
    def missing_parameter(param_name: str, param_type: str) -> str:
        """
        Generate error message for missing required parameter.

        Args:
            param_name: Name of missing parameter
            param_type: Type of the parameter

        Returns:
            User-friendly error message
        """
        return (
            f"The required parameter '{param_name}' is missing. "
            f"Please provide a {param_type} value for this parameter."
        )

    @staticmethod
    def invalid_type(param_name: str, expected_type: str, actual_type: str, value: Any) -> str:
        """
        Generate error message for type mismatch.

        Args:
            param_name: Name of the parameter
            expected_type: Expected type
            actual_type: Actual type received
            value: The actual value

        Returns:
            User-friendly error message
        """
        return (
            f"The parameter '{param_name}' has an incorrect type. "
            f"Expected {expected_type}, but got {actual_type}. "
            f"Received value: {value}"
        )

    @staticmethod
    def out_of_range(
        param_name: str, value: Any, min_value: Any | None = None, max_value: Any | None = None
    ) -> str:
        """
        Generate error message for out of range value.

        Args:
            param_name: Name of the parameter
            value: The value that's out of range
            min_value: Minimum allowed value
            max_value: Maximum allowed value

        Returns:
            User-friendly error message
        """
        if min_value is not None and max_value is not None:
            return (
                f"The value {value} for parameter '{param_name}' is out of range. "
                f"It must be between {min_value} and {max_value}."
            )
        elif min_value is not None:
            return (
                f"The value {value} for parameter '{param_name}' is too small. "
                f"It must be at least {min_value}."
            )
        elif max_value is not None:
            return (
                f"The value {value} for parameter '{param_name}' is too large. "
                f"It must be at most {max_value}."
            )
        else:
            return f"The value {value} for parameter '{param_name}' is invalid."

    @staticmethod
    def invalid_format(
        param_name: str, value: Any, expected_format: str, examples: list[str] | None = None
    ) -> str:
        """
        Generate error message for invalid format.

        Args:
            param_name: Name of the parameter
            value: The invalid value
            expected_format: Description of expected format
            examples: Optional list of valid examples

        Returns:
            User-friendly error message
        """
        message = (
            f"The parameter '{param_name}' has an invalid format. "
            f"Expected format: {expected_format}. "
            f"Received: {value}"
        )

        if examples:
            examples_str = ", ".join(f"'{ex}'" for ex in examples)
            message += f"\n\nExamples of valid values: {examples_str}"

        return message

    @staticmethod
    def invalid_choice(param_name: str, value: Any, allowed_values: list[Any]) -> str:
        """
        Generate error message for invalid choice.

        Args:
            param_name: Name of the parameter
            value: The invalid value
            allowed_values: List of allowed values

        Returns:
            User-friendly error message
        """
        allowed_str = ", ".join(f"'{v}'" for v in allowed_values)
        return (
            f"The value '{value}' is not valid for parameter '{param_name}'. "
            f"Allowed values are: {allowed_str}"
        )

    @staticmethod
    def constraint_violation(
        param_name: str, constraint_description: str, suggestion: str | None = None
    ) -> str:
        """
        Generate error message for constraint violation.

        Args:
            param_name: Name of the parameter
            constraint_description: Description of the violated constraint
            suggestion: Optional suggestion for fixing

        Returns:
            User-friendly error message
        """
        message = f"The parameter '{param_name}' violates a constraint: {constraint_description}"

        if suggestion:
            message += f"\n\nSuggestion: {suggestion}"

        return message

    @staticmethod
    def aggregate_errors(errors: list[str]) -> str:
        """
        Combine multiple error messages.

        Args:
            errors: List of error messages

        Returns:
            Combined error message
        """
        if len(errors) == 1:
            return errors[0]

        message = f"Found {len(errors)} validation errors:\n\n"
        for i, error in enumerate(errors, 1):
            message += f"{i}. {error}\n"

        return message.strip()
